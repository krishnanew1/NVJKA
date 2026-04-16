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
    
    Multi-tenant support: Uses JSONField for custom_data to store
    institution-specific fields dynamically.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text='Associated user account'
    )
    
    # Core universal fields
    reg_no = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text='Unique student registration number'
    )
    
    enrollment_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique student enrollment number (alias for reg_no)'
    )
    
    dob = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth'
    )
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text='Gender'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Residential address'
    )
    
    # Multi-tenant fields
    program = models.ForeignKey(
        'academics.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text='Academic program the student is enrolled in'
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
    
    # Custom data field for institution-specific fields
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON object storing custom registration field values (e.g., {"aadhar": "1234-5678-9012", "samagra_id": "ABC123"})'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.reg_no} - {self.user.get_full_name() or self.user.username}"
    
    def save(self, *args, **kwargs):
        # Sync enrollment_number with reg_no for backward compatibility
        if self.reg_no and not self.enrollment_number:
            self.enrollment_number = self.reg_no
        elif self.enrollment_number and not self.reg_no:
            self.reg_no = self.enrollment_number
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['-batch_year', 'reg_no']


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
from apps.users.audit_models import AuditLog
