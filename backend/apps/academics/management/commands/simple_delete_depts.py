"""
Django management command to safely delete departments using raw SQL.

Usage:
    python manage.py simple_delete_depts --codes MATH CS
"""
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Safely deletes departments using raw SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--codes',
            nargs='+',
            type=str,
            help='Department codes to delete (e.g., MATH CS)',
            required=True
        )

    def handle(self, *args, **options):
        dept_codes = options['codes']
        self.stdout.write(f'Starting deletion of departments: {", ".join(dept_codes)}...')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Get the department IDs
                    placeholders = ', '.join(['%s'] * len(dept_codes))
                    cursor.execute(
                        f"SELECT id, code, name FROM academics_department WHERE code IN ({placeholders})",
                        dept_codes
                    )
                    departments = cursor.fetchall()
                    
                    if not departments:
                        self.stdout.write(self.style.WARNING(f'No departments found with codes: {", ".join(dept_codes)}'))
                        return
                    
                    for dept_id, dept_code, dept_name in departments:
                        self.stdout.write(f'\nDeleting department: {dept_code} - {dept_name}')
                        
                        # Step 1: Get all faculty IDs in this department
                        cursor.execute("SELECT id FROM users_facultyprofile WHERE department_id = %s", [dept_id])
                        faculty_ids = [row[0] for row in cursor.fetchall()]
                        
                        # Step 2: Clear all faculty references from ALL subjects (not just this department)
                        if faculty_ids:
                            placeholders = ', '.join(['%s'] * len(faculty_ids))
                            cursor.execute(f"""
                                UPDATE academics_subject 
                                SET faculty_id = NULL 
                                WHERE faculty_id IN ({placeholders})
                            """, faculty_ids)
                            if cursor.rowcount > 0:
                                self.stdout.write(f'  Cleared faculty references from {cursor.rowcount} subjects')
                        
                        # Step 3: Get courses for this department
                        cursor.execute("SELECT id, code FROM academics_course WHERE department_id = %s", [dept_id])
                        courses = cursor.fetchall()
                        self.stdout.write(f'  Found {len(courses)} courses')
                        
                        for course_id, course_code in courses:
                            self.stdout.write(f'    Processing course: {course_code}')
                            
                            # Get subjects for this course
                            cursor.execute("SELECT id, code FROM academics_subject WHERE course_id = %s", [course_id])
                            subjects = cursor.fetchall()
                            self.stdout.write(f'      Found {len(subjects)} subjects')
                            
                            for subject_id, subject_code in subjects:
                                self.stdout.write(f'        Deleting subject: {subject_code}')
                                
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
                                            self.stdout.write(f'          Deleted {count} records from {table}')
                                    except Exception as e:
                                        self.stdout.write(self.style.WARNING(f'          Could not delete from {table}: {e}'))
                                
                                # Delete the subject
                                cursor.execute("DELETE FROM academics_subject WHERE id = %s", [subject_id])
                            
                            # Delete enrollments for this course
                            cursor.execute("DELETE FROM students_enrollment WHERE course_id = %s", [course_id])
                            enroll_count = cursor.rowcount
                            if enroll_count > 0:
                                self.stdout.write(f'      Deleted {enroll_count} enrollments')
                            
                            # Delete the course
                            cursor.execute("DELETE FROM academics_course WHERE id = %s", [course_id])
                        
                        # Delete the department
                        # First, delete faculty and student profiles that reference this department
                        cursor.execute("DELETE FROM users_facultyprofile WHERE department_id = %s", [dept_id])
                        faculty_count = cursor.rowcount
                        if faculty_count > 0:
                            self.stdout.write(f'  Deleted {faculty_count} faculty profiles')
                        
                        cursor.execute("DELETE FROM users_studentprofile WHERE department_id = %s", [dept_id])
                        student_count = cursor.rowcount
                        if student_count > 0:
                            self.stdout.write(f'  Deleted {student_count} student profiles')
                        
                        cursor.execute("DELETE FROM academics_department WHERE id = %s", [dept_id])
                        self.stdout.write(self.style.SUCCESS(f'  Deleted department: {dept_code}'))
                    
                    self.stdout.write('\n' + '='*60)
                    self.stdout.write(self.style.SUCCESS('Deletion completed successfully!'))
                    self.stdout.write('='*60)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR during deletion: {str(e)}'))
            raise
