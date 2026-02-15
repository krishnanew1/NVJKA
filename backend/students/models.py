from django.db import models
from django.core.validators import MinValueValidator
from users.models import StudentProfile
from academics.models import Course


class Enrollment(models.Model):
    """
    Enrollment model tracking student course registrations.
    Links students to courses with enrollment status.
    """
    
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Student enrolled in the course'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Course the student is enrolled in'
    )
    
    date_enrolled = models.DateField(
        auto_now_add=True,
        help_text='Date when the student enrolled'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ENROLLED',
        help_text='Current enrollment status'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-date_enrolled']
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.course.code} ({self.status})"


class AcademicHistory(models.Model):
    """
    Academic history model storing student's previous academic records.
    Uses JSONField to store flexible grade data.
    """
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='academic_history',
        help_text='Student whose academic history is recorded'
    )
    
    previous_grades = models.JSONField(
        default=dict,
        help_text='JSON data containing previous grades and academic records'
    )
    
    year_completed = models.IntegerField(
        validators=[MinValueValidator(1900)],
        help_text='Academic year completed (e.g., 2025)'
    )
    
    semester = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text='Semester number (optional)'
    )
    
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text='GPA for this academic period'
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Additional remarks or notes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Academic History'
        verbose_name_plural = 'Academic Histories'
        ordering = ['-year_completed', '-semester']
        unique_together = ['student', 'year_completed', 'semester']
    
    def __str__(self):
        semester_str = f" Sem {self.semester}" if self.semester else ""
        return f"{self.student.enrollment_number} - {self.year_completed}{semester_str}"
