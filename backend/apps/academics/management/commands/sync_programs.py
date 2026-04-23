"""
Django management command to sync Programs with Courses.

Usage:
    python manage.py sync_programs
"""
from django.core.management.base import BaseCommand
from apps.academics.models import Department, Program, Course


class Command(BaseCommand):
    help = 'Syncs Program entries with Course entries'

    def handle(self, *args, **options):
        self.stdout.write('Syncing Programs with Courses...\n')

        try:
            # Get all courses
            courses = Course.objects.all()
            
            for course in courses:
                program, created = Program.objects.get_or_create(
                    code=course.code,
                    defaults={
                        'name': course.name,
                        'department': course.department,
                        'duration_years': course.duration_years,
                        'duration_semesters': course.duration_years * 2,
                        'total_credits': course.credits,
                        'description': course.description,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created program: {program.code} - {program.name}'))
                else:
                    # Update existing program
                    program.name = course.name
                    program.department = course.department
                    program.duration_years = course.duration_years
                    program.duration_semesters = course.duration_years * 2
                    program.total_credits = course.credits
                    program.description = course.description
                    program.save()
                    self.stdout.write(self.style.WARNING(f'✓ Updated program: {program.code} - {program.name}'))
            
            # List all programs
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Current Programs:')
            self.stdout.write('='*60)
            for program in Program.objects.all().order_by('department__code', 'code'):
                self.stdout.write(
                    f'  {program.code}: {program.name}\n'
                    f'    Department: {program.department.code} - {program.department.name}\n'
                    f'    Duration: {program.duration_years} years ({program.duration_semesters} semesters)\n'
                    f'    Credits: {program.total_credits}\n'
                )
            
            self.stdout.write('='*60)
            self.stdout.write(self.style.SUCCESS('\nSync completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR during sync: {str(e)}'))
            raise
