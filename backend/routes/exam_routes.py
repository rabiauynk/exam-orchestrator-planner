import json
import random
from datetime import datetime, time

from database import db
from flask import Blueprint, jsonify, request
from models import (Department, Exam, ExamSchedule, Room, Settings,
                    exam_schema, exams_schema)

exam_bp = Blueprint('exams', __name__)

def auto_schedule_exam(exam):
    """Automatically schedule a single exam"""
    try:
        from services.advanced_scheduler import AdvancedSchedulerService

        # Prepare exam data for scheduler
        exam_data = [{
            'id': exam.id,
            'course_code': exam.course.code if exam.course else 'Unknown',
            'instructor': exam.instructor,
            'student_count': exam.student_count,
            'duration': exam.duration,
            'needs_computer': exam.needs_computer,
            'preferred_dates': exam.preferred_dates or [],
            'available_rooms': exam.available_rooms or [],
            'department_id': exam.department_id,
            'difficulty_level': exam.difficulty_level,
            'status': exam.status
        }]

        # Run scheduler
        scheduler = AdvancedSchedulerService()
        result = scheduler.schedule_exams(exam_data)

        if result['success'] and result['scheduled_count'] > 0:
            print(f"Successfully scheduled exam {exam.course.code if exam.course else exam.id}")
            return True
        else:
            print(f"Failed to schedule exam {exam.course.code if exam.course else exam.id}: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"Auto-scheduling error for exam {exam.id}: {str(e)}")
        return False





@exam_bp.route('/api/exams', methods=['GET'])
def get_exams():
    """Get all exams"""
    try:
        exams = Exam.query.all()
        return jsonify({
            'success': True,
            'data': exams_schema.dump(exams)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching exams: {str(e)}'
        }), 500

@exam_bp.route('/api/exams', methods=['POST'])
def create_exam():
    """Create a new exam"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'instructor', 'student_count', 'duration', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate course exists
        from models import Course
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404

        # Validate department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404

        # Process preferred dates
        preferred_dates = data.get('preferred_dates', [])
        if isinstance(preferred_dates, list) and len(preferred_dates) > 0:
            # Convert date strings to proper format if needed
            processed_dates = []
            for date_str in preferred_dates:
                if isinstance(date_str, str):
                    try:
                        # Try to parse different date formats
                        if 'T' in date_str:  # ISO format
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:  # Assume DD/MM/YYYY format
                            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        processed_dates.append(date_obj.strftime('%Y-%m-%d'))
                    except ValueError:
                        processed_dates.append(date_str)
                else:
                    processed_dates.append(date_str)
            preferred_dates = processed_dates

        # Create new exam
        new_exam = Exam(
            course_id=data['course_id'],
            instructor=data['instructor'],
            student_count=int(data['student_count']),
            duration=int(data['duration']),
            needs_computer=data.get('needs_computer', False),
            preferred_dates=preferred_dates,
            department_id=data['department_id'],
            status='pending'
        )

        db.session.add(new_exam)
        db.session.commit()

        # Otomatik planlama yap
        try:
            auto_schedule_exam(new_exam)
            message = 'Sınav eklendi ve otomatik olarak planlandı'
        except Exception as e:
            print(f"Auto-scheduling error: {str(e)}")
            message = 'Sınav eklendi ancak otomatik planlama başarısız'

        return jsonify({
            'success': True,
            'message': message,
            'data': exam_schema.dump(new_exam)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    """Get a specific exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        return jsonify({
            'success': True,
            'data': exam_schema.dump(exam)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    """Update an exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        data = request.get_json()

        # Update fields if provided
        if 'course_id' in data:
            # Validate course exists
            from models import Course
            course = Course.query.get(data['course_id'])
            if not course:
                return jsonify({
                    'success': False,
                    'message': 'Course not found'
                }), 404
            exam.course_id = data['course_id']
        if 'instructor' in data:
            exam.instructor = data['instructor']
        if 'student_count' in data:
            exam.student_count = int(data['student_count'])
        if 'duration' in data:
            exam.duration = int(data['duration'])
        if 'needs_computer' in data:
            exam.needs_computer = data['needs_computer']
        if 'preferred_dates' in data:
            exam.preferred_dates = data['preferred_dates']
        if 'status' in data:
            exam.status = data['status']
        if 'department_id' in data:
            # Validate department exists
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({
                    'success': False,
                    'message': 'Department not found'
                }), 404
            exam.department_id = data['department_id']

        exam.updated_at = datetime.utcnow()
        db.session.commit()

        # Eğer sınav bilgileri değiştiyse, yeniden planlama yap
        schedule_fields = ['student_count', 'duration', 'needs_computer', 'preferred_dates']
        if any(field in data for field in schedule_fields):
            try:
                # Mevcut schedule'ı sil
                if exam.exam_schedule:
                    db.session.delete(exam.exam_schedule)
                    db.session.commit()

                # Yeniden planla
                auto_schedule_exam(exam)
                message = 'Sınav güncellendi ve yeniden planlandı'
            except Exception as e:
                print(f"Re-scheduling error: {str(e)}")
                message = 'Sınav güncellendi ancak yeniden planlama başarısız'
        else:
            message = 'Sınav güncellendi'

        return jsonify({
            'success': True,
            'message': message,
            'data': exam_schema.dump(exam)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    """Delete an exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        # Delete associated schedule if exists
        if exam.exam_schedule:
            db.session.delete(exam.exam_schedule)

        db.session.delete(exam)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Exam deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting exam: {str(e)}'
        }), 500
