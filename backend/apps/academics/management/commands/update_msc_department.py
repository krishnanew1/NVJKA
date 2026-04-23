"""
Django management command to update MSC/BMS program and department names.

Usage:
    python manage.py update_msc_department
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Department, Program, Course


class Command(BaseCommand):
    help = 'Updates BMS program name to Bachelor in Mathematics and Scientific Computing'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('='*70)
        self.stdout.write('Updating BMS Program Name')
        self.stdout.write('='*70)
        
        try:
            # Find BMS program
            program = Program.objects.get(code='BMS')
            
            old_name = program.name
            new_name = 'Bachelor in Mathematics and Scientific Computing'
            
            if old_name == new_name:
                self.stdout.write(self.style.SUCCESS(f'✓ Program name is already correct: {new_name}'))
            else:
                program.name = new_name
                program.description = 'Bachelor in Mathematics and Scientific Computing program'
                program.save()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Updated program name'))
                self.stdout.write(f'  Old: {old_name}')
                self.stdout.write(f'  New: {new_name}')
            
            # Also update the Course if it exists
            try:
                course = Course.objects.get(code='BMS')
                if course.name != new_name:
                    course.name = new_name
                    course.description = 'BMS - Bachelor in Mathematics and Scientific Computing'
                    course.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated course name as well'))
            except Course.DoesNotExist:
                pass
            
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS('BMS program update completed!'))
            self.stdout.write('='*70)
            
        except Program.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ BMS program not found in database'))
            self.stdout.write('  Run: python manage.py seed_real_data')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
