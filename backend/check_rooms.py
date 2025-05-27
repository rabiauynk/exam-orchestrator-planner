from app import create_app
from models import Room

app = create_app()
with app.app_context():
    rooms = Room.query.all()
    print("=== SINIF KAPASİTELERİ ===")
    for room in rooms:
        print(f"Sınıf: {room.name}")
        print(f"  Kapasite: {room.capacity}")
        print(f"  Bilgisayar: {'Evet' if room.has_computer else 'Hayır'}")
        print(f"  Aktif: {'Evet' if room.is_active else 'Hayır'}")
        print("---")
