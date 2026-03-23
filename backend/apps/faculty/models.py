from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import FacultyProfile
from apps.academics.models import Subject


class ClassAssignment(models.Model):
    """
    Links a ``FacultyProfile`` to a ``Subject`` for a specific semester and
    academic year, establishing who is the primary teacher for that term.

    The ``unique_together`` constraint on ``(subject, semester, academic_year)``
    ensures a subject can only have one assigned faculty member per term.
    This record is also used by ``BulkAttendanceView`` to authorise which
    faculty member may mark attendance for a given subject.

    Fields:
        faculty:       The faculty member assigned to teach.
        subject:       The subject being taught.
        semester:      Semester number (≥ 1).
        academic_year: Four-digit year (≥ 2000).
    """
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='class_assignments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='class_assignments'
    )
    semester = models.IntegerField(validators=[MinValueValidator(1)])
    academic_year = models.IntegerField(validators=[MinValueValidator(2000)])

    class Meta:
        unique_together = ('subject', 'semester', 'academic_year')

    def __str__(self):
        return f"{self.faculty} — {self.subject.code} (Sem {self.semester}, {self.academic_year})"
