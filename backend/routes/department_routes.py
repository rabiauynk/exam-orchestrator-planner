from flask import Blueprint, request, jsonify
from database import db
from models import Department, departments_schema, department_schema

department_bp = Blueprint('departments', __name__)

@department_bp.route('/api/departments', methods=['GET'])
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'data': departments_schema.dump(departments)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching departments: {str(e)}'
        }), 500

@department_bp.route('/api/departments', methods=['POST'])
def create_department():
    """Create a new department"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data or 'code' not in data:
            return jsonify({
                'success': False,
                'message': 'Name and code are required'
            }), 400
        
        # Check if code already exists
        existing_dept = Department.query.filter_by(code=data['code']).first()
        if existing_dept:
            return jsonify({
                'success': False,
                'message': 'Department code already exists'
            }), 400
        
        # Create new department
        new_department = Department(
            name=data['name'],
            code=data['code']
        )
        
        db.session.add(new_department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'data': department_schema.dump(new_department)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating department: {str(e)}'
        }), 500

@department_bp.route('/api/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """Get a specific department"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': department_schema.dump(department)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching department: {str(e)}'
        }), 500

@department_bp.route('/api/departments/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    """Update a department"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            department.name = data['name']
        if 'code' in data:
            # Check if new code already exists (excluding current department)
            existing_dept = Department.query.filter(
                Department.code == data['code'],
                Department.id != department_id
            ).first()
            if existing_dept:
                return jsonify({
                    'success': False,
                    'message': 'Department code already exists'
                }), 400
            department.code = data['code']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department updated successfully',
            'data': department_schema.dump(department)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating department: {str(e)}'
        }), 500

@department_bp.route('/api/departments/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    """Delete a department"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Check if department has exams
        if department.exams:
            return jsonify({
                'success': False,
                'message': 'Cannot delete department with existing exams'
            }), 400
        
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting department: {str(e)}'
        }), 500
