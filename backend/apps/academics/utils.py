"""
Utility functions for academics app - Timetable generation and management.
"""
import datetime
from typing import List, Dict, Optional, Tuple
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Timetable, Subject, Course, Department
from apps.users.models import StudentProfile
from apps.students.models import Enrollment
from apps.faculty.models import ClassAssignment


class TimetableGenerator:
    """
    Automated timetable generation service for academic batches.
    
    Generates conflict-free timetables by:
    1. Finding all subjects for a batch
    2. Assigning faculty based on ClassAssignment
    3. Scheduling in available time slots
    4. Avoiding room and faculty conflicts
    """
    
    # Standard time slots (can be configured)
    DEFAULT_TIME_SLOTS = [
        ('09:00', '10:00'),
        ('10:00', '11:00'),
        ('11:15', '12:15'),  # 15-min break after 11:00
        ('12:15', '13:15'),
        ('14:00', '15:00'),  # Lunch break 13:15-14:00
        ('15:00', '16:00'),
        ('16:15', '17:15'),  # 15-min break after 16:00
        ('17:15', '18:15'),
    ]
    
    WORKDAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    
    # Standard classrooms (can be extended)
    DEFAULT_CLASSROOMS = [
        'Room-101', 'Room-102', 'Room-103', 'Room-104', 'Room-105',
        'Room-201', 'Room-202', 'Room-203', 'Room-204', 'Room-205',
        'Lab-A', 'Lab-B', 'Lab-C', 'Auditorium-1', 'Auditorium-2'
    ]

    def __init__(self, academic_year: str = None):
        """
        Initialize timetable generator.
        
        Args:
            academic_year: Academic year (e.g., '2026-27'). Defaults to current year.
        """
        if academic_year is None:
            current_year = datetime.datetime.now().year
            academic_year = f"{current_year}-{str(current_year + 1)[2:]}"
        
        self.academic_year = academic_year
        self.time_slots = self.DEFAULT_TIME_SLOTS
        self.workdays = self.WORKDAYS
        self.classrooms = self.DEFAULT_CLASSROOMS

    def generate_batch_timetable(self, batch_year: int, department_id: int = None, 
                                semester: int = None) -> Dict:
        """
        Generate timetable for a specific batch.
        
        Args:
            batch_year: Year of admission (e.g., 2024)
            department_id: Optional department filter
            semester: Optional semester filter (defaults to current semester of batch)
            
        Returns:
            Dict containing generated timetable and statistics
            
        Raises:
            ValidationError: If batch not found or insufficient data
        """
        # Find students in the batch
        students_query = StudentProfile.objects.filter(batch_year=batch_year)
        
        if department_id:
            students_query = students_query.filter(department_id=department_id)
        
        if not students_query.exists():
            raise ValidationError(f"No students found for batch {batch_year}")
        
        # Determine semester if not provided
        if semester is None:
            # Calculate current semester based on batch year
            current_year = datetime.datetime.now().year
            years_passed = current_year - batch_year
            semester = min(years_passed * 2 + 1, 8)  # Assume max 8 semesters
        
        # Get all subjects for this batch
        subjects = self._get_batch_subjects(batch_year, department_id, semester)
        
        if not subjects:
            raise ValidationError(f"No subjects found for batch {batch_year}, semester {semester}")
        
        # Generate class name for the batch
        class_name = self._generate_class_name(batch_year, department_id, semester)
        
        # Clear existing timetable for this batch
        self._clear_existing_timetable(class_name)
        
        # Generate timetable entries
        generated_entries = []
        failed_subjects = []
        
        for subject in subjects:
            try:
                entries = self._schedule_subject(subject, class_name, semester)
                generated_entries.extend(entries)
            except ValidationError as e:
                failed_subjects.append({
                    'subject': subject,
                    'error': str(e)
                })
        
        # Generate statistics
        stats = {
            'batch_year': batch_year,
            'semester': semester,
            'class_name': class_name,
            'academic_year': self.academic_year,
            'total_subjects': len(subjects),
            'scheduled_subjects': len(subjects) - len(failed_subjects),
            'failed_subjects': len(failed_subjects),
            'total_entries': len(generated_entries),
            'generated_entries': [self._serialize_entry(entry) for entry in generated_entries],
            'failed_subjects_details': failed_subjects
        }
        
        return stats

    def _get_batch_subjects(self, batch_year: int, department_id: int = None, 
                           semester: int = None) -> List[Subject]:
        """Get all subjects for a batch based on their enrollments."""
        # Find enrolled courses for students in this batch
        students = StudentProfile.objects.filter(batch_year=batch_year)
        if department_id:
            students = students.filter(department_id=department_id)
        
        # Get active enrollments for these students
        enrollments = Enrollment.objects.filter(
            student__in=students,
            status='Active'
        )
        
        if semester:
            enrollments = enrollments.filter(semester=semester)
        
        # Get subjects from enrolled courses
        course_ids = enrollments.values_list('course_id', flat=True).distinct()
        
        subjects_query = Subject.objects.filter(course_id__in=course_ids)
        
        if semester:
            subjects_query = subjects_query.filter(semester=semester)
        
        return list(subjects_query.select_related('course__department'))

    def _generate_class_name(self, batch_year: int, department_id: int = None, 
                            semester: int = None) -> str:
        """Generate a class name for the batch."""
        if department_id:
            try:
                dept = Department.objects.get(id=department_id)
                dept_code = dept.code
            except Department.DoesNotExist:
                dept_code = "DEPT"
        else:
            dept_code = "BATCH"
        
        return f"{dept_code}-{batch_year}-S{semester or 'X'}"

    def _clear_existing_timetable(self, class_name: str):
        """Clear existing timetable entries for the class."""
        Timetable.objects.filter(
            class_name=class_name,
            academic_year=self.academic_year
        ).delete()

    def _schedule_subject(self, subject: Subject, class_name: str, 
                         semester: int) -> List[Timetable]:
        """
        Schedule a subject in available time slots.
        
        Args:
            subject: Subject to schedule
            class_name: Class identifier
            semester: Current semester
            
        Returns:
            List of created Timetable entries
            
        Raises:
            ValidationError: If no suitable slot found
        """
        # Find assigned faculty for this subject
        faculty = self._get_subject_faculty(subject, semester)
        
        # Determine number of classes per week based on credits
        classes_per_week = min(subject.credits, 5)  # Max 5 classes per week
        
        scheduled_entries = []
        
        for _ in range(classes_per_week):
            slot = self._find_available_slot(subject, faculty, class_name)
            
            if slot is None:
                if not scheduled_entries:
                    raise ValidationError(
                        f"No available slot found for {subject.code} - {subject.name}"
                    )
                else:
                    # Partial scheduling is acceptable
                    break
            
            day, start_time, end_time, classroom = slot
            
            # Create timetable entry
            entry = Timetable.objects.create(
                class_name=class_name,
                subject=subject,
                faculty=faculty,
                day_of_week=day,
                start_time=datetime.time.fromisoformat(start_time),
                end_time=datetime.time.fromisoformat(end_time),
                classroom=classroom,
                academic_year=self.academic_year,
                is_active=True
            )
            
            scheduled_entries.append(entry)
        
        return scheduled_entries

    def _get_subject_faculty(self, subject: Subject, semester: int):
        """Find assigned faculty for a subject."""
        try:
            assignment = ClassAssignment.objects.get(
                subject=subject,
                semester=semester,
                academic_year=int(self.academic_year.split('-')[0])
            )
            return assignment.faculty
        except ClassAssignment.DoesNotExist:
            return None

    def _find_available_slot(self, subject: Subject, faculty, class_name: str) -> Optional[Tuple]:
        """
        Find an available time slot for the subject.
        
        Returns:
            Tuple of (day, start_time, end_time, classroom) or None if no slot available
        """
        for day in self.workdays:
            for start_time, end_time in self.time_slots:
                for classroom in self.classrooms:
                    if self._is_slot_available(day, start_time, end_time, classroom, faculty, class_name):
                        return (day, start_time, end_time, classroom)
        
        return None

    def _is_slot_available(self, day: str, start_time: str, end_time: str, 
                          classroom: str, faculty, class_name: str) -> bool:
        """
        Check if a time slot is available (no conflicts).
        
        Args:
            day: Day of week
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            classroom: Classroom identifier
            faculty: Faculty profile (can be None)
            class_name: Class identifier
            
        Returns:
            True if slot is available, False otherwise
        """
        start_dt = datetime.time.fromisoformat(start_time)
        end_dt = datetime.time.fromisoformat(end_time)
        
        # Check classroom conflicts
        classroom_conflicts = Timetable.objects.filter(
            day_of_week=day,
            academic_year=self.academic_year,
            is_active=True
        ).filter(
            Q(classroom=classroom) | Q(room_number=classroom)
        ).filter(
            Q(start_time__lt=end_dt) & Q(end_time__gt=start_dt)
        )
        
        if classroom_conflicts.exists():
            return False
        
        # Check faculty conflicts (if faculty is assigned)
        if faculty:
            faculty_conflicts = Timetable.objects.filter(
                faculty=faculty,
                day_of_week=day,
                academic_year=self.academic_year,
                is_active=True
            ).filter(
                Q(start_time__lt=end_dt) & Q(end_time__gt=start_dt)
            )
            
            if faculty_conflicts.exists():
                return False
        
        # Check class conflicts (same class can't have multiple subjects at same time)
        class_conflicts = Timetable.objects.filter(
            class_name=class_name,
            day_of_week=day,
            academic_year=self.academic_year,
            is_active=True
        ).filter(
            Q(start_time__lt=end_dt) & Q(end_time__gt=start_dt)
        )
        
        if class_conflicts.exists():
            return False
        
        return True

    def _serialize_entry(self, entry: Timetable) -> Dict:
        """Serialize a timetable entry for API response."""
        return {
            'id': entry.id,
            'class_name': entry.class_name,
            'subject': {
                'id': entry.subject.id,
                'name': entry.subject.name,
                'code': entry.subject.code,
                'credits': entry.subject.credits
            },
            'faculty': {
                'id': entry.faculty.id if entry.faculty else None,
                'name': entry.faculty.user.get_full_name() if entry.faculty else None,
                'employee_id': entry.faculty.employee_id if entry.faculty else None
            } if entry.faculty else None,
            'day_of_week': entry.day_of_week,
            'start_time': entry.start_time.strftime('%H:%M'),
            'end_time': entry.end_time.strftime('%H:%M'),
            'classroom': entry.classroom,
            'academic_year': entry.academic_year
        }


