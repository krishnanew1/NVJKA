"""
Signal handlers for automatic profile creation.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, StudentProfile, FacultyProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a profile when a new user is created.
    Creates StudentProfile for STUDENT role and FacultyProfile for FACULTY role.
    
    Note: For FACULTY users, department must be set manually after creation
    since it's a required field. The profile creation will be skipped if
    department cannot be determined automatically.
    """
    if created:
        if instance.role == 'STUDENT':
            StudentProfile.objects.create(
                user=instance,
                enrollment_number=f"TEMP_{instance.id}",  # Temporary, should be updated
                batch_year=2026  # Default, should be updated
            )
        elif instance.role == 'FACULTY':
            # Note: FacultyProfile requires a department (non-nullable)
            # This will need to be created manually or via admin/API
            # with proper department assignment
            pass


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile when the user is saved.
    This ensures profile changes are persisted.
    """
    if instance.role == 'STUDENT' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'FACULTY' and hasattr(instance, 'faculty_profile'):
        instance.faculty_profile.save()
