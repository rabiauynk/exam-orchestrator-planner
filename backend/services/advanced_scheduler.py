from datetime import datetime, date, time, timedelta
from database import db
from models import Exam, ExamSchedule, Room, Settings

class AdvancedSchedulerService:
    """Advanced scheduler with comprehensive constraint checking"""
    
    def __init__(self):
        # Define valid time slots with 15-minute gaps
        # Excluding 12:15-13:00 (lunch break)
        self.time_slots = [
            (time(8, 30), time(10, 0)),   # 08:30-10:00
            (time(10, 15), time(11, 45)), # 10:15-11:45
            (time(13, 0), time(14, 30)),  # 13:00-14:30
            (time(14, 45), time(16, 15)), # 14:45-16:15
            (time(16, 30), time(18, 0)),  # 16:30-18:00
        ]
        
        # Friday special time slots (excluding 12:00-13:30)
        self.friday_time_slots = [
            (time(8, 30), time(10, 0)),   # 08:30-10:00
            (time(10, 15), time(11, 45)), # 10:15-11:45
            (time(13, 30), time(15, 0)),  # 13:30-15:00
            (time(15, 15), time(16, 45)), # 15:15-16:45
            (time(17, 0), time(18, 30)),  # 17:00-18:30
        ]
    
    def _check_time_slot_rules(self, target_date, start_time, end_time):
        """Check time slot constraints"""
        # Rule 1: No exams during 12:15-13:00
        forbidden_start = time(12, 15)
        forbidden_end = time(13, 0)
        
        if (start_time < forbidden_end and end_time > forbidden_start):
            return False
        
        # Rule 2: Friday 12:00-13:30 restriction
        if target_date.weekday() == 4:  # Friday
            friday_forbidden_start = time(12, 0)
            friday_forbidden_end = time(13, 30)
            
            if (start_time < friday_forbidden_end and end_time > friday_forbidden_start):
                return False
        
        return True
    
    def _check_difficult_exam_rules(self, exam, target_date, daily_schedules):
        """Check difficult exam constraints (credits >= 4)"""
        if not exam.is_difficult:
            return True
        
        # Get existing schedules for the day
        date_key = target_date.strftime('%Y-%m-%d')
        if date_key not in daily_schedules:
            return True
        
        # Check if there's already a difficult exam on this day
        for scheduled_exam in daily_schedules[date_key]:
            if scheduled_exam.is_difficult:
                return False
        
        return True
    
    def _check_class_level_conflicts(self, exam, target_date, start_time, end_time, daily_schedules):
        """Check class level conflict constraints"""
        date_key = target_date.strftime('%Y-%m-%d')
        if date_key not in daily_schedules:
            return True
        
        # Check for same class level conflicts in the same time slot
        for scheduled_exam in daily_schedules[date_key]:
            if scheduled_exam.class_name == exam.class_name:
                # Get the scheduled time for this exam
                schedule = scheduled_exam.exam_schedule
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
            schedule = scheduled_exam.exam_schedule
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
        # Get rooms that meet basic requirements
        query = Room.query.filter_by(is_active=True)
        
        # Filter by computer requirement
        if exam.needs_computer:
            query = query.filter_by(has_computer=True)
        
        # Get available rooms (not conflicting with existing schedules)
        available_rooms = []
        for room in query.all():
            if self._is_room_available(room.id, target_date, start_time, end_time):
                available_rooms.append(room)
        
        # Sort by preference: department match, then capacity
        available_rooms.sort(key=lambda r: (
            r.department_id == exam.department_id,  # Same department first
            -abs(r.capacity - exam.student_count)   # Closest capacity match
        ), reverse=True)
        
        # Try to find room combination that fits all students
        return self._find_room_combination(available_rooms, exam.student_count)
    
    def _find_room_combination(self, available_rooms, required_capacity):
        """Find combination of rooms to accommodate all students"""
        # Try single room first
        for room in available_rooms:
            if room.capacity >= required_capacity:
                return [room]
        
        # Try combination of rooms (up to 3 rooms)
        for i, room1 in enumerate(available_rooms):
            remaining_capacity = required_capacity - room1.capacity
            if remaining_capacity <= 0:
                continue
            
            for j, room2 in enumerate(available_rooms[i+1:], i+1):
                if room1.capacity + room2.capacity >= required_capacity:
                    return [room1, room2]
                
                remaining_capacity2 = required_capacity - room1.capacity - room2.capacity
                if remaining_capacity2 <= 0:
                    continue
                
                for room3 in available_rooms[j+1:]:
                    if room1.capacity + room2.capacity + room3.capacity >= required_capacity:
                        return [room1, room2, room3]
        
        return []  # No suitable combination found
    
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
    
    def _create_exam_schedule(self, exam, rooms, target_date, start_time, end_time, daily_schedules):
        """Create exam schedule with room assignments"""
        try:
            # For multiple rooms, we'll create one schedule with the primary room
            # and store additional rooms in a separate table or as JSON
            primary_room = rooms[0]
            
            schedule = ExamSchedule(
                exam_id=exam.id,
                room_id=primary_room.id,
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
            
            # Store additional rooms info if multiple rooms used
            if len(rooms) > 1:
                # You could extend the model to store multiple rooms
                # For now, we'll use the primary room
                pass
            
            return True
            
        except Exception as e:
            print(f"Error creating exam schedule: {str(e)}")
            return False
