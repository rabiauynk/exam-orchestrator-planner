#!/usr/bin/env python3
"""
Veritabanını temizleme scripti
"""

from database import db
from models import Exam, ExamSchedule, Room, Course, Department, Settings
from app import create_app

def clean_database():
    """Veritabanını temizle"""
    
    app = create_app()
    with app.app_context():
        print("=== Veritabanı Temizleme Başlıyor ===\n")
        
        try:
            # 1. Sınav programlarını sil
            schedules = ExamSchedule.query.all()
            print(f"Siliniyor: {len(schedules)} sınav programı")
            for schedule in schedules:
                db.session.delete(schedule)
            
            # 2. Sınavları sil
            exams = Exam.query.all()
            print(f"Siliniyor: {len(exams)} sınav")
            for exam in exams:
                db.session.delete(exam)
            
            # 3. Dersleri sil
            courses = Course.query.all()
            print(f"Siliniyor: {len(courses)} ders")
            for course in courses:
                db.session.delete(course)
            
            # 4. Sınıfları sil
            rooms = Room.query.all()
            print(f"Siliniyor: {len(rooms)} sınıf")
            for room in rooms:
                db.session.delete(room)
            
            # 5. Bölümleri sil (ayarları koruyalım)
            departments = Department.query.all()
            print(f"Siliniyor: {len(departments)} bölüm")
            for department in departments:
                db.session.delete(department)
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            print("\n=== Temizlik Tamamlandı ===")
            
            # Sonucu kontrol et
            print("\n=== Temizlik Sonrası Durum ===")
            print(f"Sınav sayısı: {Exam.query.count()}")
            print(f"Program sayısı: {ExamSchedule.query.count()}")
            print(f"Sınıf sayısı: {Room.query.count()}")
            print(f"Ders sayısı: {Course.query.count()}")
            print(f"Bölüm sayısı: {Department.query.count()}")
            
            # Ayarları kontrol et
            settings = Settings.query.all()
            print(f"Ayar sayısı: {len(settings)} (korundu)")
            for setting in settings:
                print(f"  {setting.key}: {setting.value}")
            
            print("\n✅ Veritabanı başarıyla temizlendi!")
            
        except Exception as e:
            print(f"\n❌ Hata oluştu: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    clean_database()
