"""
Django management command to safely delete courses using raw SQL.

Usage:
    python manage.py delete_courses --codes BTECH-CSE
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Safely deletes courses along with all dependent records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--codes',
            nargs='+',
            type=str,
            help='Course codes to delete (e.g., BTECH-CSE BTECH-EEE)',
            required=True
        )

    def handle(self, *args, **options):
        course_codes = options['codes']
        self.stdout.write(f'Starting deletion of courses: {", ".join(course_codes)}...')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Get the course IDs
                    placeholders = ', '.join(['%s'] * len(course_codes))
                    cursor.execute(
                        f"SELECT id, code, name FROM academics_course WHERE code IN ({placeholders})",
                        course_codes
                    )
                    courses = cursor.fetchall()
                    
                    if not courses:
                        self.stdout.write(self.style.WARNING(f'No courses found with codes: {", ".join(course_codes)}'))
                        return
                    
                    for course_id, course_code, course_name in courses:
                        self.stdout.write(f'\nDeleting course: {course_code} - {course_name}')
                        
                        # Get subjects for this course
                        cursor.execute("SELECT id, code FROM academics_subject WHERE course_id = %s", [course_id])
                        subjects = cursor.fetchall()
                        self.stdout.write(f'  Found {len(subjects)} subjects')
                        
                        for subject_id, subject_code in subjects:
                            self.stdout.write(f'    Deleting subject: {subject_code}')
                            
                            # Delete all related records for this subject
                            tables_to_clean = [
                                ('attendance_attendance', 'subject_id'),
                                ('assignments_assignmentsubmission', 'assignment_id IN (SELECT id FROM assignments_assignment WHERE subject_id = %s)'),
                                ('assignments_assignment', 'subject_id'),
                                ('exams_studentgrade', 'subject_id'),
                                ('exams_assessment', 'subject_id'),
                                ('students_registeredcourse', 'subject_id'),
                                ('academics_timetable', 'subject_id'),
                            ]
                            
                            for table, condition in tables_to_clean:
                                try:
                                    if 'IN (SELECT' in condition:
                                        cursor.execute(f"DELETE FROM {table} WHERE {condition}", [subject_id])
                                    else:
                                        cursor.execute(f"DELETE FROM {table} WHERE {condition} = %s", [subject_id])
                                    count = cursor.rowcount
                                    if count > 0:
                                        self.stdout.write(f'      Deleted {count} records from {table}')
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'      Could not delete from {table}: {e}'))
                            
                            # Delete the subject
                            cursor.execute("DELETE FROM academics_subject WHERE id = %s", [subject_id])
                        
                        # Delete enrollments for this course
                        cursor.execute("DELETE FROM students_enrollment WHERE course_id = %s", [course_id])
                        enroll_count = cursor.rowcount
                        if enroll_count > 0:
                            self.stdout.write(f'  Deleted {enroll_count} enrollments')
                        
                        # Delete the course
                        cursor.execute("DELETE FROM academics_course WHERE id = %s", [course_id])
                        self.stdout.write(self.style.SUCCESS(f'  Deleted course: {course_code}'))
                    
                    self.stdout.write('\n' + '='*60)
                    self.stdout.write(self.style.SUCCESS('Deletion completed successfully!'))
                    self.stdout.write('='*60)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR during deletion: {str(e)}'))
            raise
