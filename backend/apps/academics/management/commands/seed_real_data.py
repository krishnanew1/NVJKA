"""
Django management command to seed the database with real faculty and courses.

Usage:
    python manage.py seed_real_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import FacultyProfile
from apps.academics.models import Department, Course, Subject
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with real faculty members and courses'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Starting Real Data Seeding'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Get or create Computer Science department
        dept, created = Department.objects.get_or_create(
            code='CSE',
            defaults={
                'name': 'Computer Science and Engineering',
                'description': 'Department of Computer Science and Engineering'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created department: {dept}'))
        else:
            self.stdout.write(self.style.WARNING(f'→ Department already exists: {dept}'))

        # Get or create B.Tech CSE course
        course, created = Course.objects.get_or_create(
            code='BTECH-CSE',
            defaults={
                'name': 'Bachelor of Technology in Computer Science',
                'department': dept,
                'credits': 160,
                'duration_years': 4,
                'description': 'Four-year undergraduate program in Computer Science'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course}'))
        else:
            self.stdout.write(self.style.WARNING(f'→ Course already exists: {course}'))

        # Create subjects
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Creating Subjects'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        subjects_data = [
            {
                'name': 'Multivariate Data Analysis',
                'code': 'CS401',
                'semester': 4,
                'credits': 4,
                'description': 'Advanced statistical methods for analyzing multivariate data'
            },
            {
                'name': 'Operating Systems',
                'code': 'CS301',
                'semester': 3,
                'credits': 4,
                'description': 'Fundamentals of operating system design and implementation'
            },
            {
                'name': 'Advanced Numerical Methods',
                'code': 'CS402',
                'semester': 4,
                'credits': 4,
                'description': 'Advanced computational techniques for solving numerical problems'
            },
            {
                'name': 'Software Engineering',
                'code': 'CS302',
                'semester': 3,
                'credits': 4,
                'description': 'Principles and practices of software development'
            },
        ]

        created_subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                course=course,
                defaults={
                    'name': subject_data['name'],
                    'semester': subject_data['semester'],
                    'credits': subject_data['credits'],
                    'description': subject_data['description'],
                    'is_mandatory': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created subject: {subject}'))
                created_subjects.append(subject)
            else:
                self.stdout.write(self.style.WARNING(f'→ Subject already exists: {subject}'))
                created_subjects.append(subject)

        # Create faculty users and profiles
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Creating Faculty Members'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        faculty_data = [
            {
                'username': 'ajay_k',
                'first_name': 'Ajay',
                'last_name': 'Kumar',
                'email': 'ajay.kumar@college.edu',
                'employee_id': 'FAC101',
                'designation': 'Associate Professor',
                'specialization': 'Data Science and Machine Learning'
            },
            {
                'username': 'deepak_d',
                'first_name': 'Deepak Kumar',
                'last_name': 'Dewangan',
                'email': 'deepak.dewangan@college.edu',
                'employee_id': 'FAC102',
                'designation': 'Assistant Professor',
                'specialization': 'Operating Systems and Computer Architecture'
            },
            {
                'username': 'anuraj_s',
                'first_name': 'Anuraj',
                'last_name': 'Singh',
                'email': 'anuraj.singh@college.edu',
                'employee_id': 'FAC103',
                'designation': 'Assistant Professor',
                'specialization': 'Numerical Computing and Scientific Programming'
            },
            {
                'username': 'anurag_s',
                'first_name': 'Anurag',
                'last_name': 'Srivastav',
                'email': 'anurag.srivastav@college.edu',
                'employee_id': 'FAC104',
                'designation': 'Associate Professor',
                'specialization': 'Software Engineering and Project Management'
            },
        ]

        created_faculty = []
        for faculty_info in faculty_data:
            # Create or get user
            user, user_created = User.objects.get_or_create(
                username=faculty_info['username'],
                defaults={
                    'first_name': faculty_info['first_name'],
                    'last_name': faculty_info['last_name'],
                    'email': faculty_info['email'],
                    'role': 'FACULTY',
                    'is_staff': False,
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password('faculty123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'→ User already exists: {user.username}'))

            # Create or get faculty profile
            try:
                faculty_profile = FacultyProfile.objects.get(user=user)
                self.stdout.write(self.style.WARNING(
                    f'  → Faculty profile already exists: {faculty_profile.user.get_full_name()}'
                ))
            except FacultyProfile.DoesNotExist:
                faculty_profile = FacultyProfile.objects.create(
                    user=user,
                    employee_id=faculty_info['employee_id'],
                    department=dept,
                    designation=faculty_info['designation'],
                    specialization=faculty_info['specialization'],
                    date_of_joining=date(2020, 7, 1)
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Created faculty profile: {faculty_profile.user.get_full_name()} '
                    f'({faculty_profile.employee_id})'
                ))
            
            created_faculty.append(faculty_profile)

        # Assign faculty to subjects (optional - can be done via API later)
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Faculty-Subject Assignment'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Map subjects to faculty based on specialization
        subject_faculty_mapping = {
            'CS401': created_faculty[0],  # Multivariate Data Analysis -> Ajay Kumar
            'CS301': created_faculty[1],  # Operating Systems -> Deepak Kumar Dewangan
            'CS402': created_faculty[2],  # Advanced Numerical Methods -> Anuraj Singh
            'CS302': created_faculty[3],  # Software Engineering -> Anurag Srivastav
        }

        for subject in created_subjects:
            if subject.code in subject_faculty_mapping:
                faculty = subject_faculty_mapping[subject.code]
                subject.faculty = faculty
                subject.save()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Assigned {faculty.user.get_full_name()} to {subject.name}'
                ))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Seeding Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'Department: {dept.name}'))
        self.stdout.write(self.style.SUCCESS(f'Course: {course.name}'))
        self.stdout.write(self.style.SUCCESS(f'Subjects Created: {len(created_subjects)}'))
        self.stdout.write(self.style.SUCCESS(f'Faculty Members Created: {len(created_faculty)}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Faculty Login Credentials'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        for faculty_info in faculty_data:
            self.stdout.write(self.style.SUCCESS(
                f'Username: {faculty_info["username"]} | Password: faculty123'
            ))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✓ Real data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
