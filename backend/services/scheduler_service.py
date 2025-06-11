from datetime import date, datetime, time, timedelta

from database import db
from models import Exam, ExamSchedule, Room, Settings
from services.advanced_scheduler import AdvancedSchedulerService


class SchedulerService(AdvancedSchedulerService):
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

    def generate_schedule(self, force_regenerate=False, department_id=None):
        """Generate automatic schedule for pending exams with advanced rules"""
        try:
            # Get exam week settings
            exam_week = self._get_exam_week_settings()
            if not exam_week['start_date'] or not exam_week['end_date']:
                return {
                    'success': False,
                    'message': 'Exam week dates not configured. Please set exam week range first.'
                }

            # Get pending exams
            query = Exam.query.filter_by(status='pending')
            if department_id:
                query = query.filter_by(department_id=department_id)

            pending_exams = query.all()

            if not pending_exams:
                return {
                    'success': True,
                    'message': 'No pending exams to schedule',
                    'scheduled_count': 0,
                    'failed_count': 0,
                    'failed_exams': []
                }

            # If force regenerate, clear existing schedules for these exams
            if force_regenerate:
                for exam in pending_exams:
                    if exam.exam_schedule:
                        db.session.delete(exam.exam_schedule)
                        exam.status = 'pending'
                db.session.commit()

            scheduled_count = 0
            failed_count = 0
            failed_exams = []

            # Sort exams by priority with new rules
            sorted_exams = self._prioritize_exams_advanced(pending_exams)

            # Track daily schedules for constraint checking
            daily_schedules = {}

            for exam in sorted_exams:
                success, reason = self._schedule_exam_advanced(exam, exam_week, daily_schedules)
                if success:
                    scheduled_count += 1
                else:
                    failed_count += 1
                    failed_exams.append({
                        'id': exam.id,
                        'course_name': exam.course_name,
                        'class_name': exam.class_name,
                        'instructor': exam.instructor,
                        'reason': reason
                    })

            db.session.commit()

            return {
                'success': True,
                'message': f'Scheduling completed. {scheduled_count} exams scheduled, {failed_count} failed.',
                'scheduled_count': scheduled_count,
                'failed_count': failed_count,
                'failed_exams': failed_exams
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error during scheduling: {str(e)}'
            }

    def _get_exam_week_settings(self):
        """Get exam week date range from settings"""
        start_setting = Settings.query.filter_by(key='exam_week_start').first()
        end_setting = Settings.query.filter_by(key='exam_week_end').first()

        start_date = None
        end_date = None

        if start_setting:
            start_date = datetime.strptime(start_setting.value, '%Y-%m-%d').date()
        if end_setting:
            end_date = datetime.strptime(end_setting.value, '%Y-%m-%d').date()

        return {
            'start_date': start_date,
            'end_date': end_date
        }

    def _prioritize_exams_advanced(self, exams):
        """Sort exams by priority with advanced rules based on difficulty level and duration"""
        def priority_key(exam):
            # Priority factors (higher values = higher priority):
            # 1. Difficulty level (very_hard > hard > normal > easy)
            # 2. Duration (longer exams harder to fit)
            # 3. Computer requirement (limited resources)
            # 4. Student count (capacity constraints)
            # 5. Fewer preferred dates (less flexibility)

            # Difficulty level priority
            difficulty_scores = {
                'very_hard': 20,
                'hard': 15,
                'normal': 10,
                'easy': 5
            }
            difficulty_priority = difficulty_scores.get(exam.difficulty_level, 10)

            # Duration priority (longer exams get higher priority)
            if exam.duration >= 120:
                duration_priority = 8
            elif exam.duration >= 90:
                duration_priority = 6
            elif exam.duration >= 60:
                duration_priority = 4
            else:
                duration_priority = 2

            computer_priority = 5 if exam.needs_computer else 0
            student_priority = exam.student_count / 100  # Normalize to 0-5 range

            # Count valid preferred dates
            preferred_count = len(exam.preferred_dates) if exam.preferred_dates else 0
            flexibility_penalty = 5 - min(preferred_count, 5)  # Less flexibility = higher priority

            return (difficulty_priority, duration_priority, computer_priority,
                   student_priority, flexibility_penalty)

        return sorted(exams, key=priority_key, reverse=True)

    def _schedule_exam_advanced(self, exam, exam_week, daily_schedules):
        """Try to schedule a single exam with advanced constraints"""
        # Get valid preferred dates
        preferred_dates = self._get_valid_preferred_dates(exam, exam_week)
        
        if not preferred_dates:
            return False, "No valid preferred dates within exam week"
        
        # Try to find a suitable slot
        for target_date in preferred_dates:
            # Get possible start times for this date
            possible_start_times = self._get_possible_start_times(target_date, exam.duration)
            
            for start_time in possible_start_times:
                # Calculate actual end time based on exam duration
                end_time = self._calculate_end_time(start_time, exam.duration)
                
                # Check all constraints
                if self._check_all_constraints(exam, target_date, start_time, end_time, daily_schedules):
                    # Find suitable rooms
                    rooms = self._find_suitable_rooms(exam, target_date, start_time, end_time)
                    if rooms:
                        # Create schedule(s)
                        success = self._create_exam_schedule(exam, rooms, target_date, start_time, end_time, daily_schedules)
                        if success:
                            return True, "Successfully scheduled"
        
        return False, "No suitable time slot found that satisfies all constraints"

    def _get_valid_preferred_dates(self, exam, exam_week):
        """Get valid preferred dates within exam week"""
        preferred_dates = []
        if exam.preferred_dates:
            for date_str in exam.preferred_dates:
                try:
                    if isinstance(date_str, str):
                        preferred_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        preferred_date = date_str

                    # Check if date is within exam week and is a weekday
                    if (exam_week['start_date'] <= preferred_date <= exam_week['end_date'] and
                        preferred_date.weekday() < 5):  # Monday = 0, Sunday = 6
                        preferred_dates.append(preferred_date)
                except ValueError:
                    continue

        # If no valid preferred dates, use all exam week weekdays
        if not preferred_dates:
            current_date = exam_week['start_date']
            while current_date <= exam_week['end_date']:
                if current_date.weekday() < 5:  # Skip weekends
                    preferred_dates.append(current_date)
                current_date += timedelta(days=1)

        return preferred_dates

    def _get_time_slots_for_date(self, target_date):
        """Get appropriate time slots for a specific date"""
        if target_date.weekday() == 4:  # Friday
            return self.friday_time_slots
        else:
            return self.time_slots

    def _calculate_end_time(self, start_time, duration_minutes):
        """Calculate end time based on start time and duration"""
        start_datetime = datetime.combine(date.today(), start_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        return end_datetime.time()

    def _check_all_constraints(self, exam, target_date, start_time, end_time, daily_schedules):
        """Check all scheduling constraints"""
        # Rule 1: Check forbidden time slots
        if not self._check_time_slot_rules(target_date, start_time, end_time):
            return False

        # Rule 2: Check difficulty level constraints
        if not self._check_difficulty_level_rules(exam, target_date, daily_schedules):
            return False

        # Rule 3: Check class level conflicts
        if not self._check_class_level_conflicts(exam, target_date, start_time, end_time, daily_schedules):
            return False

        # Rule 4: Check 15-minute gap requirement
        if not self._check_time_gap_requirement(target_date, start_time, end_time, daily_schedules):
            return False

        return True

    def _schedule_exam(self, exam, exam_week):
        """Try to schedule a single exam"""
        # Get preferred dates or use exam week range
        preferred_dates = []
        if exam.preferred_dates:
            for date_str in exam.preferred_dates:
                try:
                    if isinstance(date_str, str):
                        preferred_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        preferred_date = date_str

                    # Check if date is within exam week
                    if exam_week['start_date'] <= preferred_date <= exam_week['end_date']:
                        preferred_dates.append(preferred_date)
                except ValueError:
                    continue

        # If no valid preferred dates, use all exam week dates
        if not preferred_dates:
            current_date = exam_week['start_date']
            while current_date <= exam_week['end_date']:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                    preferred_dates.append(current_date)
                current_date += timedelta(days=1)

        # Try to find a suitable slot
        for target_date in preferred_dates:
            for start_time, default_end_time in self.time_slots:
                # Calculate actual end time based on exam duration
                duration_minutes = exam.duration
                end_time = (datetime.combine(date.today(), start_time) +
                           timedelta(minutes=duration_minutes)).time()

                # Find suitable room
                room = self._find_suitable_room(exam, target_date, start_time, end_time)
                if room:
                    # Create schedule
                    schedule = ExamSchedule(
                        exam_id=exam.id,
                        room_id=room.id,
                        scheduled_date=target_date,
                        start_time=start_time,
                        end_time=end_time
                    )

                    db.session.add(schedule)
                    exam.status = 'planned'
                    return True

        return False

    def _find_suitable_room(self, exam, target_date, start_time, end_time):
        """Find a suitable room for the exam"""
        # Get rooms that meet requirements
        query = Room.query.filter_by(is_active=True)

        # Filter by computer requirement
        if exam.needs_computer:
            query = query.filter_by(has_computer=True)

        # Filter by capacity
        query = query.filter(Room.capacity >= exam.student_count)

        # Prefer rooms from the same department
        rooms = query.order_by(
            (Room.department_id == exam.department_id).desc(),
            Room.capacity.asc()
        ).all()

        # Check availability
        for room in rooms:
            if self._is_room_available(room.id, target_date, start_time, end_time):
                return room

        return None

    def _is_room_available(self, room_id, target_date, start_time, end_time):
        """Check if room is available at the given time"""
        # Check for overlapping schedules
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

        return overlapping is None