def generate_batch_timetable(batch_year: int, department_id: int = None, 
                           semester: int = None, academic_year: str = None) -> Dict:
    """
    Convenience function to generate timetable for a batch.
    
    Args:
        batch_year: Year of admission (e.g., 2024)
        department_id: Optional department filter
        semester: Optional semester filter
        academic_year: Optional academic year (defaults to current)
        
    Returns:
        Dict containing generated timetable and statistics
    """
    generator = TimetableGenerator(academic_year)
    return generator.generate_batch_timetable(batch_year, department_id, semester)


def get_batch_timetable(batch_year: int, department_id: int = None, 
                       semester: int = None, academic_year: str = None) -> List[Dict]:
    """
    Retrieve existing timetable for a batch.
    
    Args:
        batch_year: Year of admission
        department_id: Optional department filter
        semester: Optional semester filter
        academic_year: Optional academic year
        
    Returns:
        List of timetable entries
    """
    generator = TimetableGenerator(academic_year)
    class_name = generator._generate_class_name(batch_year, department_id, semester)
    
    entries = Timetable.objects.filter(
        class_name=class_name,
        academic_year=generator.academic_year,
        is_active=True
    ).select_related('subject', 'faculty__user').order_by('day_of_week', 'start_time')
    
    return [generator._serialize_entry(entry) for entry in entries]