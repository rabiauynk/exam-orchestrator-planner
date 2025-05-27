from app import create_app
from database import db
from models import Department, Course, Room, Settings

app = create_app()

with app.app_context():
    print("Adding sample data...")
    
    # Departments
    departments = [
        Department(name="Bilgisayar Mühendisliği", code="BM"),
        Department(name="Elektrik-Elektronik Mühendisliği", code="EE"),
        Department(name="Endüstri Mühendisliği", code="EM"),
        Department(name="Makine Mühendisliği", code="MM"),
        Department(name="İnşaat Mühendisliği", code="IM")
    ]
    
    for dept in departments:
        db.session.add(dept)
    db.session.commit()
    
    # Courses
    courses = [
        # Bilgisayar Mühendisliği
        Course(name="Programlama Temelleri", code="BM101", credits=4, class_level=1, department_id=1),
        Course(name="Matematik I", code="BM102", credits=3, class_level=1, department_id=1),
        Course(name="Veri Yapıları", code="BM201", credits=4, class_level=2, department_id=1),
        Course(name="Algoritma Analizi", code="BM202", credits=3, class_level=2, department_id=1),
        Course(name="Yazılım Mühendisliği", code="BM301", credits=4, class_level=3, department_id=1),
        Course(name="Veritabanı Sistemleri", code="BM302", credits=3, class_level=3, department_id=1),
        Course(name="Bitirme Projesi", code="BM401", credits=5, class_level=4, department_id=1),
        
        # Elektrik-Elektronik Mühendisliği
        Course(name="Devre Analizi", code="EE101", credits=4, class_level=1, department_id=2),
        Course(name="Elektronik I", code="EE201", credits=4, class_level=2, department_id=2),
        Course(name="Sinyal İşleme", code="EE301", credits=3, class_level=3, department_id=2),
        
        # Endüstri Mühendisliği
        Course(name="Endüstri Mühendisliğine Giriş", code="EM101", credits=3, class_level=1, department_id=3),
        Course(name="Üretim Planlama", code="EM201", credits=4, class_level=2, department_id=3),
        Course(name="Kalite Kontrol", code="EM301", credits=3, class_level=3, department_id=3)
    ]
    
    for course in courses:
        db.session.add(course)
    db.session.commit()
    
    # Rooms
    rooms = [
        # Bilgisayar Mühendisliği Sınıfları
        Room(name="BM-101", capacity=60, has_computer=False, department_id=1),
        Room(name="BM-102", capacity=50, has_computer=False, department_id=1),
        Room(name="BM-201", capacity=45, has_computer=True, department_id=1),
        Room(name="BM-Lab1", capacity=30, has_computer=True, department_id=1),
        Room(name="BM-Lab2", capacity=25, has_computer=True, department_id=1),
        
        # Endüstri Mühendisliği Sınıfları
        Room(name="EM-101", capacity=70, has_computer=False, department_id=3),
        Room(name="EM-102", capacity=65, has_computer=False, department_id=3),
        
        # Elektrik-Elektronik Mühendisliği Sınıfları
        Room(name="EE-101", capacity=55, has_computer=False, department_id=2),
        Room(name="EE-Lab1", capacity=35, has_computer=True, department_id=2),
        
        # Makine Mühendisliği Sınıfları
        Room(name="MM-101", capacity=60, has_computer=False, department_id=4),
        
        # İnşaat Mühendisliği Sınıfları
        Room(name="IM-101", capacity=75, has_computer=False, department_id=5)
    ]
    
    for room in rooms:
        db.session.add(room)
    db.session.commit()
    
    # Settings
    settings = [
        Settings(key="exam_week_start", value="2025-05-26"),
        Settings(key="exam_week_end", value="2025-06-20")
    ]
    
    for setting in settings:
        db.session.add(setting)
    db.session.commit()
    
    print("Sample data added successfully!")
    print(f"Departments: {len(departments)}")
    print(f"Courses: {len(courses)}")
    print(f"Rooms: {len(rooms)}")
    print(f"Settings: {len(settings)}")
