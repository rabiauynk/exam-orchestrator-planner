from flask import Blueprint, request, jsonify
from database import db
from models import Course, courses_schema, course_schema, Department

course_bp = Blueprint('courses', __name__)

@course_bp.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with optional filtering"""
    try:
        department_id = request.args.get('department_id')
        class_level = request.args.get('class_level')
        
        query = Course.query.filter_by(is_active=True)
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        if class_level:
            query = query.filter_by(class_level=int(class_level))
        
        courses = query.order_by(Course.class_level.asc(), Course.name.asc()).all()
        
        return jsonify({
            'success': True,
            'data': courses_schema.dump(courses)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching courses: {str(e)}'
        }), 500

@course_bp.route('/api/courses', methods=['POST'])
def create_course():
    """Create a new course"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'code', 'credits', 'class_level', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Check if course code already exists in the department
        existing_course = Course.query.filter_by(
            code=data['code'],
            department_id=data['department_id']
        ).first()
        if existing_course:
            return jsonify({
                'success': False,
                'message': 'Course code already exists in this department'
            }), 400
        
        # Create new course
        new_course = Course(
            name=data['name'],
            code=data['code'],
            credits=int(data['credits']),
            class_level=int(data['class_level']),
            department_id=data['department_id'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'data': course_schema.dump(new_course)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating course: {str(e)}'
        }), 500

@course_bp.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get a specific course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': course_schema.dump(course)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching course: {str(e)}'
        }), 500

@course_bp.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update a course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            course.name = data['name']
        if 'code' in data:
            # Check if new code already exists (excluding current course)
            existing_course = Course.query.filter(
                Course.code == data['code'],
                Course.department_id == course.department_id,
                Course.id != course_id
            ).first()
            if existing_course:
                return jsonify({
                    'success': False,
                    'message': 'Course code already exists in this department'
                }), 400
            course.code = data['code']
        if 'credits' in data:
            course.credits = int(data['credits'])
        if 'class_level' in data:
            course.class_level = int(data['class_level'])
        if 'is_active' in data:
            course.is_active = data['is_active']
        if 'department_id' in data:
            # Validate department exists
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({
                    'success': False,
                    'message': 'Department not found'
                }), 404
            course.department_id = data['department_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'data': course_schema.dump(course)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating course: {str(e)}'
        }), 500

@course_bp.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course (soft delete)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Check if course has exams
        if course.exams:
            return jsonify({
                'success': False,
                'message': 'Cannot delete course with existing exams. Deactivate instead.'
            }), 400
        
        # Soft delete - just deactivate
        course.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting course: {str(e)}'
        }), 500

@course_bp.route('/api/courses/by-department/<int:department_id>', methods=['GET'])
def get_courses_by_department(department_id):
    """Get courses by department and optionally by class level"""
    try:
        class_level = request.args.get('class_level')
        
        query = Course.query.filter_by(
            department_id=department_id,
            is_active=True
        )
        
        if class_level:
            query = query.filter_by(class_level=int(class_level))
        
        courses = query.order_by(Course.class_level.asc(), Course.name.asc()).all()
        
        return jsonify({
            'success': True,
            'data': courses_schema.dump(courses)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching courses: {str(e)}'
        }), 500

@course_bp.route('/api/courses/difficult', methods=['GET'])
def get_difficult_courses():
    """Get all difficult courses (credits >= 4)"""
    try:
        courses = Course.query.filter(
            Course.credits >= 4,
            Course.is_active == True
        ).order_by(Course.department_id.asc(), Course.class_level.asc()).all()
        
        return jsonify({
            'success': True,
            'data': courses_schema.dump(courses)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching difficult courses: {str(e)}'
        }), 500
