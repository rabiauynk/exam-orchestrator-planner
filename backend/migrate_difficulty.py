#!/usr/bin/env python3
"""
Migration script to add difficulty_level and available_rooms columns to exams table
"""

import os
import sys

from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from database import db, init_db
from flask import Flask


def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    init_db(app)
    return app


def migrate_database():
    """Add new columns to exams table"""
    try:
        # Check if columns already exist (MySQL version)
        result = db.session.execute(text("SHOW COLUMNS FROM exams"))
        columns = [row[0] for row in result.fetchall()]

        migrations_needed = []

        if 'difficulty_level' not in columns:
            migrations_needed.append(
                "ALTER TABLE exams ADD COLUMN difficulty_level VARCHAR(20) DEFAULT 'normal'"
            )

        if 'available_rooms' not in columns:
            migrations_needed.append(
                "ALTER TABLE exams ADD COLUMN available_rooms JSON"
            )

        if not migrations_needed:
            print("✅ Database is already up to date!")
            return True

        # Execute migrations
        for migration in migrations_needed:
            print(f"🔄 Executing: {migration}")
            db.session.execute(text(migration))

        db.session.commit()
        print("✅ Database migration completed successfully!")

        # Update existing exams with default difficulty levels
        update_existing_exams()

        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.session.rollback()
        return False


def update_existing_exams():
    """Update existing exams with difficulty levels based on course credits"""
    try:
        print("🔄 Updating existing exams with difficulty levels...")
        
        # Get all exams with their course information
        result = db.session.execute(text("""
            SELECT e.id, e.duration, c.class_level, c.credits
            FROM exams e
            JOIN courses c ON e.course_id = c.id
            WHERE e.difficulty_level = 'normal'
        """))
        
        exams = result.fetchall()
        updated_count = 0
        
        for exam in exams:
            exam_id, duration, class_level, credits = exam
            
            # Determine difficulty based on class level and duration
            difficulty = determine_difficulty(class_level, duration)
            
            # Update exam
            db.session.execute(text("""
                UPDATE exams 
                SET difficulty_level = :difficulty 
                WHERE id = :exam_id
            """), {'difficulty': difficulty, 'exam_id': exam_id})
            
            updated_count += 1
        
        db.session.commit()
        print(f"✅ Updated {updated_count} exams with difficulty levels")
        
    except Exception as e:
        print(f"❌ Failed to update existing exams: {str(e)}")
        db.session.rollback()


def determine_difficulty(class_level, duration):
    """Determine difficulty level based on class level and duration"""
    # Difficulty mapping based on duration and class level
    difficulty_mapping = {
        (1, 60): 'easy',      # 1st class, 60 min
        (1, 90): 'normal',    # 1st class, 90 min
        (1, 120): 'normal',   # 1st class, 120 min
        (2, 60): 'normal',    # 2nd class, 60 min
        (2, 90): 'normal',    # 2nd class, 90 min
        (2, 120): 'hard',     # 2nd class, 120 min
        (3, 60): 'normal',    # 3rd class, 60 min
        (3, 90): 'hard',      # 3rd class, 90 min
        (3, 120): 'hard',     # 3rd class, 120 min
        (4, 60): 'hard',      # 4th class, 60 min
        (4, 90): 'hard',      # 4th class, 90 min
        (4, 120): 'very_hard' # 4th class, 120 min
    }
    
    # First check exact mapping
    key = (class_level, duration)
    if key in difficulty_mapping:
        return difficulty_mapping[key]
    
    # Fallback logic for non-standard durations
    if class_level == 1:
        if duration <= 60:
            return 'easy'
        elif duration <= 90:
            return 'normal'
        else:
            return 'normal'
    elif class_level == 2:
        if duration <= 60:
            return 'normal'
        elif duration <= 90:
            return 'normal'
        else:
            return 'hard'
    elif class_level == 3:
        if duration <= 60:
            return 'normal'
        elif duration <= 90:
            return 'hard'
        else:
            return 'hard'
    else:  # class_level >= 4
        if duration <= 60:
            return 'hard'
        elif duration <= 90:
            return 'hard'
        else:
            return 'very_hard'


def main():
    """Main migration function"""
    print("🚀 Starting database migration...")
    
    app = create_app()
    
    with app.app_context():
        success = migrate_database()
        
        if success:
            print("🎉 Migration completed successfully!")
            return 0
        else:
            print("💥 Migration failed!")
            return 1


if __name__ == '__main__':
    exit(main())
