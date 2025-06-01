from datetime import datetime

from database import db, ma
from marshmallow import fields


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    exams = db.relationship('Exam', backref='department', lazy=True)
    rooms = db.relationship('Room', backref='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    class_level = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    exams = db.relationship('Exam', backref='course', lazy=True, foreign_keys='Exam.course_id')

    @property
    def is_difficult(self):
        """Check if course is difficult (credits >= 4)"""
        return self.credits >= 4

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    has_computer = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    exam_schedules = db.relationship('ExamSchedule', backref='room', lazy=True)

class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    student_count = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    needs_computer = db.Column(db.Boolean, default=False)
    preferred_dates = db.Column(db.JSON)  # Store as JSON array
    status = db.Column(db.String(20), default='pending')  # pending, planned, completed
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    difficulty_level = db.Column(db.String(20), default='normal')  # easy, normal, hard, very_hard
    available_rooms = db.Column(db.JSON)  # Store as JSON array - rooms this department can use
    exam_session_id = db.Column(db.String(50), nullable=True)  # To group exams by upload session
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exam_schedules = db.relationship('ExamSchedule', backref='exam', lazy=True)

    @property
    def is_difficult(self):
        """Check if exam is difficult (credits >= 4)"""
        return self.course.credits >= 4

    @property
    def course_name(self):
        """Get course name from related course"""
        return self.course.name if self.course else ""

    @property
    def class_name(self):
        """Get class level from related course"""
        return str(self.course.class_level) if self.course else ""

    @property
    def credits(self):
        """Get credits from related course"""
        return self.course.credits if self.course else 3

class ExamSchedule(db.Model):
    __tablename__ = 'exam_schedules'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    additional_rooms = db.Column(db.JSON, nullable=True)  # Store additional room IDs as JSON array
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Marshmallow Schemas for serialization
class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True

class CourseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        load_instance = True
        include_fk = True

    department = fields.Nested(DepartmentSchema, only=['id', 'name', 'code'])

class RoomSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Room
        load_instance = True
        include_fk = True

    department = fields.Nested(DepartmentSchema, only=['id', 'name', 'code'])

class ExamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Exam
        load_instance = True
        include_fk = True

    department = fields.Nested(DepartmentSchema, only=['id', 'name', 'code'])
    course = fields.Nested(CourseSchema, only=['id', 'name', 'code', 'credits', 'class_level'])
    exam_schedules = fields.Nested('ExamScheduleSchema', many=True, exclude=['exam'])

    # Add computed fields
    course_name = fields.Method("get_course_name")
    class_name = fields.Method("get_class_name")
    credits = fields.Method("get_credits")

    def get_course_name(self, obj):
        return obj.course_name

    def get_class_name(self, obj):
        return obj.class_name

    def get_credits(self, obj):
        return obj.credits

class ExamScheduleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExamSchedule
        load_instance = True
        include_fk = True

    exam = fields.Nested(ExamSchema, exclude=['exam_schedule'])
    room = fields.Nested(RoomSchema)
    additional_rooms = fields.Raw()  # Include JSON field as-is
    additional_room_details = fields.Method("get_additional_room_details")

    def get_additional_room_details(self, obj):
        """Get detailed information about additional rooms"""
        if not obj.additional_rooms:
            return []

        room_details = []
        for room_id in obj.additional_rooms:
            room = Room.query.get(room_id)
            if room:
                room_details.append({
                    'id': room.id,
                    'name': room.name,
                    'capacity': room.capacity,
                    'has_computer': room.has_computer
                })
        return room_details

class SettingsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Settings
        load_instance = True

# Initialize schemas
department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)

exam_schema = ExamSchema()
exams_schema = ExamSchema(many=True)

exam_schedule_schema = ExamScheduleSchema()
exam_schedules_schema = ExamScheduleSchema(many=True)

settings_schema = SettingsSchema()
settings_list_schema = SettingsSchema(many=True)
