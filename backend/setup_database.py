#!/usr/bin/env python3
"""
Database setup script for Exam Orchestrator
This script creates the database and tables, and populates them with initial data.
"""

import os
import sys
from datetime import date, datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db, init_db, reset_db
from models import Department, Exam, ExamSchedule, Room, Settings


def setup_database(reset=False):
    """Setup database with initial data"""
    app = create_app()

    with app.app_context():
        if reset:
            print("Resetting database...")
            reset_db(app)
        else:
            print("Initializing database...")
            init_db(app)

        print("Database setup completed successfully!")

def add_sample_data():
    """Add sample exam data for testing"""
    app = create_app()

    with app.app_context():
        # Check if sample data already exists
        if Exam.query.count() > 0:
            print("Sample data already exists. Skipping...")
            return

        print("Adding sample exam data...")

        # Get departments
        bm_dept = Department.query.filter_by(code='BM').first()
        em_dept = Department.query.filter_by(code='EM').first()
        ee_dept = Department.query.filter_by(code='EE').first()

        if not bm_dept or not em_dept or not ee_dept:
            print("Departments not found. Please run database setup first.")
            return

        # Sample exams with credits and advanced constraints
        sample_exams = [
            {
                'course_name': 'Veri Yapıları ve Algoritmalar',
                'class_name': '2',
                'instructor': 'Dr. Ahmet Yılmaz',
                'student_count': 45,
                'duration': 120,
                'credits': 4,  # Difficult course
                'needs_computer': True,
                'preferred_dates': ['2024-01-15', '2024-01-17', '2024-01-19'],
                'department_id': bm_dept.id
            },
            {
                'course_name': 'Yazılım Mühendisliği',
                'class_name': '3',
                'instructor': 'Prof. Dr. Fatma Kaya',
                'student_count': 35,
                'duration': 90,
                'credits': 3,
                'needs_computer': True,
                'preferred_dates': ['2024-01-16', '2024-01-18', '2024-01-20'],
                'department_id': bm_dept.id
            },
            {
                'course_name': 'Calculus I',
                'class_name': '1',
                'instructor': 'Dr. Mehmet Demir',
                'student_count': 60,
                'duration': 90,
                'credits': 5,  # Difficult course
                'needs_computer': False,
                'preferred_dates': ['2024-01-15', '2024-01-17', '2024-01-19'],
                'department_id': em_dept.id
            },
            {
                'course_name': 'İstatistik',
                'class_name': '2',
                'instructor': 'Dr. Ayşe Öztürk',
                'student_count': 50,
                'duration': 75,
                'credits': 3,
                'needs_computer': False,
                'preferred_dates': ['2024-01-16', '2024-01-18', '2024-01-20'],
                'department_id': em_dept.id
            },
            {
                'course_name': 'Devre Analizi',
                'class_name': '2',
                'instructor': 'Prof. Dr. Ali Çelik',
                'student_count': 40,
                'duration': 105,
                'credits': 4,  # Difficult course
                'needs_computer': False,
                'preferred_dates': ['2024-01-15', '2024-01-17', '2024-01-19'],
                'department_id': ee_dept.id
            },
            {
                'course_name': 'Mikroişlemciler',
                'class_name': '3',
                'instructor': 'Dr. Zeynep Arslan',
                'student_count': 30,
                'duration': 120,
                'credits': 4,  # Difficult course
                'needs_computer': True,
                'preferred_dates': ['2024-01-16', '2024-01-18', '2024-01-20'],
                'department_id': ee_dept.id
            },
            {
                'course_name': 'Programlama Temelleri',
                'class_name': '1',
                'instructor': 'Dr. Can Özkan',
                'student_count': 55,
                'duration': 90,
                'credits': 3,
                'needs_computer': True,
                'preferred_dates': ['2024-01-15', '2024-01-17', '2024-01-19'],
                'department_id': bm_dept.id
            },
            {
                'course_name': 'Fizik I',
                'class_name': '1',
                'instructor': 'Prof. Dr. Elif Yıldız',
                'student_count': 65,
                'duration': 105,
                'credits': 3,
                'needs_computer': False,
                'preferred_dates': ['2024-01-16', '2024-01-18', '2024-01-20'],
                'department_id': ee_dept.id
            }
        ]

        # Add sample exams
        for exam_data in sample_exams:
            exam = Exam(**exam_data)
            db.session.add(exam)

        db.session.commit()
        print(f"Added {len(sample_exams)} sample exams.")
        print("Sample data setup completed!")

def show_database_info():
    """Show current database information"""
    app = create_app()

    with app.app_context():
        print("\n=== Database Information ===")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Count records
        dept_count = Department.query.count()
        room_count = Room.query.count()
        exam_count = Exam.query.count()
        schedule_count = ExamSchedule.query.count()
        settings_count = Settings.query.count()

        print(f"Departments: {dept_count}")
        print(f"Rooms: {room_count}")
        print(f"Exams: {exam_count}")
        print(f"Schedules: {schedule_count}")
        print(f"Settings: {settings_count}")

        # Show departments
        if dept_count > 0:
            print("\nDepartments:")
            departments = Department.query.all()
            for dept in departments:
                print(f"  - {dept.name} ({dept.code})")

        # Show exam week settings
        start_setting = Settings.query.filter_by(key='exam_week_start').first()
        end_setting = Settings.query.filter_by(key='exam_week_end').first()

        if start_setting and end_setting:
            print(f"\nExam Week: {start_setting.value} to {end_setting.value}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python setup_database.py [command]")
        print("Commands:")
        print("  init     - Initialize database with default data")
        print("  reset    - Reset database (WARNING: This will delete all data)")
        print("  sample   - Add sample exam data")
        print("  info     - Show database information")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        setup_database(reset=False)
    elif command == 'reset':
        confirm = input("This will delete all data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            setup_database(reset=True)
        else:
            print("Operation cancelled.")
    elif command == 'sample':
        add_sample_data()
    elif command == 'info':
        show_database_info()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, reset, sample, info")

if __name__ == '__main__':
    main()
