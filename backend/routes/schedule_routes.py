from flask import Blueprint, request, jsonify
from database import db
from models import ExamSchedule, Exam, Room, exam_schedules_schema, exam_schedule_schema
from services.scheduler_service import SchedulerService
from datetime import datetime, date

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get all scheduled exams"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department_id = request.args.get('department_id')
        
        query = ExamSchedule.query
        
        # Apply filters
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(ExamSchedule.scheduled_date >= start_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(ExamSchedule.scheduled_date <= end_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }), 400
        
        if department_id:
            query = query.join(Exam).filter(Exam.department_id == department_id)
        
        # Order by date and time
        schedules = query.order_by(
            ExamSchedule.scheduled_date.asc(),
            ExamSchedule.start_time.asc()
        ).all()
        
        # Group by date for frontend
        grouped_schedule = {}
        for schedule in schedules:
            date_str = schedule.scheduled_date.strftime('%d/%m/%Y')
            if date_str not in grouped_schedule:
                grouped_schedule[date_str] = []
            
            schedule_data = exam_schedule_schema.dump(schedule)
            grouped_schedule[date_str].append(schedule_data)
        
        # Convert to list format expected by frontend
        result = []
        for date_str, time_slots in grouped_schedule.items():
            result.append({
                'date': date_str,
                'timeSlots': time_slots
            })
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching schedule: {str(e)}'
        }), 500

@schedule_bp.route('/api/schedule/generate', methods=['POST'])
def generate_schedule():
    """Generate automatic schedule for pending exams"""
    try:
        data = request.get_json() or {}
        
        # Get parameters
        force_regenerate = data.get('force_regenerate', False)
        department_id = data.get('department_id')
        
        # Initialize scheduler service
        scheduler = SchedulerService()
        
        # Generate schedule
        result = scheduler.generate_schedule(
            force_regenerate=force_regenerate,
            department_id=department_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': {
                    'scheduled_count': result['scheduled_count'],
                    'failed_count': result['failed_count'],
                    'failed_exams': result['failed_exams']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating schedule: {str(e)}'
        }), 500

@schedule_bp.route('/api/schedule/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update a specific schedule"""
    try:
        schedule = ExamSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'message': 'Schedule not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'room_id' in data:
            room = Room.query.get(data['room_id'])
            if not room:
                return jsonify({
                    'success': False,
                    'message': 'Room not found'
                }), 404
            schedule.room_id = data['room_id']
        
        if 'scheduled_date' in data:
            try:
                schedule.scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        if 'start_time' in data:
            try:
                schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_time format. Use HH:MM'
                }), 400
        
        if 'end_time' in data:
            try:
                schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_time format. Use HH:MM'
                }), 400
        
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule updated successfully',
            'data': exam_schedule_schema.dump(schedule)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating schedule: {str(e)}'
        }), 500

@schedule_bp.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a specific schedule"""
    try:
        schedule = ExamSchedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'message': 'Schedule not found'
            }), 404
        
        # Update exam status back to pending
        exam = schedule.exam
        exam.status = 'pending'
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting schedule: {str(e)}'
        }), 500
