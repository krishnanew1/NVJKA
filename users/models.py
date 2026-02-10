from django.db import models
from django.contrib.auth.models import AbstractUser


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
