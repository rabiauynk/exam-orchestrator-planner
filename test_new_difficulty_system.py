#!/usr/bin/env python3
"""
Test script for new difficulty system
"""

import pandas as pd
import os

def create_test_excel():
    """Create test Excel file with new difficulty system"""
    
    # Test data with new difficulty column
    test_data = {
        'Sınıf Seviyesi': [1, 2, 3, 4, 1, 2],
        'Ders Kodu': ['MAT101', 'FIZ201', 'BIL301', 'MUH401', 'KIM101', 'ENG201'],
        'Ders Adı': [
            'Matematik I', 
            'Fizik II', 
            'Bilgisayar Programlama', 
            'Mühendislik Tasarımı',
            'Kimya I',
            'İngilizce II'
        ],
        'Öğretim Üyesi': [
            'Dr. Ahmet Yılmaz', 
            'Prof. Dr. Ayşe Demir', 
            'Doç. Dr. Mehmet Kaya', 
            'Dr. Fatma Özkan',
            'Dr. Ali Veli',
            'Dr. Zeynep Ak'
        ],
        'Öğrenci Sayısı': [45, 38, 52, 28, 35, 42],
        'Sınav Süresi (dakika)': [90, 120, 90, 120, 60, 90],
        'Sınav Zorluğu': ['Kolay', 'Orta', 'Zor', 'Orta', 'Kolay', 'Kolay'],
        'Tercih 1': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22'],
        'Tercih 2': ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22', '2024-01-23'],
        'Tercih 3': ['2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22', '2024-01-23', '2024-01-24'],
        'Bilgisayar Gerekli mi?': ['Hayır', 'Hayır', 'Evet', 'Evet', 'Hayır', 'Hayır'],
        'Kullanılabilir Derslikler': [
            'D111,D112,D113',
            'D114,D115,D117',
            'Z09,D108,LAB1',
            'A401,D109,LAB2',
            'D111,D112,D113',
            'D114,D115,D117'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Save to Excel
    filename = 'test_new_difficulty_system.xlsx'
    df.to_excel(filename, sheet_name='Sınav Verileri', index=False)
    
    print(f"✅ Test Excel file created: {filename}")
    print(f"📊 Test data includes:")
    print(f"   - {len(df)} exam records")
    print(f"   - Difficulty levels: {df['Sınav Zorluğu'].unique()}")
    print(f"   - Class levels: {df['Sınıf Seviyesi'].unique()}")
    
    # Show difficulty distribution
    print(f"\n🎯 Difficulty distribution:")
    difficulty_counts = df['Sınav Zorluğu'].value_counts()
    for difficulty, count in difficulty_counts.items():
        print(f"   - {difficulty}: {count} sınav")
    
    return filename

def show_expected_scheduling_rules():
    """Show expected scheduling rules"""
    print(f"\n📋 Expected Scheduling Rules:")
    print(f"1. 🔴 Zor sınavlar: O gün başka hiçbir sınav yapılamaz")
    print(f"2. 🟡 Orta sınavlar: Aynı gün maksimum 1 adet Kolay sınav olabilir")
    print(f"3. 🟢 Kolay sınavlar: Birden fazla olabilir (Zor/Orta yoksa)")
    
    print(f"\n🗓️ Expected daily schedule based on test data:")
    print(f"   - BIL301 (Zor) → Tek başına bir gün")
    print(f"   - FIZ201 (Orta) + KIM101 (Kolay) → Aynı gün olabilir")
    print(f"   - MAT101 (Kolay) + ENG201 (Kolay) → Aynı gün olabilir")
    print(f"   - MUH401 (Orta) → Tek başına veya 1 Kolay ile")

if __name__ == "__main__":
    print("🧪 Testing New Difficulty System")
    print("=" * 50)
    
    # Create test file
    filename = create_test_excel()
    
    # Show rules
    show_expected_scheduling_rules()
    
    print(f"\n📝 Next steps:")
    print(f"1. Upload {filename} to the system")
    print(f"2. Check if difficulty levels are correctly parsed")
    print(f"3. Verify scheduling follows new rules")
    print(f"4. Test Excel export includes course names")
