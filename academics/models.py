from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    """
    Model representing an academic department.
    
    Each department can have multiple courses and is identified by
    a unique name and code.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full name of the department"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short code for the department (e.g., 'CSE', 'ECE')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the department"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['code']


class Course(models.Model):
    """
    Model representing an academic course.
    
    Each course belongs to a department and can have multiple subjects.
    """
    name = models.CharField(
        max_length=100,
        help_text="Full name of the course"
    )
    code = models.CharField(
        max_length=15,
        unique=True,
        help_text="Unique course code (e.g., 'B.Tech CSE', 'M.Sc Physics')"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text="Department offering this course"
    )
    credits = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        help_text="Total credits for the course"
    )
    duration_years = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Duration of the course in years"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the course"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['department__code', 'code']


class Subject(models.Model):
    """
    Model representing a subject within a course.
    
    Each subject belongs to a specific course and semester.
    """
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
        (9, 'Semester 9'),
        (10, 'Semester 10'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Full name of the subject"
    )
    code = models.CharField(
        max_length=15,
        help_text="Subject code (e.g., 'CS101', 'MATH201')"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Course this subject belongs to"
    )
    semester = models.PositiveIntegerField(
        choices=SEMESTER_CHOICES,
        help_text="Semester in which this subject is taught"
    )
    credits = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=3,
        help_text="Credits for this subject"
    )
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Whether this subject is mandatory or elective"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the subject"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name} (Sem {self.semester})"
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        unique_together = ['code', 'course']
        ordering = ['course__code', 'semester', 'code']


class Timetable(models.Model):
    """
    Model representing a timetable entry for a class.
    
    Each timetable entry specifies when and where a subject is taught.
    """
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    class_name = models.CharField(
        max_length=50,
        help_text="Name/identifier of the class (e.g., 'CSE-A', 'ECE-B')"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Subject being taught in this time slot"
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
        help_text="Day of the week for this class"
    )
    start_time = models.TimeField(
        help_text="Start time of the class"
    )
    end_time = models.TimeField(
        help_text="End time of the class"
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Room number where the class is held"
    )
    academic_year = models.CharField(
        max_length=10,
        help_text="Academic year (e.g., '2024-25')"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this timetable entry is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.class_name} - {self.subject.code} ({self.day_of_week} {self.start_time}-{self.end_time})"
    
    def clean(self):
        """Validate that end_time is after start_time."""
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
    
    class Meta:
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"
        unique_together = [
            ['class_name', 'day_of_week', 'start_time', 'academic_year'],
            ['subject', 'class_name', 'day_of_week', 'start_time', 'academic_year']
        ]
        ordering = ['day_of_week', 'start_time', 'class_name']
