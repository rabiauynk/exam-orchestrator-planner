from flask import Blueprint, request, jsonify, send_file
from database import db
from models import ExamSchedule, Exam, Department, Room
from services.export_service import ExportService
import os
import tempfile

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export/excel', methods=['GET'])
def export_all_excel():
    """Export all departments' exam schedules to Excel"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Initialize export service
        export_service = ExportService()
        
        # Generate Excel file
        file_path = export_service.export_all_departments_excel(
            start_date=start_date,
            end_date=end_date
        )
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'Failed to generate Excel file'
            }), 500
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name='exam_schedule_all_departments.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting Excel: {str(e)}'
        }), 500

@export_bp.route('/api/export/excel/<int:department_id>', methods=['GET'])
def export_department_excel(department_id):
    """Export specific department's exam schedule to Excel"""
    try:
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Initialize export service
        export_service = ExportService()
        
        # Generate Excel file
        file_path = export_service.export_department_excel(
            department_id=department_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'Failed to generate Excel file'
            }), 500
        
        # Send file
        filename = f'exam_schedule_{department.code}.xlsx'
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting Excel: {str(e)}'
        }), 500

@export_bp.route('/api/export/departments-summary', methods=['GET'])
def get_departments_summary():
    """Get summary of all departments for export panel"""
    try:
        # Get all departments with exam counts
        departments = db.session.query(
            Department.id,
            Department.name,
            Department.code,
            db.func.count(Exam.id).label('exam_count'),
            db.func.max(Exam.updated_at).label('last_update')
        ).outerjoin(Exam).group_by(Department.id).all()
        
        result = []
        for dept in departments:
            result.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'exam_count': dept.exam_count or 0,
                'last_update': dept.last_update.strftime('%d/%m/%Y %H:%M') if dept.last_update else 'Henüz güncelleme yok'
            })
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching departments summary: {str(e)}'
        }), 500

@export_bp.route('/api/export/preview/<int:department_id>', methods=['GET'])
def preview_department_export(department_id):
    """Preview department export data"""
    try:
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = db.session.query(ExamSchedule).join(Exam).filter(
            Exam.department_id == department_id
        )
        
        if start_date:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(ExamSchedule.scheduled_date >= start_date_obj)
        
        if end_date:
            from datetime import datetime
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(ExamSchedule.scheduled_date <= end_date_obj)
        
        # Get schedules
        schedules = query.order_by(
            ExamSchedule.scheduled_date.asc(),
            ExamSchedule.start_time.asc()
        ).all()
        
        # Format data for preview
        preview_data = []
        for schedule in schedules:
            preview_data.append({
                'date': schedule.scheduled_date.strftime('%d/%m/%Y'),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'course_name': schedule.exam.course_name,
                'class_name': schedule.exam.class_name,
                'instructor': schedule.exam.instructor,
                'student_count': schedule.exam.student_count,
                'duration': schedule.exam.duration,
                'room_name': schedule.room.name,
                'needs_computer': 'Evet' if schedule.exam.needs_computer else 'Hayır'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'department': {
                    'id': department.id,
                    'name': department.name,
                    'code': department.code
                },
                'schedules': preview_data,
                'total_count': len(preview_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error previewing export data: {str(e)}'
        }), 500
