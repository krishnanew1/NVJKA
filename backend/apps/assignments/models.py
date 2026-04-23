from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    """
    Homework/assignment posted by a faculty member for a specific batch+subject.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
    )

    # Target batch scope (v1: section is optional and not yet derived from student profile)
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    batch_year = models.IntegerField(validators=[MinValueValidator(1900)])
    semester = models.IntegerField(validators=[MinValueValidator(1)])
    section = models.CharField(max_length=10, blank=True, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)

    requires_submission = models.BooleanField(default=True)
    allow_late = models.BooleanField(default=False)

    attachment = models.FileField(
        upload_to='assignments/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'png', 'jpg', 'jpeg'])],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['department', 'batch_year', 'semester']),
            models.Index(fields=['subject']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.subject.code} - {self.title}"


class AssignmentSubmission(models.Model):
    """
    Student submission for a given assignment (one per student).
    """

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    student = models.ForeignKey(
        'users.StudentProfile',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
    )

    file = models.FileField(
        upload_to='assignment_submissions/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'png', 'jpg', 'jpeg'])],
    )
    text_answer = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at', '-id']
        indexes = [
            models.Index(fields=['assignment', 'student']),
        ]

    def __str__(self):
        return f"{self.assignment_id} - {self.student_id}"

    @property
    def is_late(self) -> bool:
        if not self.submitted_at or not self.assignment.due_at:
            return False
        return self.submitted_at > self.assignment.due_at

    def mark_submitted(self):
        self.submitted_at = timezone.now()
