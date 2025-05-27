import json
import random
from datetime import datetime, time

from database import db
from flask import Blueprint, jsonify, request
from models import (Department, Exam, ExamSchedule, Room, exam_schema,
                    exams_schema)

exam_bp = Blueprint('exams', __name__)

def auto_schedule_exam(exam):
    """Gelişmiş otomatik planlama - çoklu sınıf desteği ile"""
    try:
        # Tercih edilen tarihlerden birini seç
        preferred_dates = exam.preferred_dates
        if not preferred_dates:
            return False

        # Uygun sınıfları bul
        available_rooms = Room.query.filter_by(is_active=True).all()
        if not available_rooms:
            return False

        # Bilgisayar ihtiyacına göre sınıf filtrele
        suitable_rooms = []
        for room in available_rooms:
            # Bilgisayar ihtiyacı kontrolü
            if exam.needs_computer and not room.has_computer:
                continue
            suitable_rooms.append(room)

        if not suitable_rooms:
            print(f"No suitable rooms found for exam {exam.id} (needs_computer: {exam.needs_computer})")
            return False

        # Tek sınıfta sığıp sığmadığını kontrol et
        max_capacity = max(room.capacity for room in suitable_rooms)
        if exam.student_count <= max_capacity:
            # Tek sınıfta sığıyor, normal planlama yap
            return schedule_single_room(exam, suitable_rooms, preferred_dates)
        else:
            # Çoklu sınıf gerekiyor
            return schedule_multiple_rooms(exam, suitable_rooms, preferred_dates)

    except Exception as e:
        print(f"Auto-scheduling error: {str(e)}")
        db.session.rollback()
        return False

def schedule_single_room(exam, suitable_rooms, preferred_dates):
    """Tek sınıfta sığan sınavlar için planlama"""
    # Kapasiteye göre uygun sınıfları filtrele
    capacity_suitable_rooms = [r for r in suitable_rooms if r.capacity >= exam.student_count]

    if not capacity_suitable_rooms:
        print(f"No rooms with sufficient capacity for exam {exam.id} (student_count: {exam.student_count})")
        return False

    # Zaman aralıkları
    time_slots = [
        ('09:00', '11:00'),
        ('11:00', '13:00'),
        ('13:00', '15:00'),
        ('15:00', '17:00')
    ]

    # Her tercih tarihini dene
    for preferred_date in preferred_dates:
        # Her zaman slotunu dene
        for start_time, _ in time_slots:
            # Süreye göre gerçek bitiş saatini hesapla
            start_hour, start_minute = map(int, start_time.split(':'))
            duration_hours = exam.duration // 60
            duration_minutes = exam.duration % 60

            end_hour = start_hour + duration_hours
            end_minute = start_minute + duration_minutes
            if end_minute >= 60:
                end_hour += 1
                end_minute -= 60

            # Saat 17:00'yi geçmesin
            if end_hour > 17:
                continue

            calculated_end_time = f"{end_hour:02d}:{end_minute:02d}"

            # Sınıfları kapasiteye göre sırala (en küçük uygun sınıf önce)
            sorted_rooms = sorted(capacity_suitable_rooms, key=lambda r: r.capacity)

            # Bu tarih/saatte kullanılan sınıfları bul
            existing_schedules = ExamSchedule.query.filter(
                ExamSchedule.scheduled_date == preferred_date,
                db.or_(
                    db.and_(
                        ExamSchedule.start_time <= start_time,
                        ExamSchedule.end_time > start_time
                    ),
                    db.and_(
                        ExamSchedule.start_time < calculated_end_time,
                        ExamSchedule.end_time >= calculated_end_time
                    ),
                    db.and_(
                        ExamSchedule.start_time >= start_time,
                        ExamSchedule.end_time <= calculated_end_time
                    )
                )
            ).all()

            occupied_room_ids = [schedule.room_id for schedule in existing_schedules]

            # Her uygun sınıfı dene
            for room in sorted_rooms:
                # Bu sınıf o tarih/saatte kullanılıyor mu?
                if room.id not in occupied_room_ids:
                    # Çakışma yok, bu slot'u kullan
                    schedule = ExamSchedule(
                        exam_id=exam.id,
                        room_id=room.id,
                        scheduled_date=preferred_date,
                        start_time=start_time,
                        end_time=calculated_end_time
                    )

                    exam.status = 'planned'
                    db.session.add(schedule)
                    db.session.commit()

                    print(f"Exam {exam.id} scheduled: {preferred_date} {start_time}-{calculated_end_time} in room {room.name} (capacity: {room.capacity}, students: {exam.student_count})")
                    return True

    print(f"No available slot found for exam {exam.id}")
    return False

