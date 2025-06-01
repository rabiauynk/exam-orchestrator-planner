from flask import Blueprint, jsonify, request
from database import db
from models import Room, Department, room_schema, rooms_schema

room_bp = Blueprint('room', __name__)

@room_bp.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms"""
    try:
        department_id = request.args.get('department_id')
        
        if department_id:
            rooms = Room.query.filter_by(department_id=department_id, is_active=True).all()
        else:
            rooms = Room.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'data': rooms_schema.dump(rooms)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching rooms: {str(e)}'
        }), 500

@room_bp.route('/api/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'capacity', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404
        
        # Check if room name already exists in department
        existing_room = Room.query.filter_by(
            name=data['name'],
            department_id=data['department_id']
        ).first()
        
        if existing_room:
            return jsonify({
                'success': False,
                'message': 'Room with this name already exists in the department'
            }), 400
        
        # Create room
        room = Room(
            name=data['name'],
            capacity=int(data['capacity']),
            has_computer=data.get('has_computer', False),
            department_id=data['department_id'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(room)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room created successfully',
            'data': room_schema.dump(room)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating room: {str(e)}'
        }), 500

@room_bp.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """Update a room"""
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            room.name = data['name']
        if 'capacity' in data:
            room.capacity = int(data['capacity'])
        if 'has_computer' in data:
            room.has_computer = data['has_computer']
        if 'is_active' in data:
            room.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room updated successfully',
            'data': room_schema.dump(room)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating room: {str(e)}'
        }), 500

@room_bp.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room (soft delete)"""
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        # Soft delete
        room.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting room: {str(e)}'
        }), 500
