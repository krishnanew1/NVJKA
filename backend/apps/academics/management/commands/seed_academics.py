"""
Django management command to seed academic data from Course-of-study PDF.

Usage:
    python manage.py seed_academics --pdf path/to/Course-of-study-2023-Updated.pdf
    
    Or place the PDF in the backend directory and run:
    python manage.py seed_academics
"""
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academics.models import Department, Program, Subject, Course


class Command(BaseCommand):
    help = 'Seeds the database with academic programs and subjects from Course-of-study PDF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pdf',
            type=str,
            default='Course-of-study-2023-Updated.pdf',
            help='Path to the Course-of-study PDF file'
        )

    def handle(self, *args, **options):
        pdf_path = options['pdf']
        
        # Check if file exists, if not try in backend directory
        if not Path(pdf_path).exists():
            backend_path = Path(__file__).resolve().parent.parent.parent.parent.parent / pdf_path
            if backend_path.exists():
                pdf_path = str(backend_path)
            else:
                self.stdout.write(self.style.ERROR(f'\n✗ PDF file not found: {pdf_path}'))
                self.stdout.write(self.style.WARNING('Please place the PDF in the backend directory or specify the full path.'))
                return
        
        self.stdout.write(self.style.SUCCESS(f'Starting PDF parsing from: {pdf_path}'))

        try:
            import pdfplumber
        except ImportError:
            self.stdout.write(self.style.ERROR('\n✗ pdfplumber is not installed.'))
            self.stdout.write(self.style.WARNING('Please install it with: pip install pdfplumber'))
            return

        try:
            with transaction.atomic():
                # Create departments first
                self.create_departments()
                
                # Parse PDF and create programs and subjects
                self.parse_and_create_data(pdf_path)
                
                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('Academic data seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*60))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error during seeding: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise

    def parse_and_create_data(self, pdf_path):
        """Parse PDF and create programs and subjects."""
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            # Program tracking
            current_program = None
            current_program_code = None
            current_semester = None
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                # Detect program headers and create programs
                if 'B.Tech. in Computer Science and Engineering' in text and '(167 credits)' in text:
                    current_program_code = 'BTECH-CSE'
                    current_program = self.create_program(
                        name='Bachelor of Technology in Computer Science and Engineering',
                        code='BTECH-CSE',
                        department_code='CSE',
                        total_credits=167
                    )
                    current_semester = None
                
                elif 'B.Tech. in Electrical and Electronics Engineering' in text and '(169 credits)' in text:
                    current_program_code = 'BTECH-EEE'
                    current_program = self.create_program(
                        name='Bachelor of Technology in Electrical and Electronics Engineering',
                        code='BTECH-EEE',
                        department_code='EEE',
                        total_credits=169
                    )
                    current_semester = None
                
                elif 'B.Tech. in Mathematics and Scientific Computing' in text:
                    # Extract credits (175-186 range)
                    credits_match = re.search(r'\((\d+)-\d+ credits\)', text)
                    total_credits = int(credits_match.group(1)) if credits_match else 175
                    
                    current_program_code = 'BMS'
                    current_program = self.create_program(
                        name='Bachelor in Mathematics and Scientific Computing',
                        code='BMS',
                        department_code='MSC',
                        total_credits=total_credits
                    )
                    current_semester = None
                
                # Detect semester headers
                semester_patterns = [
                    r'SEMESTER\s*-?\s*(\d+)',
                    r'SEMESTER\s*-\s*(\d+)',
                    r'SEMESTER\s+(\d+)'
                ]
                
                for pattern in semester_patterns:
                    semester_match = re.search(pattern, text)
                    if semester_match:
                        current_semester = int(semester_match.group(1))
                        break
                
                # Extract subjects from tables if we have a program and semester
                if current_program and current_semester:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if table:
                            self.process_table(table, current_program_code, current_semester)
                    
                    # Also try text-based extraction as fallback
                    self.extract_subjects_from_text(text, current_program_code, current_semester)

    def process_table(self, table, program_code, semester):
        """Process a table and extract subjects."""
        if not table or len(table) < 2:
            return
        
        # Find header row to identify columns
        header_row = None
        for i, row in enumerate(table[:3]):  # Check first 3 rows for header
            if row and any(cell and ('Code' in str(cell) or 'Subject' in str(cell)) for cell in row):
                header_row = i
                break
        
        if header_row is None:
            return
        
        # Process data rows
        for row in table[header_row + 1:]:
            if not row or len(row) < 4:
                continue
            
            # Try to find course code, name, credits, L-T-P
            code = None
            name = None
            credits = None
            ltp = None
            
            for cell in row:
                if not cell:
                    continue
                
                cell_str = str(cell).strip()
                
                # Check if it's a course code (e.g., CS101, EE201, ES301)
                if re.match(r'^[A-Z]{2}\d{3}$', cell_str):
                    code = cell_str
                
                # Check if it's credits (single digit)
                elif re.match(r'^\d$', cell_str) and not credits:
                    credits = int(cell_str)
                
                # Check if it's L-T-P format
                elif re.match(r'^\d+-\d+-\d+$', cell_str):
                    ltp = cell_str
                
                # Otherwise it might be the subject name
                elif len(cell_str) > 5 and not code:
                    name = cell_str
            
            # Create subject if we have minimum required data
            if code and name and credits:
                self.create_subject(
                    code=code,
                    name=name,
                    program_code=program_code,
                    semester=semester,
                    credits=credits,
                    ltp=ltp or '3-0-0'
                )

    def extract_subjects_from_text(self, text, program_code, semester):
        """Extract subjects from text using regex patterns."""
        lines = text.split('\n')
        
        for line in lines:
            # Pattern: Sl no, Code, Subject Name, Credits, L-T-P
            # Example: 1 CS101 Principles of Computer Programming 4 3-0-2
            pattern = r'^\s*\d+\s+([A-Z]{2}\d{3})\s+(.+?)\s+(\d+)\s+(\d+-\d+-\d+)\s*$'
            
            match = re.match(pattern, line)
            
            if match:
                code = match.group(1).strip()
                name = match.group(2).strip()
                credits = int(match.group(3))
                ltp = match.group(4).strip()
                
                # Skip headers and totals
                if any(skip in name.upper() for skip in ['TOTAL', 'SEMESTER', 'EXIT', 'MOOC', 'OPTIONAL']):
                    continue
                
                self.create_subject(
                    code=code,
                    name=name,
                    program_code=program_code,
                    semester=semester,
                    credits=credits,
                    ltp=ltp
                )

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
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created department: {dept.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ Department already exists: {dept.code}'))

    def create_program(self, name, code, department_code, total_credits):
        """Create a program record."""
        try:
            department = Department.objects.get(code=department_code)
            
            program, created = Program.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'department': department,
                    'duration_years': 4,
                    'duration_semesters': 8,
                    'total_credits': total_credits,
                    'description': f'{name} program',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Created program: {program.code} ({program.total_credits} credits)'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'\n⚠ Program already exists: {program.code}'
                ))
            
            # Create a default course for this program (for Subject FK compatibility)
            course, _ = Course.objects.get_or_create(
                code=f'{code}-COURSE',
                defaults={
                    'name': f'{name} Course',
                    'department': department,
                    'credits': total_credits,
                    'duration_years': 4,
                    'description': f'Course for {name}'
                }
            )
            
            return program
            
        except Department.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'✗ Department not found: {department_code}'
            ))
            return None

    def create_subject(self, code, name, program_code, semester, credits, ltp):
        """Create a subject record."""
        try:
            # Get the course for this program
            course = Course.objects.get(code=f'{program_code}-COURSE')
            
            # Determine if mandatory
            is_mandatory = not any(keyword in name for keyword in ['Elective', 'MOOC', 'Optional'])
            
            # Create subject
            subject, created = Subject.objects.get_or_create(
                code=code,
                course=course,
                defaults={
                    'name': name,
                    'semester': semester,
                    'credits': credits,
                    'is_mandatory': is_mandatory,
                    'description': f'{name} - {ltp} (Lecture-Tutorial-Practical)'
                }
            )
            
            if created:
                # Only show first few subjects to avoid clutter
                if Subject.objects.filter(course=course).count() <= 5:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {subject.code} - {subject.name} (Sem {subject.semester}, {subject.credits} credits)'
                    ))
            
        except Course.DoesNotExist:
            pass  # Silently skip if course doesn't exist
        except Exception as e:
            # Silently skip duplicates and other errors
            pass
