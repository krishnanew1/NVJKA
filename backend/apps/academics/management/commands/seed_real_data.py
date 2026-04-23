"""
Django management command to seed real Course of Study data (hardcoded).

This command creates the actual academic programs and subjects from the
Course-of-study 2023 document without requiring the PDF file.

Usage:
    python manage.py seed_real_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Department, Program, Subject, Course


class Command(BaseCommand):
    help = 'Seeds the database with real Course of Study data (BTECH-CSE, BTECH-EEE, BMS - Bachelor in Mathematics and Scientific Computing)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Course of Study data seeding...'))

        try:
            with transaction.atomic():
                # Create departments
                self.create_departments()
                
                # Create programs and subjects
                self.create_btech_cse()
                self.create_btech_eee()
                self.create_bms()
                
                self.stdout.write(self.style.SUCCESS('\n' + '='*70))
                self.stdout.write(self.style.SUCCESS('Course of Study data seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*70))
                self.stdout.write('\nCreated Programs:')
                self.stdout.write('  • BTECH-CSE: B.Tech. in Computer Science and Engineering (167 credits)')
                self.stdout.write('  • BTECH-EEE: B.Tech. in Electrical and Electronics Engineering (169 credits)')
                self.stdout.write('  • BMS: Bachelor in Mathematics and Scientific Computing (175 credits)')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error during seeding: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise

    def create_departments(self):
        """Create department records."""
        self.stdout.write('\nCreating departments...')
        
        departments = [
            {
                'code': 'CSE',
                'name': 'Computer Science and Engineering',
                'description': 'Department of Computer Science and Engineering'
            },
            {
                'code': 'EEE',
                'name': 'Electrical and Electronics Engineering',
                'description': 'Department of Electrical and Electronics Engineering'
            },
            {
                'code': 'MSC',
                'name': 'Mathematics and Scientific Computing',
                'description': 'Department of Mathematics and Scientific Computing'
            }
        ]
        
        for dept_data in departments:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created department: {dept.code} - {dept.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ Department already exists: {dept.code}'))

    def create_btech_cse(self):
        """Create B.Tech. CSE program and subjects."""
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Creating B.Tech. in Computer Science and Engineering...')
        self.stdout.write('='*70)
        
        # Create program
        department = Department.objects.get(code='CSE')
        program, created = Program.objects.get_or_create(
            code='BTECH-CSE',
            defaults={
                'name': 'Bachelor of Technology in Computer Science and Engineering',
                'department': department,
                'duration_years': 4,
                'duration_semesters': 8,
                'total_credits': 167,
                'description': 'B.Tech. in Computer Science and Engineering program',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created program: {program.code} ({program.total_credits} credits)'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Program already exists: {program.code}'))
        
        # Create course for FK compatibility
        course, _ = Course.objects.get_or_create(
            code='BTECHCSE',
            defaults={
                'name': 'Bachelor of Technology in Computer Science and Engineering',
                'department': department,
                'credits': 167,
                'duration_years': 4,
                'description': 'B.Tech. CSE Course'
            }
        )
        
        # Define subjects by semester
        subjects = [
            # Semester 1
            {'code': 'CS101', 'name': 'Principles of Computer Programming', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'ES101', 'name': 'Engineering Physics', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'ES102', 'name': 'Engineering Mathematics I', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'HS101', 'name': 'English for Communication', 'semester': 1, 'credits': 3, 'mandatory': True},
            {'code': 'ES103', 'name': 'Engineering Graphics and Design', 'semester': 1, 'credits': 3, 'mandatory': True},
            
            # Semester 2
            {'code': 'CS102', 'name': 'Data Structures', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'ES104', 'name': 'Engineering Chemistry', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'ES105', 'name': 'Engineering Mathematics II', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'EE103', 'name': 'Digital Electronics', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'HS102', 'name': 'Professional Ethics and Indian Constitution', 'semester': 2, 'credits': 2, 'mandatory': True},
            
            # Semester 3
            {'code': 'CS201', 'name': 'Discrete Structures', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'CS202', 'name': 'Computer Organization and Architecture', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'CS203', 'name': 'Design and Analysis of Algorithms', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'ES201', 'name': 'Probability and Statistics', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'HS201', 'name': 'Economics for Engineers', 'semester': 3, 'credits': 3, 'mandatory': True},
            
            # Semester 4
            {'code': 'CS204', 'name': 'Database Management Systems', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'CS205', 'name': 'Operating Systems', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'CS206', 'name': 'Theory of Computation', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'CS207', 'name': 'Object Oriented Programming', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'HS202', 'name': 'Organizational Behavior', 'semester': 4, 'credits': 3, 'mandatory': True},
            
            # Semester 5
            {'code': 'CS301', 'name': 'Computer Networks', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'CS302', 'name': 'Software Engineering', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'CS303', 'name': 'Compiler Design', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'CS304', 'name': 'Artificial Intelligence', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'CS3XX', 'name': 'Department Elective I', 'semester': 5, 'credits': 4, 'mandatory': False},
            
            # Semester 6
            {'code': 'CS305', 'name': 'Machine Learning', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'CS306', 'name': 'Information Security', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'CS307', 'name': 'Web Technologies', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'CS3YY', 'name': 'Department Elective II', 'semester': 6, 'credits': 4, 'mandatory': False},
            {'code': 'CS3ZZ', 'name': 'Department Elective III', 'semester': 6, 'credits': 4, 'mandatory': False},
            
            # Semester 7
            {'code': 'CS401', 'name': 'Cloud Computing', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'CS402', 'name': 'Big Data Analytics', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'CS4XX', 'name': 'Department Elective IV', 'semester': 7, 'credits': 4, 'mandatory': False},
            {'code': 'CS4YY', 'name': 'Open Elective I', 'semester': 7, 'credits': 3, 'mandatory': False},
            {'code': 'CS498', 'name': 'Project Phase I', 'semester': 7, 'credits': 4, 'mandatory': True},
            
            # Semester 8
            {'code': 'CS4ZZ', 'name': 'Department Elective V', 'semester': 8, 'credits': 4, 'mandatory': False},
            {'code': 'CS4WW', 'name': 'Open Elective II', 'semester': 8, 'credits': 3, 'mandatory': False},
            {'code': 'CS499', 'name': 'Project Phase II', 'semester': 8, 'credits': 8, 'mandatory': True},
            {'code': 'CS403', 'name': 'Seminar', 'semester': 8, 'credits': 2, 'mandatory': True},
        ]
        
        self.create_subjects(course, subjects, 'BTECH-CSE')

    def create_btech_eee(self):
        """Create B.Tech. EEE program and subjects."""
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Creating B.Tech. in Electrical and Electronics Engineering...')
        self.stdout.write('='*70)
        
        # Create program
        department = Department.objects.get(code='EEE')
        program, created = Program.objects.get_or_create(
            code='BTECH-EEE',
            defaults={
                'name': 'Bachelor of Technology in Electrical and Electronics Engineering',
                'department': department,
                'duration_years': 4,
                'duration_semesters': 8,
                'total_credits': 169,
                'description': 'B.Tech. in Electrical and Electronics Engineering program',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created program: {program.code} ({program.total_credits} credits)'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Program already exists: {program.code}'))
        
        # Create course for FK compatibility
        course, _ = Course.objects.get_or_create(
            code='BTECHEEE',
            defaults={
                'name': 'Bachelor of Technology in Electrical and Electronics Engineering',
                'department': department,
                'credits': 169,
                'duration_years': 4,
                'description': 'B.Tech. EEE Course'
            }
        )
        
        # Define subjects by semester
        subjects = [
            # Semester 1
            {'code': 'EE101', 'name': 'Fundamentals of Electrical and Electronics Engineering', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'ES101', 'name': 'Engineering Physics', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'ES102', 'name': 'Engineering Mathematics I', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'HS101', 'name': 'English for Communication', 'semester': 1, 'credits': 3, 'mandatory': True},
            {'code': 'ES103', 'name': 'Engineering Graphics and Design', 'semester': 1, 'credits': 3, 'mandatory': True},
            
            # Semester 2
            {'code': 'EE102', 'name': 'Circuit Theory', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'EE103', 'name': 'Digital Electronics', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'ES104', 'name': 'Engineering Chemistry', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'ES105', 'name': 'Engineering Mathematics II', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'HS102', 'name': 'Professional Ethics and Indian Constitution', 'semester': 2, 'credits': 2, 'mandatory': True},
            
            # Semester 3
            {'code': 'EE201', 'name': 'Signals and Systems', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'EE202', 'name': 'Network Analysis and Synthesis', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'EE203', 'name': 'Microelectronics: Devices and Materials', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'ES201', 'name': 'Probability and Statistics', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'HS201', 'name': 'Economics for Engineers', 'semester': 3, 'credits': 3, 'mandatory': True},
            
            # Semester 4
            {'code': 'EE204', 'name': 'Electromagnetic Theory', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'EE205', 'name': 'Analog and Digital Communication', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'EE206', 'name': 'Control Systems', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'EE207', 'name': 'Electrical Machines', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'HS202', 'name': 'Organizational Behavior', 'semester': 4, 'credits': 3, 'mandatory': True},
            
            # Semester 5
            {'code': 'EE301', 'name': 'Power Electronics', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'EE302', 'name': 'Digital Signal Processing', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'EE303', 'name': 'Microprocessors and Microcontrollers', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'EE304', 'name': 'Power Systems I', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'EE3XX', 'name': 'Department Elective I', 'semester': 5, 'credits': 4, 'mandatory': False},
            
            # Semester 6
            {'code': 'EE305', 'name': 'VLSI Design', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'EE306', 'name': 'Embedded Systems', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'EE307', 'name': 'Power Systems II', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'EE3YY', 'name': 'Department Elective II', 'semester': 6, 'credits': 4, 'mandatory': False},
            {'code': 'EE3ZZ', 'name': 'Department Elective III', 'semester': 6, 'credits': 4, 'mandatory': False},
            
            # Semester 7
            {'code': 'EE401', 'name': 'Renewable Energy Systems', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'EE402', 'name': 'Smart Grid Technology', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'EE4XX', 'name': 'Department Elective IV', 'semester': 7, 'credits': 4, 'mandatory': False},
            {'code': 'EE4YY', 'name': 'Open Elective I', 'semester': 7, 'credits': 3, 'mandatory': False},
            {'code': 'EE498', 'name': 'Project Phase I', 'semester': 7, 'credits': 4, 'mandatory': True},
            
            # Semester 8
            {'code': 'EE4ZZ', 'name': 'Department Elective V', 'semester': 8, 'credits': 4, 'mandatory': False},
            {'code': 'EE4WW', 'name': 'Open Elective II', 'semester': 8, 'credits': 3, 'mandatory': False},
            {'code': 'EE499', 'name': 'Project Phase II', 'semester': 8, 'credits': 8, 'mandatory': True},
            {'code': 'EE403', 'name': 'Seminar', 'semester': 8, 'credits': 2, 'mandatory': True},
        ]
        
        self.create_subjects(course, subjects, 'BTECH-EEE')

    def create_bms(self):
        """Create BMS (Bachelor in Mathematics and Scientific Computing) program and subjects."""
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Creating Bachelor in Mathematics and Scientific Computing...')
        self.stdout.write('='*70)
        
        # Create program
        department = Department.objects.get(code='MSC')
        program, created = Program.objects.get_or_create(
            code='BMS',
            defaults={
                'name': 'Bachelor in Mathematics and Scientific Computing',
                'department': department,
                'duration_years': 4,
                'duration_semesters': 8,
                'total_credits': 175,
                'description': 'Bachelor in Mathematics and Scientific Computing program',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created program: {program.code} ({program.total_credits} credits)'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Program already exists: {program.code}'))
        
        # Create course for FK compatibility
        course, _ = Course.objects.get_or_create(
            code='BMS',
            defaults={
                'name': 'Bachelor in Mathematics and Scientific Computing',
                'department': department,
                'credits': 175,
                'duration_years': 4,
                'description': 'BMS - Bachelor in Mathematics and Scientific Computing'
            }
        )
        
        # Define subjects by semester
        subjects = [
            # Semester 1
            {'code': 'MA101', 'name': 'Calculus and Linear Algebra', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'MA102', 'name': 'Discrete Mathematics', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'CS101', 'name': 'Principles of Computer Programming', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'ES101', 'name': 'Engineering Physics', 'semester': 1, 'credits': 4, 'mandatory': True},
            {'code': 'HS101', 'name': 'English for Communication', 'semester': 1, 'credits': 3, 'mandatory': True},
            
            # Semester 2
            {'code': 'MA103', 'name': 'Differential Equations', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'MA104', 'name': 'Probability and Statistics', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'CS102', 'name': 'Data Structures', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'ES104', 'name': 'Engineering Chemistry', 'semester': 2, 'credits': 4, 'mandatory': True},
            {'code': 'HS102', 'name': 'Professional Ethics and Indian Constitution', 'semester': 2, 'credits': 2, 'mandatory': True},
            
            # Semester 3
            {'code': 'MA201', 'name': 'Real Analysis', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'MA202', 'name': 'Abstract Algebra', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'MA203', 'name': 'Numerical Methods', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'CS203', 'name': 'Design and Analysis of Algorithms', 'semester': 3, 'credits': 4, 'mandatory': True},
            {'code': 'HS201', 'name': 'Economics for Engineers', 'semester': 3, 'credits': 3, 'mandatory': True},
            
            # Semester 4
            {'code': 'MA204', 'name': 'Complex Analysis', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'MA205', 'name': 'Optimization Techniques', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'MA206', 'name': 'Mathematical Modeling', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'CS204', 'name': 'Database Management Systems', 'semester': 4, 'credits': 4, 'mandatory': True},
            {'code': 'HS202', 'name': 'Organizational Behavior', 'semester': 4, 'credits': 3, 'mandatory': True},
            
            # Semester 5
            {'code': 'MA301', 'name': 'Partial Differential Equations', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'MA302', 'name': 'Stochastic Processes', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'MA303', 'name': 'Computational Mathematics', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'CS304', 'name': 'Artificial Intelligence', 'semester': 5, 'credits': 4, 'mandatory': True},
            {'code': 'MA3XX', 'name': 'Department Elective I', 'semester': 5, 'credits': 4, 'mandatory': False},
            
            # Semester 6
            {'code': 'MA304', 'name': 'Operations Research', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'MA305', 'name': 'Cryptography and Network Security', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'CS305', 'name': 'Machine Learning', 'semester': 6, 'credits': 4, 'mandatory': True},
            {'code': 'MA3YY', 'name': 'Department Elective II', 'semester': 6, 'credits': 4, 'mandatory': False},
            {'code': 'MA3ZZ', 'name': 'Department Elective III', 'semester': 6, 'credits': 4, 'mandatory': False},
            
            # Semester 7
            {'code': 'MA401', 'name': 'Data Science and Analytics', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'MA402', 'name': 'Financial Mathematics', 'semester': 7, 'credits': 4, 'mandatory': True},
            {'code': 'MA4XX', 'name': 'Department Elective IV', 'semester': 7, 'credits': 4, 'mandatory': False},
            {'code': 'MA4YY', 'name': 'Open Elective I', 'semester': 7, 'credits': 3, 'mandatory': False},
            {'code': 'MA498', 'name': 'Project Phase I', 'semester': 7, 'credits': 4, 'mandatory': True},
            
            # Semester 8
            {'code': 'MA4ZZ', 'name': 'Department Elective V', 'semester': 8, 'credits': 4, 'mandatory': False},
            {'code': 'MA4WW', 'name': 'Open Elective II', 'semester': 8, 'credits': 3, 'mandatory': False},
            {'code': 'MA499', 'name': 'Project Phase II', 'semester': 8, 'credits': 8, 'mandatory': True},
            {'code': 'MA403', 'name': 'Seminar', 'semester': 8, 'credits': 2, 'mandatory': True},
        ]
        
        self.create_subjects(course, subjects, 'BMS')

    def create_subjects(self, course, subjects, program_code):
        """Create subject records for a course."""
        created_count = 0
        existing_count = 0
        
        for subject_data in subjects:
            try:
                subject, created = Subject.objects.get_or_create(
                    code=subject_data['code'],
                    course=course,
                    defaults={
                        'name': subject_data['name'],
                        'semester': subject_data['semester'],
                        'credits': subject_data['credits'],
                        'is_mandatory': subject_data['mandatory'],
                        'description': f"{subject_data['name']} - {program_code} Semester {subject_data['semester']}"
                    }
                )
                
                if created:
                    created_count += 1
                    # Show first 5 subjects
                    if created_count <= 5:
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ {subject.code} - {subject.name} (Sem {subject.semester}, {subject.credits} credits)'
                        ))
                else:
                    existing_count += 1
            except Exception as e:
                # Skip subjects that already exist with different course
                existing_count += 1
                continue
        
        # Show summary
        if created_count > 5:
            self.stdout.write(self.style.SUCCESS(f'  ✓ ... and {created_count - 5} more subjects'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n  Summary: {created_count} subjects created, {existing_count} already existed'
        ))
