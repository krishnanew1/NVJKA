from django.db import models
from apps.users.models import StudentProfile
from apps.academics.models import Subject


class Attendance(models.Model):
    """
    Attendance model tracking student presence in classes.
    Records daily attendance status for students in specific subjects.
    """
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text='Student whose attendance is being recorded'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text='Subject for which attendance is recorded'
    )
    
    date = models.DateField(
        help_text='Date of the class'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text='Attendance status'
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Additional remarks or notes'
    )
    
    marked_by = models.ForeignKey(
        'users.FacultyProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendances',
        help_text='Faculty member who marked the attendance'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-date', 'student__enrollment_number']
        unique_together = ['student', 'subject', 'date']
        indexes = [
            models.Index(fields=['date', 'subject']),
            models.Index(fields=['student', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.subject.code} - {self.date} ({self.status})"
    
    @property
    def is_present(self):
        """Check if student was present."""
        return self.status == 'PRESENT'
    
    @property
    def is_absent(self):
        """Check if student was absent."""
        return self.status == 'ABSENT'
    
    @property
    def is_late(self):
        """Check if student was late."""
        return self.status == 'LATE'
