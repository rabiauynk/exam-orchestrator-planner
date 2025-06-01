#!/usr/bin/env python3
"""
Add exam_session_id column to exams table
"""

from database import db
from app import create_app
import sqlalchemy as sa

def add_session_column():
    """Add exam_session_id column to exams table"""
    
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            inspector = sa.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('exams')]
            
            if 'exam_session_id' in columns:
                print('✅ exam_session_id column already exists')
                return
            
            # Add the column
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE exams ADD COLUMN exam_session_id VARCHAR(50)'))
                conn.commit()
            
            print('✅ exam_session_id column added successfully')
            
        except Exception as e:
            print(f'❌ Error: {e}')

if __name__ == "__main__":
    add_session_column()
