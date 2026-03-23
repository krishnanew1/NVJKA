from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import StudentProfile
from apps.academics.models import Course


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Dropped', 'Dropped'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    date_enrolled = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    semester = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student} - {self.course} (Sem {self.semester})"


class AcademicHistory(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='academic_history'
    )
    institution_name = models.CharField(max_length=255)
    board_university = models.CharField(max_length=255)
    passing_year = models.IntegerField(validators=[MinValueValidator(1900)])
    percentage_cgpa = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.institution_name} ({self.passing_year})"
