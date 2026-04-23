"""
Django management command to seed the database with demo data.

Usage:
    python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import CustomUser, FacultyProfile, StudentProfile
from apps.academics.models import Department, Course, Subject
from apps.faculty.models import ClassAssignment
from apps.attendance.models import Attendance


class Command(BaseCommand):
    help = 'Seeds the database with demo users, departments, courses, and assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        try:
            with transaction.atomic():
                # Create Departments
                self.stdout.write('Creating departments...')
                cs_dept, _ = Department.objects.get_or_create(
                    code='CS',
                    defaults={
                        'name': 'Computer Science',
                        'description': 'Department of Computer Science and Engineering'
                    }
                )
                
                math_dept, _ = Department.objects.get_or_create(
                    code='MATH',
                    defaults={
                        'name': 'Mathematics',
                        'description': 'Department of Mathematics'
                    }
                )
                
                self.stdout.write(self.style.SUCCESS(f'OK Created departments: {cs_dept.code}, {math_dept.code}'))

                # Create Courses
                self.stdout.write('Creating courses...')
                btech_cs, _ = Course.objects.get_or_create(
                    code='BTECH-CS',
                    defaults={
                        'name': 'Bachelor of Technology in Computer Science',
                        'department': cs_dept,
                        'duration_years': 4,
                        'credits': 160
                    }
                )
                
                msc_math, _ = Course.objects.get_or_create(
                    code='MSC-MATH',
                    defaults={
                        'name': 'Master of Science in Mathematics',
                        'department': math_dept,
                        'duration_years': 2,
                        'credits': 80
                    }
                )
                
                self.stdout.write(self.style.SUCCESS(f'OK Created courses: {btech_cs.code}, {msc_math.code}'))

                # Create Subjects
                self.stdout.write('Creating subjects...')
                ds_subject, _ = Subject.objects.get_or_create(
                    code='CS101',
                    course=btech_cs,
                    defaults={
                        'name': 'Data Structures',
                        'semester': 3,
                        'credits': 4,
                        'is_mandatory': True,
                        'description': 'Introduction to fundamental data structures and algorithms'
                    }
                )
                
                algo_subject, _ = Subject.objects.get_or_create(
                    code='CS201',
                    course=btech_cs,
                    defaults={
                        'name': 'Algorithm Design',
                        'semester': 4,
                        'credits': 4,
                        'is_mandatory': True,
                        'description': 'Advanced algorithm design and analysis'
                    }
                )
                
                db_subject, _ = Subject.objects.get_or_create(
                    code='CS301',
                    course=btech_cs,
                    defaults={
                        'name': 'Database Management Systems',
                        'semester': 5,
                        'credits': 4,
                        'is_mandatory': True,
                        'description': 'Relational databases, SQL, and database design'
                    }
                )
                
                self.stdout.write(self.style.SUCCESS(f'OK Created subjects: {ds_subject.code}, {algo_subject.code}, {db_subject.code}'))

                # Create Users
                self.stdout.write('Creating users...')
                
                # Admin user
                admin_user, created = CustomUser.objects.get_or_create(
                    username='admin_demo',
                    defaults={
                        'email': 'admin@example.com',
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'role': 'ADMIN',
                        'is_staff': True,
                        'is_superuser': True,
                        'phone_number': '+1234567890'
                    }
                )
                if created:
                    admin_user.set_password('Admin@2026')
                    admin_user.save()
                    self.stdout.write(self.style.SUCCESS(f'OK Created admin user: {admin_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Admin user already exists: {admin_user.username}'))

                # Faculty user
                faculty_user, created = CustomUser.objects.get_or_create(
                    username='prof_smith',
                    defaults={
                        'email': 'smith@example.com',
                        'first_name': 'John',
                        'last_name': 'Smith',
                        'role': 'FACULTY',
                        'is_staff': True,
                        'phone_number': '+1234567891'
                    }
                )
                if created:
                    faculty_user.set_password('Faculty@2026')
                    faculty_user.save()
                    self.stdout.write(self.style.SUCCESS(f'OK Created faculty user: {faculty_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Faculty user already exists: {faculty_user.username}'))

                # Create Faculty Profile
                faculty_profile, created = FacultyProfile.objects.get_or_create(
                    user=faculty_user,
                    defaults={
                        'employee_id': 'FAC001',
                        'department': cs_dept,
                        'designation': 'Associate Professor',
                        'specialization': 'Data Structures and Algorithms',
                        'date_of_joining': '2020-01-15'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'OK Created faculty profile for: {faculty_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Faculty profile already exists for: {faculty_user.username}'))

                # Student user
                student_user, created = CustomUser.objects.get_or_create(
                    username='john_doe',
                    defaults={
                        'email': 'john.doe@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'STUDENT',
                        'phone_number': '+1234567892'
                    }
                )
                if created:
                    student_user.set_password('Student@2026')
                    student_user.save()
                    self.stdout.write(self.style.SUCCESS(f'OK Created student user: {student_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Student user already exists: {student_user.username}'))

                # Create Student Profile
                student_profile, created = StudentProfile.objects.get_or_create(
                    user=student_user,
                    defaults={
                        'enrollment_number': 'STU2023001',
                        'department': cs_dept,
                        'current_semester': 3,
                        'batch_year': 2023
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'OK Created student profile for: {student_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Student profile already exists for: {student_user.username}'))

                # Create Class Assignments for Faculty
                self.stdout.write('Creating class assignments...')
                
                assignment1, created = ClassAssignment.objects.get_or_create(
                    faculty=faculty_profile,
                    subject=ds_subject,
                    semester=3,
                    academic_year=2026,
                    defaults={}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'OK Assigned {ds_subject.code} to {faculty_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Assignment already exists: {ds_subject.code}'))

                assignment2, created = ClassAssignment.objects.get_or_create(
                    faculty=faculty_profile,
                    subject=algo_subject,
                    semester=4,
                    academic_year=2026,
                    defaults={}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'OK Assigned {algo_subject.code} to {faculty_user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Assignment already exists: {algo_subject.code}'))

                # Create Student Enrollment
                from apps.students.models import Enrollment
                
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student_profile,
                    course=btech_cs,
                    semester=3,
                    defaults={
                        'status': 'Active'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'OK Enrolled {student_user.username} in {btech_cs.code}'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Enrollment already exists for {student_user.username}'))

                # Create Attendance Records for Student
                self.stdout.write('Creating attendance records...')
                from datetime import date, timedelta
                
                # Create attendance for CS101 (Data Structures)
                today = date.today()
                attendance_records_created = 0
                
                # Create 10 attendance records for CS101 over the past 10 days (starting from yesterday)
                for i in range(1, 11):
                    attendance_date = today - timedelta(days=i)
                    # 80% present, 10% late, 10% absent
                    if i <= 8:
                        status = 'Present'
                    elif i == 9:
                        status = 'Late'
                    else:
                        status = 'Absent'
                    
                    attendance, created = Attendance.objects.get_or_create(
                        student=student_profile,
                        subject=ds_subject,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'recorded_by': faculty_user
                        }
                    )
                    if created:
                        attendance_records_created += 1
                
                # Create 8 attendance records for CS201 (Algorithm Design)
                for i in range(1, 9):
                    attendance_date = today - timedelta(days=i)
                    # 62.5% present (5/8), 25% late (2/8), 12.5% absent (1/8)
                    if i <= 5:
                        status = 'Present'
                    elif i <= 7:
                        status = 'Late'
                    else:
                        status = 'Absent'
                    
                    attendance, created = Attendance.objects.get_or_create(
                        student=student_profile,
                        subject=algo_subject,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'recorded_by': faculty_user
                        }
                    )
                    if created:
                        attendance_records_created += 1
                
                if attendance_records_created > 0:
                    self.stdout.write(self.style.SUCCESS(f'OK Created {attendance_records_created} attendance records'))
                else:
                    self.stdout.write(self.style.WARNING(f'WARN Attendance records already exist'))

                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*60))
                self.stdout.write('\nDemo Credentials:')
                self.stdout.write(f'  Admin:   username=admin_demo    password=Admin@2026')
                self.stdout.write(f'  Faculty: username=prof_smith    password=Faculty@2026')
                self.stdout.write(f'  Student: username=john_doe      password=Student@2026')
                self.stdout.write('\nYou can now log in with these credentials!')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR during seeding: {str(e)}'))
            raise
