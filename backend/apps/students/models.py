from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from apps.users.models import StudentProfile
from apps.academics.models import Course, Subject


class SemesterRegistration(models.Model):
    """
    Model representing a student's semester registration.
    
    Captures fee payment status, hostel details, total credits, and approval status for a semester.
    """
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='semester_registrations'
    )
    academic_year = models.CharField(
        max_length=10,
        help_text="Academic year (e.g., '2025-26')"
    )
    semester = models.CharField(
        max_length=50,
        help_text="Semester period (e.g., 'Jan-Jun 2026')"
    )
    institute_fee_paid = models.BooleanField(
        default=False,
        help_text="Whether institute fee has been paid"
    )
    hostel_fee_paid = models.BooleanField(
        default=False,
        help_text="Whether hostel fee has been paid"
    )
    hostel_room_no = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Hostel room number (if applicable)"
    )
    total_credits = models.PositiveIntegerField(
        default=0,
        help_text="Total credits registered for this semester"
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        help_text="Admin approval status for this registration"
    )
    approved_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_registrations',
        help_text="Admin who approved/rejected this registration"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when registration was approved/rejected"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Admin notes for approval/rejection"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'academic_year', 'semester')
        ordering = ['-academic_year', '-semester']
        indexes = [
            models.Index(fields=['approval_status']),
            models.Index(fields=['student', 'approval_status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} ({self.semester}) - {self.approval_status}"


class FeeTransaction(models.Model):
    """
    Model representing a fee payment transaction.
    
    Each semester registration can have up to 3 fee transactions.
    """
    semester_registration = models.ForeignKey(
        SemesterRegistration,
        on_delete=models.CASCADE,
        related_name='fee_transactions'
    )
    utr_no = models.CharField(
        max_length=50,
        help_text="Unique Transaction Reference number"
    )
    bank_name = models.CharField(
        max_length=100,
        help_text="Name of the bank"
    )
    transaction_date = models.DateField(
        help_text="Date of transaction"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Transaction amount"
    )
    account_debited = models.CharField(
        max_length=100,
        help_text="Account from which amount was debited"
    )
    account_credited = models.CharField(
        max_length=100,
        help_text="Account to which amount was credited"
    )
    receipt_image = models.ImageField(
        upload_to='fee_receipts/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        help_text="Upload fee receipt screenshot/image (JPG, PNG, or PDF)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"Transaction {self.utr_no} - {self.amount}"
    
    def clean(self):
        """Validate that a semester registration doesn't have more than 3 transactions."""
        if not self.pk:  # Only check on creation
            existing_count = FeeTransaction.objects.filter(
                semester_registration=self.semester_registration
            ).count()
            if existing_count >= 3:
                raise ValidationError(
                    'A semester registration cannot have more than 3 fee transactions.'
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class RegisteredCourse(models.Model):
    """
    Model representing a course/subject registered by a student for a semester.
    
    Links a semester registration to specific subjects with backlog tracking.
    """
    semester_registration = models.ForeignKey(
        SemesterRegistration,
        on_delete=models.CASCADE,
        related_name='registered_courses'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_registrations'
    )
    is_backlog = models.BooleanField(
        default=False,
        help_text="Whether this is a backlog subject"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('semester_registration', 'subject')
        ordering = ['is_backlog', 'subject__code']
    
    def __str__(self):
        backlog_str = " (Backlog)" if self.is_backlog else ""
        return f"{self.subject.code}{backlog_str}"


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
