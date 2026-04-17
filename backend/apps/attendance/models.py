from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.users.models import StudentProfile, CustomUser, FacultyProfile
from apps.academics.models import Subject


class Attendance(models.Model):
    """
    Records a single student's attendance for a subject on a specific date.

    Each record is unique per (student, subject, date) — enforced by
    ``unique_together``.  The ``clean()`` method prevents future-dated entries,
    and ``save()`` calls ``clean()`` automatically so the constraint is enforced
    at the ORM level as well as via the API.

    Fields:
        student:     The student whose attendance is being recorded.
        subject:     The subject the class belongs to.
        date:        The calendar date of the class (cannot be in the future).
        status:      Present / Absent / Late.
        recorded_by: The ``CustomUser`` (faculty or admin) who marked attendance.
    """
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendances'
    )

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def clean(self):
        if self.date and self.date > timezone.localdate():
            raise ValidationError({'date': 'Attendance date cannot be in the future.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} — {self.subject.code} — {self.date} ({self.status})"


class AttendanceReportSubmission(models.Model):
    """
    Records when a faculty member submits an attendance report for a specific batch.
    
    This model tracks attendance report submissions by faculty for administrative review.
    Each submission is for a specific subject and batch (e.g., '2024-IMG').
    
    Fields:
        faculty:              The faculty member submitting the report.
        subject:              The subject for which attendance is being reported.
        batch_string:         The batch identifier (e.g., '2024-IMG', '2023-CSE').
        submitted_at:         Timestamp when the report was submitted.
        is_reviewed_by_admin: Whether an admin has reviewed this submission.
        reviewed_at:          Timestamp when the report was reviewed (optional).
        reviewed_by:          The admin user who reviewed the report (optional).
        notes:                Optional notes from admin review.
    """
    
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='attendance_report_submissions'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_report_submissions'
    )
    batch_string = models.CharField(
        max_length=50,
        help_text="Batch identifier (e.g., '2024-IMG', '2023-CSE')"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed_by_admin = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_attendance_reports'
    )
    notes = models.TextField(blank=True, help_text="Admin review notes")
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['faculty', 'subject']),
            models.Index(fields=['batch_string']),
            models.Index(fields=['is_reviewed_by_admin']),
        ]
    
    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.subject.code} - {self.batch_string} ({self.submitted_at.strftime('%Y-%m-%d')})"
