from flask import Blueprint, request, jsonify
from database import db
from models import Settings, settings_schema, settings_list_schema
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings', methods=['GET'])
def get_all_settings():
    """Get all settings"""
    try:
        settings = Settings.query.all()
        return jsonify({
            'success': True,
            'data': settings_list_schema.dump(settings)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching settings: {str(e)}'
        }), 500

@settings_bp.route('/api/settings/<string:key>', methods=['GET'])
def get_setting(key):
    """Get a specific setting by key"""
    try:
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            return jsonify({
                'success': False,
                'message': 'Setting not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': settings_schema.dump(setting)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching setting: {str(e)}'
        }), 500

@settings_bp.route('/api/settings/exam-week', methods=['GET'])
def get_exam_week_settings():
    """Get exam week date range settings"""
    try:
        start_date_setting = Settings.query.filter_by(key='exam_week_start').first()
        end_date_setting = Settings.query.filter_by(key='exam_week_end').first()
        
        result = {
            'start_date': start_date_setting.value if start_date_setting else None,
            'end_date': end_date_setting.value if end_date_setting else None
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching exam week settings: {str(e)}'
        }), 500

@settings_bp.route('/api/settings/exam-week', methods=['POST'])
def save_exam_week_settings():
    """Save exam week date range settings"""
    try:
        data = request.get_json()
        
        if 'start_date' not in data or 'end_date' not in data:
            return jsonify({
                'success': False,
                'message': 'Both start_date and end_date are required'
            }), 400
        
        # Validate date format
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Validate date range
        if start_date >= end_date:
            return jsonify({
                'success': False,
                'message': 'Start date must be before end date'
            }), 400
        
        # Update or create start date setting
        start_setting = Settings.query.filter_by(key='exam_week_start').first()
        if start_setting:
            start_setting.value = data['start_date']
            start_setting.updated_at = datetime.utcnow()
        else:
            start_setting = Settings(key='exam_week_start', value=data['start_date'])
            db.session.add(start_setting)
        
        # Update or create end date setting
        end_setting = Settings.query.filter_by(key='exam_week_end').first()
        if end_setting:
            end_setting.value = data['end_date']
            end_setting.updated_at = datetime.utcnow()
        else:
            end_setting = Settings(key='exam_week_end', value=data['end_date'])
            db.session.add(end_setting)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Exam week settings saved successfully',
            'data': {
                'start_date': data['start_date'],
                'end_date': data['end_date']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving exam week settings: {str(e)}'
        }), 500

@settings_bp.route('/api/settings', methods=['POST'])
def create_or_update_setting():
    """Create or update a setting"""
    try:
        data = request.get_json()
        
        if 'key' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': 'Key and value are required'
            }), 400
        
        # Check if setting exists
        setting = Settings.query.filter_by(key=data['key']).first()
        
        if setting:
            # Update existing setting
            setting.value = data['value']
            setting.updated_at = datetime.utcnow()
            message = 'Setting updated successfully'
        else:
            # Create new setting
            setting = Settings(
                key=data['key'],
                value=data['value']
            )
            db.session.add(setting)
            message = 'Setting created successfully'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'data': settings_schema.dump(setting)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving setting: {str(e)}'
        }), 500

@settings_bp.route('/api/settings/<string:key>', methods=['DELETE'])
def delete_setting(key):
    """Delete a setting"""
    try:
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            return jsonify({
                'success': False,
                'message': 'Setting not found'
            }), 404
        
        db.session.delete(setting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Setting deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting setting: {str(e)}'
        }), 500
