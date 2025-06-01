import os

from config import config
from database import db, init_db
from flask import Flask, jsonify
from flask_cors import CORS


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Initialize database
    db.init_app(app)
    # init_db(app)  # Temporarily disabled

    # Register blueprints
    from routes.course_routes import course_bp
    from routes.department_routes import department_bp
    from routes.exam_routes import exam_bp
    from routes.excel_routes import excel_bp
    from routes.export_routes import export_bp
    from routes.room_routes import room_bp
    from routes.schedule_routes import schedule_bp
    from routes.settings_routes import settings_bp

    app.register_blueprint(exam_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(excel_bp)
    app.register_blueprint(room_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request'
        }), 400

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'Exam Orchestrator API is running',
            'version': '1.0.0'
        }), 200

    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            'success': True,
            'message': 'Exam Orchestrator API',
            'version': '1.0.0',
            'endpoints': {
                'exams': '/api/exams',
                'schedule': '/api/schedule',
                'departments': '/api/departments',
                'settings': '/api/settings',
                'export': '/api/export',
                'health': '/api/health'
            }
        }), 200

    return app

if __name__ == '__main__':
    app = create_app()

    # Create uploads directory if it doesn't exist
    upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    print("Starting Exam Orchestrator API...")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"CORS Origins: {app.config['CORS_ORIGINS']}")

    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
