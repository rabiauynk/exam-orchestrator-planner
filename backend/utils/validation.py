import re
from datetime import datetime, date

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "All required fields present"

def validate_positive_integer(value, field_name):
    """Validate that value is a positive integer"""
    try:
        int_value = int(value)
        if int_value <= 0:
            return False, f"{field_name} must be a positive integer"
        return True, int_value
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer"

def validate_duration(duration):
    """Validate exam duration (15-300 minutes)"""
    try:
        duration_int = int(duration)
        if duration_int < 15:
            return False, "Duration must be at least 15 minutes"
        if duration_int > 300:
            return False, "Duration cannot exceed 300 minutes (5 hours)"
        return True, duration_int
    except (ValueError, TypeError):
        return False, "Duration must be a valid integer"

def validate_student_count(count):
    """Validate student count (1-500)"""
    try:
        count_int = int(count)
        if count_int < 1:
            return False, "Student count must be at least 1"
        if count_int > 500:
            return False, "Student count cannot exceed 500"
        return True, count_int
    except (ValueError, TypeError):
        return False, "Student count must be a valid integer"

def validate_date_format(date_str, format_str='%Y-%m-%d'):
    """Validate date format"""
    try:
        parsed_date = datetime.strptime(date_str, format_str).date()
        return True, parsed_date
    except (ValueError, TypeError):
        return False, f"Invalid date format. Expected: {format_str}"

def validate_time_format(time_str, format_str='%H:%M'):
    """Validate time format"""
    try:
        parsed_time = datetime.strptime(time_str, format_str).time()
        return True, parsed_time
    except (ValueError, TypeError):
        return False, f"Invalid time format. Expected: {format_str}"

def validate_course_name(course_name):
    """Validate course name"""
    if not course_name or len(course_name.strip()) < 2:
        return False, "Course name must be at least 2 characters long"
    if len(course_name) > 100:
        return False, "Course name cannot exceed 100 characters"
    return True, course_name.strip()

def validate_instructor_name(instructor):
    """Validate instructor name"""
    if not instructor or len(instructor.strip()) < 2:
        return False, "Instructor name must be at least 2 characters long"
    if len(instructor) > 100:
        return False, "Instructor name cannot exceed 100 characters"
    return True, instructor.strip()

def validate_class_name(class_name):
    """Validate class name"""
    if not class_name or len(class_name.strip()) < 1:
        return False, "Class name is required"
    if len(class_name) > 20:
        return False, "Class name cannot exceed 20 characters"
    return True, class_name.strip()

def validate_department_code(code):
    """Validate department code"""
    if not code or len(code.strip()) < 2:
        return False, "Department code must be at least 2 characters long"
    if len(code) > 10:
        return False, "Department code cannot exceed 10 characters"
    # Only allow alphanumeric characters and hyphens
    if not re.match(r'^[A-Za-z0-9-]+$', code.strip()):
        return False, "Department code can only contain letters, numbers, and hyphens"
    return True, code.strip().upper()

def validate_preferred_dates(dates, min_count=3):
    """Validate preferred dates list"""
    if not dates or not isinstance(dates, list):
        return False, "Preferred dates must be a list"
    
    if len(dates) < min_count:
        return False, f"At least {min_count} preferred dates are required"
    
    valid_dates = []
    for date_str in dates:
        is_valid, parsed_date = validate_date_format(date_str)
        if not is_valid:
            return False, f"Invalid date format in preferred dates: {date_str}"
        
        # Check if date is not in the past
        if parsed_date < date.today():
            return False, f"Preferred date cannot be in the past: {date_str}"
        
        valid_dates.append(parsed_date)
    
    return True, valid_dates

def sanitize_string(value, max_length=None):
    """Sanitize string input"""
    if not value:
        return ""
    
    # Strip whitespace
    sanitized = str(value).strip()
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
