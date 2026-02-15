from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser with additional fields
    for the Academic ERP system.
    """
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('FACULTY', 'Faculty Member'),
        ('STUDENT', 'Student'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        help_text='User role in the academic system'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text='User address'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class StudentProfile(models.Model):
    """
    Student profile model with academic information.
    Links to CustomUser with OneToOne relationship.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text='Associated user account'
    )
    
    enrollment_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique student enrollment number'
    )
    
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text='Student department'
    )
    
    current_semester = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Current semester number'
    )
    
    batch_year = models.IntegerField(
        help_text='Year of admission/batch (e.g., 2026)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.enrollment_number} - {self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['-batch_year', 'enrollment_number']


class FacultyProfile(models.Model):
    """
    Faculty profile model with employment information.
    Links to CustomUser with OneToOne relationship.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        help_text='Associated user account'
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique employee identification number'
    )
    
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.CASCADE,
        related_name='faculty_members',
        help_text='Faculty department'
    )
    
    designation = models.CharField(
        max_length=100,
        help_text='Faculty designation (e.g., Professor, Lecturer, Assistant Professor)'
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Area of specialization'
    )
    
    date_of_joining = models.DateField(
        null=True,
        blank=True,
        help_text='Date of joining the institution'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username} ({self.designation})"
    
    class Meta:
        verbose_name = 'Faculty Profile'
        verbose_name_plural = 'Faculty Profiles'
        ordering = ['department', 'designation']


# Import audit model
from users.audit_models import AuditLog
