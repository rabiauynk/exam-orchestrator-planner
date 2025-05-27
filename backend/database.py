from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()

def init_db(app):
    """Initialize database with Flask app"""
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
    if not hasattr(app, 'extensions') or 'flask-marshmallow' not in app.extensions:
        ma.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Insert default data if tables are empty
        from models import Course, Department, Room, Settings

        # Add default departments if none exist
        if Department.query.count() == 0:
            departments = [
                Department(name="Bilgisayar Mühendisliği", code="BM"),
                Department(name="Endüstri Mühendisliği", code="EM"),
                Department(name="Elektrik-Elektronik Mühendisliği", code="EE"),
                Department(name="Makine Mühendisliği", code="MM"),
                Department(name="İnşaat Mühendisliği", code="IM")
            ]
            for dept in departments:
                db.session.add(dept)

        # Add default rooms if none exist
        if Room.query.count() == 0:
            rooms = [
                Room(name="BM-101", capacity=60, has_computer=False, department_id=1),
                Room(name="BM-102", capacity=50, has_computer=False, department_id=1),
                Room(name="BM-201", capacity=45, has_computer=True, department_id=1),
                Room(name="BM-Lab1", capacity=30, has_computer=True, department_id=1),
                Room(name="BM-Lab2", capacity=25, has_computer=True, department_id=1),
                Room(name="EM-101", capacity=70, has_computer=False, department_id=2),
                Room(name="EM-102", capacity=65, has_computer=False, department_id=2),
                Room(name="EE-101", capacity=55, has_computer=False, department_id=3),
                Room(name="EE-Lab1", capacity=35, has_computer=True, department_id=3),
                Room(name="MM-101", capacity=60, has_computer=False, department_id=4),
                Room(name="IM-101", capacity=75, has_computer=False, department_id=5)
            ]
            for room in rooms:
                db.session.add(room)

        # Add default settings if none exist
        if Settings.query.count() == 0:
            default_settings = Settings(
                key="exam_week_start",
                value="2024-01-15"
            )
            db.session.add(default_settings)

            default_settings2 = Settings(
                key="exam_week_end",
                value="2024-01-26"
            )
            db.session.add(default_settings2)

        # Add default courses if none exist
        if Course.query.count() == 0:
            courses = [
                # Bilgisayar Mühendisliği - 1. Sınıf
                Course(name="Matematik I", code="BM101", credits=4, class_level=1, department_id=1),
                Course(name="Fizik I", code="BM102", credits=3, class_level=1, department_id=1),
                Course(name="Programlama Temelleri", code="BM103", credits=3, class_level=1, department_id=1),
                Course(name="Mühendislik Temelleri", code="BM104", credits=2, class_level=1, department_id=1),

                # Bilgisayar Mühendisliği - 2. Sınıf
                Course(name="Veri Yapıları ve Algoritmalar", code="BM201", credits=4, class_level=2, department_id=1),
                Course(name="Nesne Yönelimli Programlama", code="BM202", credits=3, class_level=2, department_id=1),
                Course(name="Matematik II", code="BM203", credits=4, class_level=2, department_id=1),
                Course(name="Veritabanı Sistemleri", code="BM204", credits=3, class_level=2, department_id=1),

                # Bilgisayar Mühendisliği - 3. Sınıf
                Course(name="Yazılım Mühendisliği", code="BM301", credits=3, class_level=3, department_id=1),
                Course(name="İşletim Sistemleri", code="BM302", credits=4, class_level=3, department_id=1),
                Course(name="Bilgisayar Ağları", code="BM303", credits=3, class_level=3, department_id=1),
                Course(name="Web Programlama", code="BM304", credits=3, class_level=3, department_id=1),

                # Endüstri Mühendisliği - 1. Sınıf
                Course(name="Calculus I", code="EM101", credits=5, class_level=1, department_id=2),
                Course(name="Fizik I", code="EM102", credits=3, class_level=1, department_id=2),
                Course(name="Kimya I", code="EM103", credits=3, class_level=1, department_id=2),
                Course(name="Mühendislik Çizimi", code="EM104", credits=2, class_level=1, department_id=2),

                # Endüstri Mühendisliği - 2. Sınıf
                Course(name="İstatistik", code="EM201", credits=3, class_level=2, department_id=2),
                Course(name="Üretim Yöntemleri", code="EM202", credits=4, class_level=2, department_id=2),
                Course(name="Malzeme Bilimi", code="EM203", credits=3, class_level=2, department_id=2),
                Course(name="Calculus II", code="EM204", credits=5, class_level=2, department_id=2),

                # Elektrik-Elektronik Mühendisliği - 2. Sınıf
                Course(name="Devre Analizi", code="EE201", credits=4, class_level=2, department_id=3),
                Course(name="Elektronik I", code="EE202", credits=3, class_level=2, department_id=3),
                Course(name="Sinyal ve Sistemler", code="EE203", credits=4, class_level=2, department_id=3),

                # Elektrik-Elektronik Mühendisliği - 3. Sınıf
                Course(name="Mikroişlemciler", code="EE301", credits=4, class_level=3, department_id=3),
                Course(name="Kontrol Sistemleri", code="EE302", credits=4, class_level=3, department_id=3),
                Course(name="Güç Elektroniği", code="EE303", credits=3, class_level=3, department_id=3),
            ]
            for course in courses:
                db.session.add(course)

        db.session.commit()
        print("Database initialized successfully!")

def reset_db(app):
    """Reset database - drop and recreate all tables"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")
