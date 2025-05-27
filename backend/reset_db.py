from app import create_app
from database import db
from models import Department, Course, Room, Exam, ExamSchedule, Settings

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables...")
    db.create_all()
    
    print("Database reset complete!")
    print("Please run init_data.py to populate with sample data.")
