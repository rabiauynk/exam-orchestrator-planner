from datetime import date, datetime, time, timedelta

from database import db
from models import Exam, ExamSchedule, Room, Settings
from sqlalchemy import func


class AdvancedSchedulerService:
    """Advanced scheduler with comprehensive constraint checking"""
    
    def __init__(self):
        # Define working hours
        self.working_hours_start = time(9, 0)  # 09:00 AM
        self.working_hours_end = time(17, 0)   # 05:00 PM
        
        # Lunch break
        self.lunch_break_start = time(12, 15)
        self.lunch_break_end = time(13, 0)
        
        # Friday prayer time
        self.friday_prayer_start = time(12, 0)
        self.friday_prayer_end = time(13, 30)

        # Time slot generation parameters for flexible scheduling
        self.time_slot_interval = 15  # Generate time slots every 15 minutes

    def _generate_possible_start_times(self, target_date, exam_duration):
        """Generate all possible start times for an exam on a given date"""
        possible_times = []

        # Start from working hours start
        current_time = self.working_hours_start

        while current_time < self.working_hours_end:
            # Calculate end time for this start time
            end_time = (datetime.combine(target_date, current_time) +
                       timedelta(minutes=exam_duration)).time()

            # Check if exam would end within working hours
            if end_time <= self.working_hours_end:
                # Check basic time slot rules (lunch break, prayer time)
                if self._check_time_slot_rules(target_date, current_time, end_time):
                    possible_times.append(current_time)

            # Move to next time slot (15 minute intervals)
            current_time = (datetime.combine(target_date, current_time) +
                           timedelta(minutes=self.time_slot_interval)).time()

        return possible_times
    
    def _check_time_slot_rules(self, target_date, start_time, end_time):
        """Check time slot constraints"""
        # Check if exam is within working hours
        if start_time < self.working_hours_start or end_time > self.working_hours_end:
            return False
        
        # Rule 1: No exams during lunch break
        if (start_time < self.lunch_break_end and end_time > self.lunch_break_start):
            return False
        
        # Rule 2: Friday prayer time restriction
        if target_date.weekday() == 4:  # Friday
            if (start_time < self.friday_prayer_end and end_time > self.friday_prayer_start):
                return False
        
        return True
    
    def _check_difficulty_level_rules(self, exam, target_date, daily_schedules):
        """Check difficulty level constraints based on new difficulty system"""
        # Get existing schedules for the day
        date_key = target_date.strftime('%Y-%m-%d')
        if date_key not in daily_schedules:
            return True

        # Rules based on difficulty level:
        # 1. Only one very_hard exam per day
        # 2. Maximum two hard exams per day
        # 3. No more than three normal exams per day
        # 4. Easy exams have no daily limit

        difficulty_counts = {
            'very_hard': 0,
            'hard': 0,
            'normal': 0,
            'easy': 0
        }

        # Count existing exams by difficulty
        for scheduled_exam in daily_schedules[date_key]:
            difficulty = getattr(scheduled_exam, 'difficulty_level', 'normal')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        # Check constraints for the new exam
        exam_difficulty = getattr(exam, 'difficulty_level', 'normal')

        if exam_difficulty == 'very_hard':
            return difficulty_counts['very_hard'] == 0
        elif exam_difficulty == 'hard':
            return difficulty_counts['hard'] < 2 and difficulty_counts['very_hard'] == 0
        elif exam_difficulty == 'normal':
            return (difficulty_counts['normal'] < 3 and
                   difficulty_counts['hard'] == 0 and
                   difficulty_counts['very_hard'] == 0)
        else:  # easy
            return True  # No restrictions for easy exams
    
    def _check_class_level_conflicts(self, exam, target_date, start_time, end_time, daily_schedules):
        """Check class level conflict constraints"""
        date_key = target_date.strftime('%Y-%m-%d')
        if date_key not in daily_schedules:
            return True
        
        # Check for same class level conflicts in the same time slot
        for scheduled_exam in daily_schedules[date_key]:
            if scheduled_exam.class_name == exam.class_name:
                # Get the scheduled time for this exam
                schedule = scheduled_exam.exam_schedules[0] if scheduled_exam.exam_schedules else None
                if schedule:
                    # Check time overlap
                    if self._times_overlap(start_time, end_time, schedule.start_time, schedule.end_time):
                        return False
        
        return True
    
    def _check_time_gap_requirement(self, target_date, start_time, end_time, daily_schedules):
        """Check 15-minute gap requirement between exams"""
        date_key = target_date.strftime('%Y-%m-%d')
        if date_key not in daily_schedules:
            return True
        
        # Check gap with existing exams
        for scheduled_exam in daily_schedules[date_key]:
            schedule = scheduled_exam.exam_schedules[0] if scheduled_exam.exam_schedules else None
            if schedule:
                # Check if there's at least 15 minutes gap
                if not self._has_sufficient_gap(start_time, end_time, schedule.start_time, schedule.end_time):
                    return False
        
        return True
    
    def _times_overlap(self, start1, end1, start2, end2):
        """Check if two time ranges overlap"""
        return start1 < end2 and start2 < end1
    
    def _has_sufficient_gap(self, start1, end1, start2, end2):
        """Check if there's at least 15 minutes gap between time slots"""
        gap_minutes = 15
        
        # Convert times to minutes for easier calculation
        start1_minutes = start1.hour * 60 + start1.minute
        end1_minutes = end1.hour * 60 + end1.minute
        start2_minutes = start2.hour * 60 + start2.minute
        end2_minutes = end2.hour * 60 + end2.minute
        
        # Check gap in both directions
        if end1_minutes <= start2_minutes:
            return (start2_minutes - end1_minutes) >= gap_minutes
        elif end2_minutes <= start1_minutes:
            return (start1_minutes - end2_minutes) >= gap_minutes
        else:
            # Times overlap, no gap
            return False
    
    def _find_suitable_rooms(self, exam, target_date, start_time, end_time):
        """Find suitable rooms for the exam with capacity splitting if needed"""
        # Get available rooms from exam's available_rooms list
        available_room_names = getattr(exam, 'available_rooms', [])
        if not available_room_names:
            return []

        # Get room objects that match the names and meet requirements
        available_rooms = []
        for room_name in available_room_names:
            room = Room.query.filter_by(name=room_name.strip(), is_active=True).first()
            if room:
                # Check computer requirement
                if exam.needs_computer and not room.has_computer:
                    continue

                # Check availability
                if self._is_room_available(room.id, target_date, start_time, end_time):
                    available_rooms.append(room)

        if not available_rooms:
            return []

        # Sort by capacity (largest first for better optimization)
        available_rooms.sort(key=lambda r: r.capacity, reverse=True)

        # Try to find room combination that fits all students
        return self._find_room_combination(available_rooms, exam.student_count)
    
    def _find_room_combination(self, available_rooms, required_capacity):
        """Find combination of rooms to accommodate all students"""
        print(f"DEBUG: Finding room combination for {required_capacity} students")
        print(f"DEBUG: Available rooms: {[(r.name, r.capacity) for r in available_rooms]}")

        # Try single room first
        for room in available_rooms:
            if room.capacity >= required_capacity:
                print(f"DEBUG: Single room sufficient: {room.name} (capacity: {room.capacity})")
                return [room]

        print(f"DEBUG: No single room sufficient, trying combinations...")

        # Try combination of rooms (up to 3 rooms)
        for i, room1 in enumerate(available_rooms):
            remaining_capacity = required_capacity - room1.capacity
            if remaining_capacity <= 0:
                continue

            for j, room2 in enumerate(available_rooms[i+1:], i+1):
                total_capacity = room1.capacity + room2.capacity
                if total_capacity >= required_capacity:
                    print(f"DEBUG: Two-room combination found: {room1.name} + {room2.name} (total: {total_capacity})")
                    return [room1, room2]

                remaining_capacity2 = required_capacity - total_capacity
                if remaining_capacity2 <= 0:
                    continue

                for room3 in available_rooms[j+1:]:
                    total_capacity3 = room1.capacity + room2.capacity + room3.capacity
                    if total_capacity3 >= required_capacity:
                        print(f"DEBUG: Three-room combination found: {room1.name} + {room2.name} + {room3.name} (total: {total_capacity3})")
                        return [room1, room2, room3]

        print(f"DEBUG: No suitable room combination found for {required_capacity} students")
        return []  # No suitable combination found
    
    def _is_room_available(self, room_id, target_date, start_time, end_time):
        """Check if room is available at the given time"""
        # Check for overlapping schedules in primary room
        overlapping = ExamSchedule.query.filter(
            ExamSchedule.room_id == room_id,
            ExamSchedule.scheduled_date == target_date,
            db.or_(
                # New exam starts during existing exam
                db.and_(
                    ExamSchedule.start_time <= start_time,
                    ExamSchedule.end_time > start_time
                ),
                # New exam ends during existing exam
                db.and_(
                    ExamSchedule.start_time < end_time,
                    ExamSchedule.end_time >= end_time
                ),
                # New exam completely contains existing exam
                db.and_(
                    ExamSchedule.start_time >= start_time,
                    ExamSchedule.end_time <= end_time
                )
            )
        ).first()

        if overlapping:
            return False

        # Also check if this room is used as an additional room in any schedule
        overlapping_additional = ExamSchedule.query.filter(
            ExamSchedule.scheduled_date == target_date,
            ExamSchedule.additional_rooms.isnot(None),
            func.json_contains(ExamSchedule.additional_rooms, str(room_id)),
            db.or_(
                # New exam starts during existing exam
                db.and_(
                    ExamSchedule.start_time <= start_time,
                    ExamSchedule.end_time > start_time
                ),
                # New exam ends during existing exam
                db.and_(
                    ExamSchedule.start_time < end_time,
                    ExamSchedule.end_time >= end_time
                ),
                # New exam completely contains existing exam
                db.and_(
                    ExamSchedule.start_time >= start_time,
                    ExamSchedule.end_time <= end_time
                )
            )
        ).first()

        return overlapping_additional is None
    
    def _create_exam_schedule(self, exam, rooms, target_date, start_time, end_time, daily_schedules):
        """Create exam schedule with room assignments"""
        try:
            # Primary room is the first (largest capacity)
            primary_room = rooms[0]

            # Prepare additional rooms list (exclude primary room)
            additional_room_ids = [room.id for room in rooms[1:]] if len(rooms) > 1 else None

            # Calculate total capacity
            total_capacity = sum(room.capacity for room in rooms)

            schedule = ExamSchedule(
                exam_id=exam.id,
                room_id=primary_room.id,
                additional_rooms=additional_room_ids,
                scheduled_date=target_date,
                start_time=start_time,
                end_time=end_time
            )

            db.session.add(schedule)
            exam.status = 'planned'

            # Update daily schedules tracking
            date_key = target_date.strftime('%Y-%m-%d')
            if date_key not in daily_schedules:
                daily_schedules[date_key] = []
            daily_schedules[date_key].append(exam)

            # Log multi-room assignment
            if len(rooms) > 1:
                room_names = [room.name for room in rooms]
                print(f"DEBUG: Multi-room assignment for {exam.course.code}: {', '.join(room_names)} (Total capacity: {total_capacity}, Students: {exam.student_count})")
            else:
                print(f"DEBUG: Single room assignment for {exam.course.code}: {primary_room.name} (Capacity: {primary_room.capacity}, Students: {exam.student_count})")

            return True
            
        except Exception as e:
            print(f"Error creating exam schedule: {str(e)}")
            return False

    def schedule_exams(self, exam_data_list):
        """Schedule multiple exams with advanced constraints"""
        try:
            # Get exam week settings
            exam_week_start_setting = Settings.query.filter_by(key='exam_week_start').first()
            exam_week_end_setting = Settings.query.filter_by(key='exam_week_end').first()

            if not exam_week_start_setting or not exam_week_end_setting:
                return {
                    'success': False,
                    'message': 'Exam week dates not configured',
                    'scheduled_count': 0,
                    'failed_count': len(exam_data_list),
                    'details': []
                }

            # Parse dates from settings
            from datetime import datetime
            try:
                exam_week_start = datetime.strptime(exam_week_start_setting.value, '%Y-%m-%d').date()
                exam_week_end = datetime.strptime(exam_week_end_setting.value, '%Y-%m-%d').date()
            except ValueError:
                return {
                    'success': False,
                    'message': 'Invalid exam week date format',
                    'scheduled_count': 0,
                    'failed_count': len(exam_data_list),
                    'details': []
                }

            # Get valid exam dates (only weekdays within exam week)
            exam_dates = []
            current_date = exam_week_start
            while current_date <= exam_week_end:
                if current_date.weekday() < 5:  # Monday=0, Friday=4
                    exam_dates.append(current_date)
                current_date += timedelta(days=1)

            if not exam_dates:
                return {
                    'success': False,
                    'message': 'No valid exam dates found',
                    'scheduled_count': 0,
                    'failed_count': len(exam_data_list),
                    'details': []
                }

            # Track daily schedules for constraint checking
            daily_schedules = {}
            scheduled_count = 0
            failed_count = 0
            details = []

            # Get exam objects from database
            exams_to_schedule = []
            for exam_data in exam_data_list:
                exam = Exam.query.get(exam_data['id'])
                if exam:
                    exams_to_schedule.append(exam)
                else:
                    failed_count += 1
                    details.append(f"Exam ID {exam_data['id']} not found")

            # Sort exams by priority (difficulty, student count, duration)
            exams_to_schedule.sort(key=lambda e: (
                {'very_hard': 4, 'hard': 3, 'normal': 2, 'easy': 1}.get(e.difficulty_level, 2),
                -e.student_count,  # Larger classes first
                -e.duration        # Longer exams first
            ), reverse=True)

            # Schedule each exam
            for exam in exams_to_schedule:
                scheduled = False

                # Try each preferred date first
                preferred_dates = getattr(exam, 'preferred_dates', [])
                if preferred_dates:
                    for pref_date in preferred_dates:
                        if isinstance(pref_date, str):
                            try:
                                pref_date = datetime.strptime(pref_date, '%Y-%m-%d').date()
                            except:
                                continue

                        if pref_date in exam_dates:
                            if self._try_schedule_exam_on_date(exam, pref_date, daily_schedules):
                                scheduled = True
                                scheduled_count += 1
                                details.append(f"Scheduled {exam.course.code} on preferred date {pref_date}")
                                break

                # If not scheduled on preferred dates, try all available dates
                if not scheduled:
                    for exam_date in exam_dates:
                        if self._try_schedule_exam_on_date(exam, exam_date, daily_schedules):
                            scheduled = True
                            scheduled_count += 1
                            details.append(f"Scheduled {exam.course.code} on {exam_date}")
                            break

                if not scheduled:
                    failed_count += 1
                    details.append(f"Failed to schedule {exam.course.code} - no suitable time slot found")

            # Commit all changes
            db.session.commit()

            return {
                'success': True,
                'message': f'Scheduled {scheduled_count} out of {len(exams_to_schedule)} exams',
                'scheduled_count': scheduled_count,
                'failed_count': failed_count,
                'details': details
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Scheduling failed: {str(e)}',
                'scheduled_count': 0,
                'failed_count': len(exam_data_list),
                'details': [str(e)]
            }

    def _try_schedule_exam_on_date(self, exam, target_date, daily_schedules):
        """Try to schedule an exam on a specific date with flexible timing"""
        # Generate all possible start times for this exam duration
        possible_start_times = self._generate_possible_start_times(target_date, exam.duration)

        # Try each possible start time
        for start_time in possible_start_times:
            # Calculate end time based on exam duration
            duration_minutes = exam.duration
            end_time = (datetime.combine(target_date, start_time) +
                       timedelta(minutes=duration_minutes)).time()

            # Check all constraints
            if not self._check_difficulty_level_rules(exam, target_date, daily_schedules):
                continue

            if not self._check_class_level_conflicts(exam, target_date, start_time, end_time, daily_schedules):
                continue

            if not self._check_time_gap_requirement(target_date, start_time, end_time, daily_schedules):
                continue

            # Find suitable rooms
            suitable_rooms = self._find_suitable_rooms(exam, target_date, start_time, end_time)
            if not suitable_rooms:
                continue

            # Create the schedule
            if self._create_exam_schedule(exam, suitable_rooms, target_date, start_time, end_time, daily_schedules):
                return True

        return False


