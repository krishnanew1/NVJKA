"""
Utility functions for attendance calculations.
"""
from .models import Attendance


def calculate_attendance_percentage(student, subject=None):
    """
    Calculate attendance percentage for a student.
    
    Args:
        student: StudentProfile instance
        subject: Subject instance (optional). If provided, calculates for specific subject.
                If None, calculates overall attendance.
    
    Returns:
        float: Attendance percentage (0-100)
    
    Examples:
        >>> percentage = calculate_attendance_percentage(student, subject)
        >>> print(f"Attendance: {percentage:.2f}%")
    """
    # Get attendance records
    records = student.attendance_records.all()
    
    if subject:
        records = records.filter(subject=subject)
    
    total = records.count()
    
    if total == 0:
        return 0.0
    
    # Count present and late as attended
    attended = records.filter(status__in=['PRESENT', 'LATE']).count()
    
    return (attended / total) * 100


def get_attendance_summary(student, subject=None):
    """
    Get detailed attendance summary for a student.
    
    Args:
        student: StudentProfile instance
        subject: Subject instance (optional)
    
    Returns:
        dict: Summary with total, present, absent, late counts and percentage
    """
    records = student.attendance_records.all()
    
    if subject:
        records = records.filter(subject=subject)
    
    total = records.count()
    present = records.filter(status='PRESENT').count()
    absent = records.filter(status='ABSENT').count()
    late = records.filter(status='LATE').count()
    
    percentage = calculate_attendance_percentage(student, subject)
    
    return {
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'attended': present + late,
        'percentage': round(percentage, 2)
    }
