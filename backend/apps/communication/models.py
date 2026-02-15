from django.db import models
from django.core.validators import FileExtensionValidator
from apps.users.models import CustomUser
from apps.academics.models import Subject


class Notice(models.Model):
    """
    Notice/Announcement model for broadcasting information to users.
    
    Notices can be targeted to specific audiences (all users, students only, or faculty only).
    """
    
    AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('STUDENTS', 'Students Only'),
        ('FACULTY', 'Faculty Only'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text='Title of the notice'
    )
    
    content = models.TextField(
        help_text='Main content/body of the notice'
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notices_created',
        help_text='User who created this notice (typically admin or faculty)'
    )
    
    audience = models.CharField(
        max_length=10,
        choices=AUDIENCE_CHOICES,
        default='ALL',
        help_text='Target audience for this notice'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this notice is currently active/visible'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Low'),
            ('NORMAL', 'Normal'),
            ('HIGH', 'High'),
            ('URGENT', 'Urgent'),
        ],
        default='NORMAL',
        help_text='Priority level of the notice'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Optional expiration date/time for the notice'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['audience', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_audience_display()})"
    
    def is_visible_to_user(self, user):
        """
        Check if this notice is visible to a specific user.
        
        Args:
            user: CustomUser instance
            
        Returns:
            bool: True if notice should be visible to the user
        """
        if not self.is_active:
            return False
        
        # Check expiration
        if self.expires_at:
            from django.utils import timezone
            if timezone.now() > self.expires_at:
                return False
        
        # Check audience
        if self.audience == 'ALL':
            return True
        elif self.audience == 'STUDENTS' and user.role == 'STUDENT':
            return True
        elif self.audience == 'FACULTY' and user.role == 'FACULTY':
            return True
        
        return False


class Resource(models.Model):
    """
    Learning Resource model for file uploads related to subjects.
    
    Faculty can upload study materials, assignments, notes, etc. for their subjects.
    """
    
    RESOURCE_TYPE_CHOICES = [
        ('NOTES', 'Lecture Notes'),
        ('ASSIGNMENT', 'Assignment'),
        ('REFERENCE', 'Reference Material'),
        ('SLIDES', 'Presentation Slides'),
        ('VIDEO', 'Video Link'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text='Title/name of the resource'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Description of the resource content'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='resources',
        help_text='Subject this resource belongs to'
    )
    
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='resources_uploaded',
        help_text='User who uploaded this resource (typically faculty)'
    )
    
    file = models.FileField(
        upload_to='resources/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'pdf', 'doc', 'docx', 'ppt', 'pptx', 
                    'xls', 'xlsx', 'txt', 'zip', 'rar',
                    'jpg', 'jpeg', 'png', 'mp4', 'avi'
                ]
            )
        ],
        help_text='File upload (PDF, DOC, PPT, images, videos, etc.)'
    )
    
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        default='NOTES',
        help_text='Type of resource'
    )
    
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='File size in bytes'
    )
    
    download_count = models.IntegerField(
        default=0,
        help_text='Number of times this resource has been downloaded'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this resource is currently available'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Learning Resource'
        verbose_name_plural = 'Learning Resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', '-created_at']),
            models.Index(fields=['uploaded_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject.code}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set file_size."""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Get the file extension."""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return None
    
    def increment_download_count(self):
        """Increment the download counter."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_file_size_display(self):
        """Get human-readable file size."""
        if not self.file_size:
            return "Unknown"
        
        # Convert bytes to appropriate unit
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

