from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.users.models import StudentProfile, CustomUser
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
