#!/usr/bin/env python3
"""
Test script to verify capacity control and multi-room assignment functionality
"""

from datetime import datetime, date
from database import db
from models import Exam, Course, Department, Room, Settings
from services.advanced_scheduler import AdvancedSchedulerService
from app import create_app

def test_capacity_control():
    """Test that the system assigns multiple rooms when capacity is insufficient"""
    
    app = create_app()
    with app.app_context():
        print("=== Testing Capacity Control and Multi-Room Assignment ===\n")
        
        # Get available rooms
        rooms = Room.query.filter_by(is_active=True).all()
        print("Available rooms:")
        for room in rooms:
            print(f"  {room.name}: capacity={room.capacity}, has_computer={room.has_computer}")
        
        # Find the largest single room capacity
        max_single_capacity = max(room.capacity for room in rooms) if rooms else 0
        print(f"\nLargest single room capacity: {max_single_capacity}")
        
        # Create a test exam that requires more students than the largest room
        test_student_count = max_single_capacity + 20  # Exceed largest room by 20 students
        print(f"Test exam student count: {test_student_count}")
        
        # Get or create test department
        dept = Department.query.first()
        if not dept:
            dept = Department(name="Test Department", code="TEST")
            db.session.add(dept)
            db.session.commit()
        
        # Get or create test course
        course = Course.query.first()
        if not course:
            course = Course(
                name="Test Course",
                code="TEST101",
                credits=3,
                class_level=1,
                department_id=dept.id
            )
            db.session.add(course)
            db.session.commit()
        
        # Create test exam with high student count
        test_exam = Exam(
            course_id=course.id,
            instructor="Test Instructor",
            student_count=test_student_count,
            duration=120,
            needs_computer=False,
            preferred_dates=["2024-01-15", "2024-01-16", "2024-01-17"],
            department_id=dept.id,
            difficulty_level="normal",
            available_rooms=[room.name for room in rooms[:6]]  # Use first 6 rooms
        )
        
        db.session.add(test_exam)
        db.session.commit()
        
        print(f"\nCreated test exam:")
        print(f"  Course: {test_exam.course.code}")
        print(f"  Students: {test_exam.student_count}")
        print(f"  Available rooms: {test_exam.available_rooms}")
        
        # Set exam week settings
        start_setting = Settings.query.filter_by(key='exam_week_start').first()
        end_setting = Settings.query.filter_by(key='exam_week_end').first()
        
        if not start_setting:
            start_setting = Settings(key='exam_week_start', value='2024-01-15')
            db.session.add(start_setting)
        else:
            start_setting.value = '2024-01-15'
            
        if not end_setting:
            end_setting = Settings(key='exam_week_end', value='2024-01-19')
            db.session.add(end_setting)
        else:
            end_setting.value = '2024-01-19'
            
        db.session.commit()
        
        # Test the scheduler
        scheduler = AdvancedSchedulerService()
        
        # Prepare exam data for scheduling
        exam_data = [{
            'id': test_exam.id,
            'course_code': test_exam.course.code,
            'instructor': test_exam.instructor,
            'student_count': test_exam.student_count,
            'duration': test_exam.duration,
            'needs_computer': test_exam.needs_computer,
            'preferred_dates': test_exam.preferred_dates,
            'available_rooms': test_exam.available_rooms,
            'difficulty': test_exam.difficulty_level
        }]
        
        print(f"\n=== Testing Scheduler ===")
        result = scheduler.schedule_exams(exam_data)
        
        print(f"\nScheduling result:")
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        print(f"  Scheduled: {result['scheduled_count']}")
        print(f"  Failed: {result['failed_count']}")
        
        if result['details']:
            print("  Details:")
            for detail in result['details']:
                print(f"    - {detail}")
        
        # Check if exam was scheduled and with how many rooms
        test_exam = Exam.query.get(test_exam.id)
        if test_exam.exam_schedules:
            schedule = test_exam.exam_schedules[0]
            print(f"\n=== Exam Schedule Created ===")
            print(f"  Primary room: {schedule.room.name} (capacity: {schedule.room.capacity})")
            print(f"  Date: {schedule.scheduled_date}")
            print(f"  Time: {schedule.start_time} - {schedule.end_time}")
            
            total_capacity = schedule.room.capacity
            
            if schedule.additional_rooms:
                print(f"  Additional rooms: {schedule.additional_rooms}")
                for room_id in schedule.additional_rooms:
                    room = Room.query.get(room_id)
                    if room:
                        print(f"    - {room.name} (capacity: {room.capacity})")
                        total_capacity += room.capacity
                        
            print(f"  Total capacity: {total_capacity}")
            print(f"  Students: {test_exam.student_count}")
            print(f"  Capacity sufficient: {total_capacity >= test_exam.student_count}")
            
            if total_capacity >= test_exam.student_count:
                print("\n✅ SUCCESS: Multi-room assignment working correctly!")
            else:
                print("\n❌ FAILURE: Insufficient total capacity assigned!")
                
        else:
            print("\n❌ FAILURE: Exam was not scheduled!")
        
        # Clean up test data
        if test_exam.exam_schedules:
            for schedule in test_exam.exam_schedules:
                db.session.delete(schedule)
        db.session.delete(test_exam)
        db.session.commit()
        
        print("\n=== Test completed and cleaned up ===")

if __name__ == "__main__":
    test_capacity_control()
