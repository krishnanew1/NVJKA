"""
Django management command to delete all faculty entries.

Usage:
    python manage.py delete_all_faculty
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import CustomUser, FacultyProfile


class Command(BaseCommand):
    help = 'Deletes all faculty profiles and their user accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking faculty entries...\n')

        try:
            # Count faculty
            faculty_profiles = FacultyProfile.objects.all()
            faculty_users = CustomUser.objects.filter(role='FACULTY')
            
            profile_count = faculty_profiles.count()
            user_count = faculty_users.count()
            
            self.stdout.write(f'Found:')
            self.stdout.write(f'  - {profile_count} faculty profiles')
            self.stdout.write(f'  - {user_count} faculty user accounts')
            
            if profile_count == 0 and user_count == 0:
                self.stdout.write(self.style.SUCCESS('\nNo faculty entries found. Database is clean.'))
                return
            
            # Confirm deletion
            if not options['confirm']:
                self.stdout.write(self.style.WARNING('\nThis will permanently delete all faculty data!'))
                confirm = input('Are you sure you want to continue? (yes/no): ')
                if confirm.lower() != 'yes':
                    self.stdout.write(self.style.ERROR('Deletion cancelled.'))
                    return
            
            self.stdout.write('\nDeleting faculty entries...')
            
            with transaction.atomic():
                from django.db import connection
                
                with connection.cursor() as cursor:
                    # First, clear faculty references from subjects
                    cursor.execute("UPDATE academics_subject SET faculty_id = NULL WHERE faculty_id IS NOT NULL")
                    subject_count = cursor.rowcount
                    if subject_count > 0:
                        self.stdout.write(f'  ✓ Cleared faculty references from {subject_count} subjects')
                    
                    # Clear faculty references from timetables
                    try:
                        cursor.execute("UPDATE academics_timetable SET faculty_id = NULL WHERE faculty_id IS NOT NULL")
                        timetable_count = cursor.rowcount
                        if timetable_count > 0:
                            self.stdout.write(f'  ✓ Cleared faculty references from {timetable_count} timetable entries')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Could not clear timetable references: {e}'))
                    
                    # Delete faculty works
                    try:
                        cursor.execute("DELETE FROM users_facultywork")
                        work_count = cursor.rowcount
                        if work_count > 0:
                            self.stdout.write(f'  ✓ Deleted {work_count} faculty works')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Could not delete faculty works: {e}'))
                    
                    # Delete faculty profiles
                    if profile_count > 0:
                        cursor.execute("DELETE FROM users_facultyprofile")
                        deleted_profiles = cursor.rowcount
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted_profiles} faculty profiles'))
                    
                    # Delete faculty user accounts
                    if user_count > 0:
                        cursor.execute("DELETE FROM users_customuser WHERE role = 'FACULTY'")
                        deleted_users = cursor.rowcount
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted {deleted_users} faculty user accounts'))
                
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('All faculty entries deleted successfully!'))
                self.stdout.write('='*60)
                
                # Verify
                remaining_profiles = FacultyProfile.objects.count()
                remaining_users = CustomUser.objects.filter(role='FACULTY').count()
                
                if remaining_profiles == 0 and remaining_users == 0:
                    self.stdout.write(self.style.SUCCESS('\n✓ Verification: Database is clean'))
                else:
                    self.stdout.write(self.style.WARNING(f'\n⚠ Warning: {remaining_profiles} profiles and {remaining_users} users still remain'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ ERROR: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise
