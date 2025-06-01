import os
import time

from database import db
from flask import Blueprint, jsonify, request
from services.excel_service import ExcelService
from services.scheduler_service import SchedulerService
from werkzeug.utils import secure_filename

excel_bp = Blueprint('excel', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@excel_bp.route('/api/excel/upload', methods=['POST'])
def upload_excel():
    """Upload and process Excel file for exam creation"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        department_id = request.form.get('department_id')
        auto_schedule = request.form.get('auto_schedule', 'true').lower() == 'true'
        
        # Validate inputs
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not department_id:
            return jsonify({
                'success': False,
                'message': 'Department ID is required'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only .xlsx and .xls files are allowed'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # Process Excel file
            excel_service = ExcelService()
            result = excel_service.process_excel_file(file_path, int(department_id))
            
            if result['success']:
                # Commit changes to database
                excel_service.commit_changes()
                
                # Auto-schedule if requested
                print(f"DEBUG: auto_schedule={auto_schedule}, processed={result['processed']}")
                if auto_schedule and result['processed'] > 0:
                    try:
                        print(f"DEBUG: Starting scheduling for {result['processed']} exams")
                        from services.advanced_scheduler import \
                            AdvancedSchedulerService

                        # Get created exams data for scheduling
                        exam_data = []
                        for exam_info in result.get('created_exams', []):
                            # Get full exam data from database
                            from models import Exam
                            exam = Exam.query.get(exam_info['id'])
                            if exam:
                                exam_data.append({
                                    'id': exam.id,
                                    'course_code': exam_info['course_code'],
                                    'instructor': exam_info['instructor'],
                                    'student_count': exam.student_count,
                                    'duration': exam.duration,
                                    'needs_computer': exam.needs_computer,
                                    'preferred_dates': exam.preferred_dates,
                                    'available_rooms': exam.available_rooms,
                                    'difficulty_level': exam_info['difficulty']
                                })

                        print(f"DEBUG: Prepared {len(exam_data)} exams for scheduling")

                        scheduler = AdvancedSchedulerService()
                        schedule_result = scheduler.schedule_exams(exam_data)

                        print(f"DEBUG: Scheduling result: {schedule_result}")
                        result['scheduling'] = schedule_result

                    except Exception as e:
                        import traceback
                        print(f"Scheduling error: {str(e)}")
                        print(f"Scheduling traceback: {traceback.format_exc()}")
                        result['scheduling'] = {
                            'success': False,
                            'message': f'Scheduling failed: {str(e)}'
                        }
                
                return jsonify(result), 200
            else:
                # Rollback on failure
                excel_service.rollback_changes()
                return jsonify(result), 400
                
        except Exception as e:
            # Rollback on error
            try:
                excel_service.rollback_changes()
            except:
                pass

            import traceback
            print(f"Processing error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")

            return jsonify({
                'success': False,
                'message': f'Processing error: {str(e)}',
                'traceback': traceback.format_exc()
            }), 500
            
        finally:
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        }), 500

@excel_bp.route('/api/excel/template', methods=['GET'])
def download_template():
    """Download Excel template file"""
    try:
        from io import BytesIO

        import pandas as pd
        from flask import send_file

        # Create template data
        template_data = {
            'Sınıf Seviyesi': [1, 2, 3, 4],
            'Ders Kodu': ['MAT101', 'FIZ201', 'BIL301', 'MUH401'],
            'Öğretim Üyesi': ['Dr. Ahmet Yılmaz', 'Prof. Dr. Ayşe Demir', 'Doç. Dr. Mehmet Kaya', 'Dr. Fatma Özkan'],
            'Öğrenci Sayısı': [45, 38, 52, 28],
            'Sınav Süresi (dakika)': [90, 120, 90, 120],
            'Tercih 1': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'],
            'Tercih 2': ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'Tercih 3': ['2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22'],
            'Bilgisayar Gerekli mi?': ['Hayır', 'Hayır', 'Evet', 'Evet'],
            'Kullanılabilir Derslikler': [
                'A101,A102,A103',
                'B201,B202,B203',
                'C301,C302,LAB1,LAB2',
                'D401,D402,LAB3,LAB4'
            ]
        }
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(template_data)
        
        # Create BytesIO object
        output = BytesIO()
        
        # Write to Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sınav Verileri', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Sınav Verileri']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='sinav_verileri_template.xlsx'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Template generation error: {str(e)}'
        }), 500

@excel_bp.route('/api/excel/validate', methods=['POST'])
def validate_excel():
    """Validate Excel file without processing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only .xlsx and .xls files are allowed'
            }), 400
        
        # Save temporary file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"temp_{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            import pandas as pd

            # Read and validate Excel file
            df = pd.read_excel(file_path)
            
            excel_service = ExcelService()
            validation_result = excel_service._validate_columns(df)
            
            if validation_result['valid']:
                # Additional validation
                validation_result.update({
                    'total_rows': len(df),
                    'columns_found': list(df.columns),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                })
            
            return jsonify(validation_result), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'File validation error: {str(e)}'
            }), 400
            
        finally:
            # Clean up temp file
            try:
                os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }), 500
