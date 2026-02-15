from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import FacultyProfile
from apps.academics.models import Subject


class ClassAssignment(models.Model):
    """
    ClassAssignment model linking faculty members to subjects they teach.
    Tracks which faculty member teaches which subject in a specific semester and academic year.
    """
    
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        help_text='Faculty member assigned to teach the subject'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        help_text='Subject being taught'
    )
    
    semester = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Semester number (e.g., 1, 2, 3)'
    )
    
    academic_year = models.CharField(
        max_length=10,
        help_text='Academic year (e.g., 2025-2026, 2026)'
    )
    
    section = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Section or class group (e.g., A, B, C)'
    )
    
    max_students = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Maximum number of students allowed in this class'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this assignment is currently active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Class Assignment'
        verbose_name_plural = 'Class Assignments'
        ordering = ['-academic_year', '-semester', 'subject__name']
        unique_together = ['faculty', 'subject', 'semester', 'academic_year', 'section']
    
    def __str__(self):
        section_str = f" ({self.section})" if self.section else ""
        return f"{self.faculty.user.get_full_name() or self.faculty.employee_id} - {self.subject.code} - {self.academic_year} Sem {self.semester}{section_str}"
    
    def get_enrolled_count(self):
        """
        Get the number of students enrolled in this class.
        This would typically query the Enrollment model filtered by this assignment.
        """
        # Placeholder for future implementation
        return 0
    
    def is_full(self):
        """
        Check if the class has reached maximum capacity.
        """
        if self.max_students is None:
            return False
        return self.get_enrolled_count() >= self.max_students