def schedule_multiple_rooms(exam, suitable_rooms, preferred_dates):
    """Çoklu sınıf gerektiren sınavlar için planlama"""
    print(f"Exam {exam.id} requires multiple rooms (students: {exam.student_count})")

    # Zaman aralıkları
    time_slots = [
        ('09:00', '11:00'),
        ('11:00', '13:00'),
        ('13:00', '15:00'),
        ('15:00', '17:00')
    ]

    # Her tercih tarihini dene
    for preferred_date in preferred_dates:
        # Her zaman slotunu dene
        for start_time, _ in time_slots:
            # Süreye göre gerçek bitiş saatini hesapla
            start_hour, start_minute = map(int, start_time.split(':'))
            duration_hours = exam.duration // 60
            duration_minutes = exam.duration % 60

            end_hour = start_hour + duration_hours
            end_minute = start_minute + duration_minutes
            if end_minute >= 60:
                end_hour += 1
                end_minute -= 60

            # Saat 17:00'yi geçmesin
            if end_hour > 17:
                continue

            calculated_end_time = f"{end_hour:02d}:{end_minute:02d}"

            # Bu tarih/saatte uygun sınıfları bul
            available_rooms_for_slot = []

            # Önce bu tarih/saatte başka sınavlar var mı kontrol et
            existing_schedules = ExamSchedule.query.filter(
                ExamSchedule.scheduled_date == preferred_date,
                db.or_(
                    db.and_(
                        ExamSchedule.start_time <= start_time,
                        ExamSchedule.end_time > start_time
                    ),
                    db.and_(
                        ExamSchedule.start_time < calculated_end_time,
                        ExamSchedule.end_time >= calculated_end_time
                    ),
                    db.and_(
                        ExamSchedule.start_time >= start_time,
                        ExamSchedule.end_time <= calculated_end_time
                    )
                )
            ).all()

            # Kullanılan sınıfları listele
            occupied_room_ids = [schedule.room_id for schedule in existing_schedules]

            for room in suitable_rooms:
                # Bu sınıf o tarih/saatte kullanılıyor mu?
                if room.id not in occupied_room_ids:
                    available_rooms_for_slot.append(room)

            # Toplam kapasiteyi hesapla
            total_capacity = sum(room.capacity for room in available_rooms_for_slot)

            if total_capacity >= exam.student_count:
                # Yeterli kapasite var, sınıfları ata
                remaining_students = exam.student_count
                assigned_rooms = []

                # Büyük sınıflardan başla
                sorted_rooms = sorted(available_rooms_for_slot, key=lambda r: r.capacity, reverse=True)

                for room in sorted_rooms:
                    if remaining_students <= 0:
                        break

                    students_in_room = min(room.capacity, remaining_students)
                    assigned_rooms.append((room, students_in_room))
                    remaining_students -= students_in_room

                # Tüm sınıfları ata
                for room, students_in_room in assigned_rooms:
                    schedule = ExamSchedule(
                        exam_id=exam.id,
                        room_id=room.id,
                        scheduled_date=preferred_date,
                        start_time=start_time,
                        end_time=calculated_end_time
                    )
                    db.session.add(schedule)

                exam.status = 'planned'
                db.session.commit()

                room_info = ", ".join([f"{room.name}({students})" for room, students in assigned_rooms])
                print(f"Exam {exam.id} scheduled in multiple rooms: {preferred_date} {start_time}-{calculated_end_time} - {room_info}")
                return True

    print(f"No available slots found for multi-room exam {exam.id}")
    return False

