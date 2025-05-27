from datetime import datetime, date, time, timedelta
import json

def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError):
        return None

def parse_time(time_str, format_str='%H:%M'):
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_str, format_str).time()
    except (ValueError, TypeError):
        return None

def format_date(date_obj, format_str='%d/%m/%Y'):
    """Format date object to string"""
    try:
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(format_str)
    except (AttributeError, TypeError):
        return None

def format_time(time_obj, format_str='%H:%M'):
    """Format time object to string"""
    try:
        if isinstance(time_obj, str):
            return time_obj
        return time_obj.strftime(format_str)
    except (AttributeError, TypeError):
        return None

def get_weekdays_between(start_date, end_date):
    """Get all weekdays between two dates (excluding weekends)"""
    weekdays = []
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    
    return weekdays

def is_time_overlap(start1, end1, start2, end2):
    """Check if two time ranges overlap"""
    return start1 < end2 and start2 < end1

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(minutes=minutes)
    return dt.time()

def time_difference_minutes(start_time, end_time):
    """Calculate difference between two times in minutes"""
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    
    # Handle case where end time is next day
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    return int((end_dt - start_dt).total_seconds() / 60)

def validate_date_range(start_date, end_date):
    """Validate that start date is before end date"""
    if not start_date or not end_date:
        return False, "Both start and end dates are required"
    
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    return True, "Valid date range"

def get_exam_week_dates(start_date, end_date):
    """Get all valid exam dates within the exam week"""
    valid_dates = []
    current_date = start_date
    
    while current_date <= end_date:
        # Only include weekdays
        if current_date.weekday() < 5:
            valid_dates.append(current_date)
        current_date += timedelta(days=1)
    
    return valid_dates

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        return super().default(obj)
