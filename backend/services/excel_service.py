import re
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
from database import db
from flask import current_app
from models import Course, Department, Exam, Room


class ExcelService:
    """Service for processing Excel files and creating exams"""
    
    def __init__(self):
        self.required_columns = [
            'Sınıf Seviyesi',
            'Ders Kodu',
            'Ders Adı',
            'Öğretim Üyesi',
            'Öğrenci Sayısı',
            'Sınav Süresi (dakika)',
            'Sınav Zorluğu',
            'Tercih 1',
            'Tercih 2',
            'Tercih 3',
            'Bilgisayar Gerekli mi?',
            'Kullanılabilir Derslikler'
        ]

    
    def process_excel_file(self, file_path: str, department_id: int, session_id: str = None) -> Dict[str, Any]:
        """Process Excel file and create exams"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Validate columns
            validation_result = self._validate_columns(df)
            if not validation_result['valid']:
                return validation_result
            
            # Process each row
            results = {
                'success': True,
                'total_rows': len(df),
                'processed': 0,
                'failed': 0,
                'errors': [],
                'created_exams': []
            }
            
            for index, row in df.iterrows():
                try:
                    print(f"DEBUG: Processing row {index + 1}: {dict(row)}")
                    exam_data = self._process_row(row, department_id, index + 1, session_id)
                    if exam_data:
                        print(f"DEBUG: Creating exam for {exam_data['_course_code']}")
                        exam = self._create_exam(exam_data)
                        results['created_exams'].append({
                            'id': exam.id,
                            'course_code': exam_data['_course_code'],
                            'instructor': exam_data['instructor'],
                            'difficulty': exam_data['difficulty_level']
                        })
                        results['processed'] += 1
                        print(f"DEBUG: Successfully processed exam {exam.id}")
                    else:
                        results['failed'] += 1
                        print(f"DEBUG: No exam data returned for row {index + 1}")

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Row {index + 1}: {str(e)}")
                    print(f"DEBUG: Error processing row {index + 1}: {str(e)}")
                    import traceback
                    print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Excel processing error: {str(e)}'
            }
    
    def _validate_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate Excel columns and data"""
        # Check for missing columns
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)

        if missing_columns:
            return {
                'success': False,
                'valid': False,
                'message': f'❌ Eksik sütunlar: {", ".join(missing_columns)}',
                'details': f'Excel dosyanızda şu sütunlar eksik: {", ".join(missing_columns)}. Lütfen template dosyasını indirip doğru formatı kullanın.'
            }

        # Check if file is empty
        if len(df) == 0:
            return {
                'success': False,
                'valid': False,
                'message': '❌ Excel dosyası boş!',
                'details': 'Excel dosyanızda hiç veri yok. Lütfen sınav verilerini ekleyip tekrar deneyin.'
            }

        # Check for extra columns (warning)
        extra_columns = [col for col in df.columns if col not in self.required_columns]
        warnings = []
        if extra_columns:
            warnings.append(f'⚠️ Fazla sütunlar göz ardı edilecek: {", ".join(extra_columns)}')

        # Basic data validation
        errors = []
        for index, row in df.iterrows():
            row_num = index + 1

            # Check for empty critical fields
            if pd.isna(row.get('Ders Kodu', '')) or str(row.get('Ders Kodu', '')).strip() == '':
                errors.append(f'Satır {row_num}: Ders Kodu boş olamaz')

            if pd.isna(row.get('Ders Adı', '')) or str(row.get('Ders Adı', '')).strip() == '':
                errors.append(f'Satır {row_num}: Ders Adı boş olamaz')

            if pd.isna(row.get('Öğretim Üyesi', '')) or str(row.get('Öğretim Üyesi', '')).strip() == '':
                errors.append(f'Satır {row_num}: Öğretim Üyesi boş olamaz')

            # Check difficulty level
            difficulty_input = str(row.get('Sınav Zorluğu', '')).strip().lower()
            valid_difficulties = ['kolay', 'orta', 'zor', 'easy', 'normal', 'hard', 'medium']
            if not difficulty_input or difficulty_input not in valid_difficulties:
                errors.append(f'Satır {row_num}: Sınav Zorluğu "Kolay", "Orta" veya "Zor" olmalı')

            # Check numeric fields
            try:
                class_level = int(row.get('Sınıf Seviyesi', 0))
                if class_level < 1 or class_level > 4:
                    errors.append(f'Satır {row_num}: Sınıf Seviyesi 1-4 arasında olmalı')
            except (ValueError, TypeError):
                errors.append(f'Satır {row_num}: Sınıf Seviyesi sayı olmalı')

            try:
                student_count = int(row.get('Öğrenci Sayısı', 0))
                if student_count <= 0:
                    errors.append(f'Satır {row_num}: Öğrenci Sayısı 0\'dan büyük olmalı')
            except (ValueError, TypeError):
                errors.append(f'Satır {row_num}: Öğrenci Sayısı sayı olmalı')

            try:
                duration = int(row.get('Sınav Süresi (dakika)', 0))
                if duration <= 0:
                    errors.append(f'Satır {row_num}: Sınav Süresi 0\'dan büyük olmalı')
            except (ValueError, TypeError):
                errors.append(f'Satır {row_num}: Sınav Süresi sayı olmalı')

        if errors:
            return {
                'success': False,
                'valid': False,
                'message': f'❌ {len(errors)} veri hatası bulundu',
                'details': '\n'.join(errors[:10]) + ('\n... ve daha fazlası' if len(errors) > 10 else ''),
                'warnings': warnings
            }

        return {
            'valid': True,
            'warnings': warnings
        }
    
    def _process_row(self, row: pd.Series, department_id: int, row_number: int, session_id: str = None) -> Dict[str, Any]:
        """Process a single Excel row"""
        try:
            # Extract basic data
            class_level = int(row['Sınıf Seviyesi'])
            course_code = str(row['Ders Kodu']).strip()
            course_name = str(row['Ders Adı']).strip()
            instructor = str(row['Öğretim Üyesi']).strip()
            student_count = int(row['Öğrenci Sayısı'])
            duration = int(row['Sınav Süresi (dakika)'])

            # Process difficulty level from user input
            difficulty_input = str(row['Sınav Zorluğu']).strip().lower()
            difficulty_level = self._parse_difficulty(difficulty_input)

            # Process computer requirement
            computer_req = str(row['Bilgisayar Gerekli mi?']).strip().lower()
            needs_computer = computer_req in ['evet', 'yes', 'true', '1']
            
            # Process preferred dates
            preferred_dates = self._parse_dates([
                row['Tercih 1'],
                row['Tercih 2'], 
                row['Tercih 3']
            ])
            
            if len(preferred_dates) != 3:
                raise ValueError(f"Exactly 3 valid dates required, got {len(preferred_dates)}")
            
            # Process available rooms
            available_rooms = self._parse_rooms(row['Kullanılabilir Derslikler'])

            # Ensure rooms exist in database
            self._ensure_rooms_exist(available_rooms, department_id)

            # Find or create course
            course = self._find_or_create_course(course_code, course_name, class_level, department_id)
            
            return {
                'course_id': course.id,
                'instructor': instructor,
                'student_count': student_count,
                'duration': duration,
                'needs_computer': needs_computer,
                'preferred_dates': preferred_dates,
                'available_rooms': available_rooms,
                'department_id': department_id,
                'difficulty_level': difficulty_level,
                'status': 'pending',
                'exam_session_id': session_id,
                # Store course_code for later use (not in Exam model)
                '_course_code': course_code
            }
            
        except Exception as e:
            raise ValueError(f"Row processing error: {str(e)}")
    
    def _parse_dates(self, date_values: List[Any]) -> List[str]:
        """Parse and validate date values"""
        parsed_dates = []
        
        for date_val in date_values:
            if pd.isna(date_val):
                continue
                
            try:
                if isinstance(date_val, datetime):
                    parsed_dates.append(date_val.strftime('%Y-%m-%d'))
                elif isinstance(date_val, date):
                    parsed_dates.append(date_val.strftime('%Y-%m-%d'))
                elif isinstance(date_val, str):
                    # Try to parse string date
                    parsed_date = pd.to_datetime(date_val).strftime('%Y-%m-%d')
                    parsed_dates.append(parsed_date)
            except:
                continue
        
        return parsed_dates

    def _parse_difficulty(self, difficulty_input: str) -> str:
        """Parse difficulty level from user input"""
        difficulty_mapping = {
            'kolay': 'easy',
            'easy': 'easy',
            'orta': 'normal',
            'normal': 'normal',
            'medium': 'normal',
            'zor': 'hard',
            'hard': 'hard',
            'çok zor': 'very_hard',
            'very hard': 'very_hard',
            'very_hard': 'very_hard'
        }

        normalized_input = difficulty_input.lower().strip()
        return difficulty_mapping.get(normalized_input, 'normal')  # Default to normal if not found

    def _parse_rooms(self, rooms_str: str) -> List[str]:
        """Parse comma-separated room list"""
        if pd.isna(rooms_str):
            return []

        rooms = str(rooms_str).split(',')
        return [room.strip() for room in rooms if room.strip()]

    def _ensure_rooms_exist(self, room_names: List[str], department_id: int):
        """Ensure rooms exist in database, create if missing"""
        for room_name in room_names:
            if not room_name:
                continue

            # Check if room already exists
            existing_room = Room.query.filter_by(
                name=room_name,
                department_id=department_id
            ).first()

            if not existing_room:
                # Determine room properties based on name patterns
                has_computer = any(pattern in room_name.upper() for pattern in ['LAB', 'Z09', 'D108'])

                # Estimate capacity based on room name patterns
                capacity = 30  # Default
                if 'D112' in room_name:
                    capacity = 42
                elif 'D114' in room_name:
                    capacity = 29
                elif 'D115' in room_name:
                    capacity = 29
                elif 'D117' in room_name:
                    capacity = 40
                elif 'D113' in room_name:
                    capacity = 23
                elif 'A401' in room_name:
                    capacity = 52
                elif 'D111' in room_name:
                    capacity = 42
                elif 'D108' in room_name:
                    capacity = 30
                elif 'D109' in room_name:
                    capacity = 30
                elif 'Z09' in room_name:
                    capacity = 54

                # Create room
                room = Room(
                    name=room_name,
                    capacity=capacity,
                    has_computer=has_computer,
                    department_id=department_id,
                    is_active=True
                )
                db.session.add(room)
                print(f"DEBUG: Created room {room_name} (capacity: {capacity}, computer: {has_computer})")

        db.session.flush()  # Ensure rooms are created before continuing
    
    def _find_or_create_course(self, course_code: str, course_name: str, class_level: int, department_id: int) -> Course:
        """Find existing course or create new one"""
        course = Course.query.filter_by(
            code=course_code,
            class_level=class_level,
            department_id=department_id
        ).first()

        if not course:
            # Create new course with provided name
            course = Course(
                name=course_name,
                code=course_code,
                credits=3,  # Default credits
                class_level=class_level,
                department_id=department_id,
                is_active=True
            )
            db.session.add(course)
            db.session.flush()  # Get ID without committing
        else:
            # Update course name if it's different
            if course.name != course_name:
                course.name = course_name

        return course
    

    
    def _create_exam(self, exam_data: Dict[str, Any]) -> Exam:
        """Create exam in database"""
        # Remove non-model fields before creating exam
        clean_data = {k: v for k, v in exam_data.items() if not k.startswith('_')}
        print(f"DEBUG: Original exam_data keys: {list(exam_data.keys())}")
        print(f"DEBUG: Clean data keys: {list(clean_data.keys())}")
        exam = Exam(**clean_data)
        db.session.add(exam)
        db.session.flush()  # Get ID without committing
        return exam
    
    def commit_changes(self):
        """Commit all changes to database"""
        db.session.commit()
    
    def rollback_changes(self):
        """Rollback all changes"""
        db.session.rollback()
