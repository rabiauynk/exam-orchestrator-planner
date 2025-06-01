#!/usr/bin/env python3
"""
Test script to create a sample Excel file for exam data
"""

from datetime import datetime, timedelta

import pandas as pd


def create_test_excel():
    """Create a test Excel file with sample exam data"""
    
    # Sample exam data
    data = {
        'Sınıf Seviyesi': [1, 1, 2, 2, 3, 3, 4, 4, 1, 2],
        'Ders Kodu': ['MAT101', 'FIZ101', 'MAT201', 'FIZ201', 'BIL301', 'MAT301', 'MUH401', 'BIL401', 'KIM101', 'STAT201'],
        'Öğretim Üyesi': [
            'Dr. Ahmet Yılmaz', 
            'Prof. Dr. Ayşe Demir', 
            'Doç. Dr. Mehmet Kaya', 
            'Dr. Fatma Özkan',
            'Prof. Dr. Ali Veli',
            'Doç. Dr. Zeynep Ak',
            'Dr. Hasan Çelik',
            'Prof. Dr. Elif Yıldız',
            'Dr. Murat Şen',
            'Doç. Dr. Selin Kara'
        ],
        'Öğrenci Sayısı': [45, 38, 52, 28, 35, 42, 25, 30, 40, 48],
        'Sınav Süresi (dakika)': [90, 60, 120, 90, 90, 120, 120, 90, 60, 90],
        'Tercih 1': [
            '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
            '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-26'
        ],
        'Tercih 2': [
            '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22',
            '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-26', '2024-01-29'
        ],
        'Tercih 3': [
            '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22', '2024-01-23',
            '2024-01-24', '2024-01-25', '2024-01-26', '2024-01-29', '2024-01-30'
        ],
        'Bilgisayar Gerekli mi?': [
            'Hayır', 'Hayır', 'Hayır', 'Hayır', 'Evet', 
            'Hayır', 'Evet', 'Evet', 'Hayır', 'Hayır'
        ],
        'Kullanılabilir Derslikler': [
            'A101,A102,A103',
            'B201,B202,B203',
            'A101,A102,A103,A104',
            'B201,B202,B203',
            'C301,C302,LAB1,LAB2',
            'A101,A102,A103',
            'LAB1,LAB2,LAB3',
            'C301,C302,LAB1,LAB2',
            'B201,B202,B203',
            'A101,A102,A103,A104'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    filename = 'test_sinav_verileri.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sınav Verileri', index=False)
        
        # Get workbook and worksheet for formatting
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
    
    print(f"✅ Test Excel file created: {filename}")
    print(f"📊 Contains {len(df)} exam records")
    print("\n📋 Sample data:")
    print(df.head(3).to_string(index=False))
    
    # Show difficulty distribution
    print("\n🎯 Expected difficulty distribution:")
    for _, row in df.iterrows():
        class_level = row['Sınıf Seviyesi']
        duration = row['Sınav Süresi (dakika)']
        course = row['Ders Kodu']
        
        # Determine expected difficulty
        if class_level == 1 and duration <= 60:
            difficulty = 'easy'
        elif class_level == 1 and duration <= 90:
            difficulty = 'normal'
        elif class_level == 2 and duration <= 90:
            difficulty = 'normal'
        elif class_level == 2 and duration >= 120:
            difficulty = 'hard'
        elif class_level == 3:
            difficulty = 'hard'
        elif class_level == 4 and duration <= 90:
            difficulty = 'hard'
        elif class_level == 4 and duration >= 120:
            difficulty = 'very_hard'
        else:
            difficulty = 'normal'
        
        print(f"  {course} (Sınıf {class_level}, {duration}dk) → {difficulty}")

if __name__ == '__main__':
    create_test_excel()
