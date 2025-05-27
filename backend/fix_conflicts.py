from app import create_app
from models import ExamSchedule, Exam
from database import db

app = create_app()

with app.app_context():
    print("=== ÇAKIşAN SINAVLARI TEMİZLEME ===")
    
    # Tüm sınavları sil ve yeniden planla
    print("Tüm sınav planlarını siliniyor...")
    ExamSchedule.query.delete()
    
    # Tüm sınavları pending durumuna al
    exams = Exam.query.all()
    for exam in exams:
        exam.status = 'pending'
    
    db.session.commit()
    
    print(f"Temizlendi: {len(exams)} sınav pending durumuna alındı")
    print("Şimdi yeni sınavlar ekleyerek otomatik planlamayı test edebilirsiniz.")
