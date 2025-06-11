#!/usr/bin/env python3
"""
Test script for new difficulty rules
"""

def test_difficulty_rules():
    """Test the new difficulty rules logic"""
    
    print("🧪 Testing New Difficulty Rules")
    print("=" * 50)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Empty day - any exam should be allowed',
            'existing_exams': [],
            'new_exam': 'hard',
            'expected': True
        },
        {
            'name': 'Hard exam exists - no other exam allowed',
            'existing_exams': ['hard'],
            'new_exam': 'normal',
            'expected': False
        },
        {
            'name': 'Hard exam exists - no other hard exam allowed',
            'existing_exams': ['hard'],
            'new_exam': 'hard',
            'expected': False
        },
        {
            'name': 'Normal exam exists - another normal exam allowed',
            'existing_exams': ['normal'],
            'new_exam': 'normal',
            'expected': True
        },
        {
            'name': 'Normal exam exists - easy exam allowed',
            'existing_exams': ['normal'],
            'new_exam': 'easy',
            'expected': True
        },
        {
            'name': 'Multiple normal exams - another normal allowed',
            'existing_exams': ['normal', 'normal'],
            'new_exam': 'normal',
            'expected': True
        },
        {
            'name': 'Normal and easy exams - another easy allowed',
            'existing_exams': ['normal', 'easy'],
            'new_exam': 'easy',
            'expected': True
        },
        {
            'name': 'Easy exams only - normal exam allowed',
            'existing_exams': ['easy', 'easy'],
            'new_exam': 'normal',
            'expected': True
        },
        {
            'name': 'Easy exams only - another easy allowed',
            'existing_exams': ['easy', 'easy'],
            'new_exam': 'easy',
            'expected': True
        },
        {
            'name': 'Normal exam exists - hard exam NOT allowed',
            'existing_exams': ['normal'],
            'new_exam': 'hard',
            'expected': False
        }
    ]
    
    def check_difficulty_rules(existing_exams, new_exam):
        """Simulate the difficulty checking logic"""
        difficulty_counts = {
            'hard': 0,
            'normal': 0,
            'easy': 0
        }
        
        # Count existing exams
        for exam in existing_exams:
            difficulty_counts[exam] += 1
        
        # Check rules for new exam
        if new_exam == 'hard':
            # Hard exam: no other exams allowed
            total_existing = sum(difficulty_counts.values())
            return total_existing == 0
        elif new_exam == 'normal':
            # Normal exam: no hard exams allowed
            return difficulty_counts['hard'] == 0
        else:  # easy
            # Easy exam: no hard exams allowed
            return difficulty_counts['hard'] == 0
    
    # Run tests
    passed = 0
    failed = 0
    
    for scenario in scenarios:
        result = check_difficulty_rules(scenario['existing_exams'], scenario['new_exam'])
        expected = scenario['expected']
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} {scenario['name']}")
        print(f"     Existing: {scenario['existing_exams']}")
        print(f"     New: {scenario['new_exam']}")
        print(f"     Expected: {expected}, Got: {result}")
        print()
        
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Difficulty rules are working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the logic.")

def show_updated_rules():
    """Show the updated difficulty rules"""
    print("\n📋 Updated Difficulty Rules:")
    print("=" * 30)
    print("🔴 ZOR SINAVLAR:")
    print("   - O gün başka hiçbir sınav yapılamaz")
    print("   - En yüksek öncelik")
    print()
    print("🟡 ORTA SINAVLAR:")
    print("   - Aynı gün birden fazla orta sınav olabilir")
    print("   - Kolay sınavlar da eklenebilir")
    print("   - Zor sınav varsa yapılamaz")
    print()
    print("🟢 KOLAY SINAVLAR:")
    print("   - Birden fazla olabilir")
    print("   - Orta sınavlarla birlikte olabilir")
    print("   - Zor sınav varsa yapılamaz")
    print()
    print("📝 Zorluk Tespiti:")
    print("   - Excel'deki 'Sınav Zorluğu' kolonundan")
    print("   - Kullanıcı 'Kolay', 'Orta', 'Zor' seçer")
    print("   - Otomatik hesaplama YOK")

if __name__ == "__main__":
    test_difficulty_rules()
    show_updated_rules()
