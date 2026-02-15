"""
Utility functions for exams app - GPA calculations and grade processing.
"""
from decimal import Decimal
from django.db.models import Avg, Sum, Q
from exams.models import Grade, Assessment
from users.models import StudentProfile


def calculate_gpa(student_id):
    """
    Calculate GPA for a student on a 10.0 scale.
    
    The GPA is calculated as a weighted average where:
    - Each grade's percentage is converted to a 10-point scale
    - Grades are weighted by the subject's credit hours
    - Only the highest grade per subject is considered (in case of multiple assessments)
    
    Args:
        student_id: ID of the StudentProfile
        
    Returns:
        dict: {
            'gpa': Decimal,  # GPA on 10.0 scale
            'total_credits': int,  # Total credits considered
            'grades_count': int,  # Number of grades included
            'subject_grades': list  # List of per-subject grade details
        }
        
    Raises:
        StudentProfile.DoesNotExist: If student not found
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
    except StudentProfile.DoesNotExist:
        raise StudentProfile.DoesNotExist(f"Student with id {student_id} not found")
    
    # Get all grades for the student
    grades = Grade.objects.filter(student=student).select_related(
        'assessment', 'assessment__subject'
    )
    
    if not grades.exists():
        return {
            'gpa': Decimal('0.0'),
            'total_credits': 0,
            'grades_count': 0,
            'subject_grades': []
        }
    
    # Group grades by subject and calculate average percentage per subject
    subject_data = {}
    
    for grade in grades:
        subject = grade.assessment.subject
        subject_code = subject.code
        
        if subject_code not in subject_data:
            subject_data[subject_code] = {
                'subject': subject,
                'credits': subject.credits,
                'percentages': [],
                'grades': []
            }
        
        subject_data[subject_code]['percentages'].append(float(grade.percentage))
        subject_data[subject_code]['grades'].append(grade)
    
    # Calculate weighted GPA
    total_weighted_points = Decimal('0.0')
    total_credits = 0
    subject_grades = []
    
    for subject_code, data in subject_data.items():
        # Calculate average percentage for this subject
        avg_percentage = sum(data['percentages']) / len(data['percentages'])
        
        # Convert percentage to 10-point scale
        grade_point = Decimal(str(avg_percentage / 10.0))
        
        # Weight by credits
        credits = data['credits']
        weighted_points = grade_point * Decimal(str(credits))
        
        total_weighted_points += weighted_points
        total_credits += credits
        
        subject_grades.append({
            'subject_code': subject_code,
            'subject_name': data['subject'].name,
            'credits': credits,
            'average_percentage': round(avg_percentage, 2),
            'grade_point': round(float(grade_point), 2),
            'weighted_points': round(float(weighted_points), 2),
            'assessments_count': len(data['grades'])
        })
    
    # Calculate final GPA
    if total_credits > 0:
        gpa = total_weighted_points / Decimal(str(total_credits))
    else:
        gpa = Decimal('0.0')
    
    return {
        'gpa': round(gpa, 2),
        'total_credits': total_credits,
        'grades_count': grades.count(),
        'subject_grades': sorted(subject_grades, key=lambda x: x['subject_code'])
    }


def get_letter_grade_from_percentage(percentage):
    """
    Convert percentage to letter grade.
    
    Args:
        percentage: float or Decimal percentage (0-100)
        
    Returns:
        str: Letter grade (A, B, C, D, F)
    """
    percentage = float(percentage)
    
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'


def get_grade_point_from_percentage(percentage):
    """
    Convert percentage to grade point on 10.0 scale.
    
    Args:
        percentage: float or Decimal percentage (0-100)
        
    Returns:
        Decimal: Grade point (0.0-10.0)
    """
    return Decimal(str(float(percentage) / 10.0))


def calculate_subject_average(student_id, subject_id):
    """
    Calculate average grade for a specific subject.
    
    Args:
        student_id: ID of the StudentProfile
        subject_id: ID of the Subject
        
    Returns:
        dict: {
            'average_percentage': Decimal,
            'average_grade_point': Decimal,
            'letter_grade': str,
            'assessments_count': int,
            'grades': list
        }
    """
    grades = Grade.objects.filter(
        student_id=student_id,
        assessment__subject_id=subject_id
    ).select_related('assessment')
    
    if not grades.exists():
        return {
            'average_percentage': Decimal('0.0'),
            'average_grade_point': Decimal('0.0'),
            'letter_grade': 'F',
            'assessments_count': 0,
            'grades': []
        }
    
    # Calculate average percentage
    total_percentage = sum(float(grade.percentage) for grade in grades)
    avg_percentage = Decimal(str(total_percentage / grades.count()))
    
    # Convert to grade point
    avg_grade_point = get_grade_point_from_percentage(avg_percentage)
    
    # Get letter grade
    letter_grade = get_letter_grade_from_percentage(avg_percentage)
    
    # Prepare grade details
    grade_details = [
        {
            'assessment_name': grade.assessment.name,
            'assessment_type': grade.assessment.assessment_type,
            'marks_obtained': float(grade.marks_obtained),
            'max_marks': float(grade.assessment.max_marks),
            'percentage': float(grade.percentage),
            'weightage': float(grade.assessment.weightage)
        }
        for grade in grades
    ]
    
    return {
        'average_percentage': round(avg_percentage, 2),
        'average_grade_point': round(avg_grade_point, 2),
        'letter_grade': letter_grade,
        'assessments_count': grades.count(),
        'grades': grade_details
    }


def get_student_transcript(student_id):
    """
    Generate a complete academic transcript for a student.
    
    Args:
        student_id: ID of the StudentProfile
        
    Returns:
        dict: Complete transcript with GPA and all subject grades
    """
    try:
        student = StudentProfile.objects.get(id=student_id)
    except StudentProfile.DoesNotExist:
        raise StudentProfile.DoesNotExist(f"Student with id {student_id} not found")
    
    # Calculate GPA
    gpa_data = calculate_gpa(student_id)
    
    # Get detailed subject information
    detailed_subjects = []
    for subject_grade in gpa_data['subject_grades']:
        subject_code = subject_grade['subject_code']
        
        # Find the subject ID from the first grade
        grade = Grade.objects.filter(
            student=student,
            assessment__subject__code=subject_code
        ).select_related('assessment__subject').first()
        
        if grade:
            subject_details = calculate_subject_average(
                student_id,
                grade.assessment.subject.id
            )
            
            detailed_subjects.append({
                'subject_code': subject_code,
                'subject_name': subject_grade['subject_name'],
                'credits': subject_grade['credits'],
                'average_percentage': subject_details['average_percentage'],
                'grade_point': subject_grade['grade_point'],
                'letter_grade': subject_details['letter_grade'],
                'assessments': subject_details['grades']
            })
    
    return {
        'student': {
            'enrollment_number': student.enrollment_number,
            'name': student.user.get_full_name() or student.user.username,
            'email': student.user.email,
            'department': student.department.name if student.department else None,
            'batch_year': student.batch_year,
            'current_semester': student.current_semester
        },
        'gpa': float(gpa_data['gpa']),
        'total_credits': gpa_data['total_credits'],
        'total_assessments': gpa_data['grades_count'],
        'subjects': detailed_subjects
    }