@exam_bp.route('/api/exams', methods=['GET'])
def get_exams():
    """Get all exams"""
    try:
        exams = Exam.query.all()
        return jsonify({
            'success': True,
            'data': exams_schema.dump(exams)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching exams: {str(e)}'
        }), 500

@exam_bp.route('/api/exams', methods=['POST'])
def create_exam():
    """Create a new exam"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'instructor', 'student_count', 'duration', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate course exists
        from models import Course
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404

        # Validate department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found'
            }), 404

        # Process preferred dates
        preferred_dates = data.get('preferred_dates', [])
        if isinstance(preferred_dates, list) and len(preferred_dates) > 0:
            # Convert date strings to proper format if needed
            processed_dates = []
            for date_str in preferred_dates:
                if isinstance(date_str, str):
                    try:
                        # Try to parse different date formats
                        if 'T' in date_str:  # ISO format
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:  # Assume DD/MM/YYYY format
                            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        processed_dates.append(date_obj.strftime('%Y-%m-%d'))
                    except ValueError:
                        processed_dates.append(date_str)
                else:
                    processed_dates.append(date_str)
            preferred_dates = processed_dates

        # Create new exam
        new_exam = Exam(
            course_id=data['course_id'],
            instructor=data['instructor'],
            student_count=int(data['student_count']),
            duration=int(data['duration']),
            needs_computer=data.get('needs_computer', False),
            preferred_dates=preferred_dates,
            department_id=data['department_id'],
            status='pending'
        )

        db.session.add(new_exam)
        db.session.commit()

        # Otomatik planlama yap
        try:
            auto_schedule_exam(new_exam)
            message = 'Sınav eklendi ve otomatik olarak planlandı'
        except Exception as e:
            print(f"Auto-scheduling error: {str(e)}")
            message = 'Sınav eklendi ancak otomatik planlama başarısız'

        return jsonify({
            'success': True,
            'message': message,
            'data': exam_schema.dump(new_exam)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    """Get a specific exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        return jsonify({
            'success': True,
            'data': exam_schema.dump(exam)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    """Update an exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        data = request.get_json()

        # Update fields if provided
        if 'course_id' in data:
            # Validate course exists
            from models import Course
            course = Course.query.get(data['course_id'])
            if not course:
                return jsonify({
                    'success': False,
                    'message': 'Course not found'
                }), 404
            exam.course_id = data['course_id']
        if 'instructor' in data:
            exam.instructor = data['instructor']
        if 'student_count' in data:
            exam.student_count = int(data['student_count'])
        if 'duration' in data:
            exam.duration = int(data['duration'])
        if 'needs_computer' in data:
            exam.needs_computer = data['needs_computer']
        if 'preferred_dates' in data:
            exam.preferred_dates = data['preferred_dates']
        if 'status' in data:
            exam.status = data['status']
        if 'department_id' in data:
            # Validate department exists
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({
                    'success': False,
                    'message': 'Department not found'
                }), 404
            exam.department_id = data['department_id']

        exam.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Exam updated successfully',
            'data': exam_schema.dump(exam)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating exam: {str(e)}'
        }), 500

@exam_bp.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    """Delete an exam"""
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({
                'success': False,
                'message': 'Exam not found'
            }), 404

        # Delete associated schedule if exists
        if exam.exam_schedule:
            db.session.delete(exam.exam_schedule)

        db.session.delete(exam)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Exam deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting exam: {str(e)}'
        }), 500
