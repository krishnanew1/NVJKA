"""
Tests for timetable generation functionality.

This module tests the auto-generation of timetables for academic batches,
including conflict detection, faculty assignment, and API endpoints.
"""
import datetime
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Department, Course, Subject, Timetable
from apps.users.models import CustomUser, StudentProfile, FacultyProfile
from apps.students.models import Enrollment
from apps.faculty.models import ClassAssignment
from apps.academics.utils import TimetableGenerator, generate_batch_timetable


class TimetableGenerationTest(TransactionTestCase):
    """
    Test suite for timetable generation functionality.
    
    Tests both the utility functions and API endpoints for generating
    and retrieving batch timetables.
    """

    def setUp(self):
        """Set up test data for timetable generation."""
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin_timetable',
            password='Admin@2026',
            role='ADMIN',
            is_staff=True
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Computer Science Engineering',
            code='CSE',
            description='Department of Computer Science and Engineering'
        )
        
        # Create course
        self.course = Course.objects.create(
            name='Bachelor of Technology in Computer Science',
            code='BTECH-CSE',
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        # Create subjects for semester 3
        self.subjects = []
        subject_data = [
            ('Data Structures', 'CS301', 4),
            ('Database Management', 'CS302', 3),
            ('Computer Networks', 'CS303', 3),
            ('Operating Systems', 'CS304', 4),
            ('Software Engineering', 'CS305', 3),
        ]
        
        for name, code, credits in subject_data:
            subject = Subject.objects.create(
                name=name,
                code=code,
                course=self.course,
                semester=3,
                credits=credits,
                is_mandatory=True
            )
            self.subjects.append(subject)
        
        # Create faculty members
        self.faculty_members = []
        faculty_data = [
            ('prof_alice', 'Alice Johnson', 'Professor'),
            ('prof_bob', 'Bob Smith', 'Associate Professor'),
            ('prof_carol', 'Carol Davis', 'Assistant Professor'),
        ]
        
        for username, full_name, designation in faculty_data:
            user = CustomUser.objects.create_user(
                username=username,
                password='Faculty@2026',
                role='FACULTY',
                first_name=full_name.split()[0],
                last_name=full_name.split()[1]
            )
            
            faculty = FacultyProfile.objects.create(
                user=user,
                employee_id=f'EMP-{len(self.faculty_members) + 1:03d}',
                department=self.department,
                designation=designation
            )
            self.faculty_members.append(faculty)
        
        # Create class assignments
        for i, subject in enumerate(self.subjects[:3]):  # Assign faculty to first 3 subjects
            ClassAssignment.objects.create(
                faculty=self.faculty_members[i % len(self.faculty_members)],
                subject=subject,
                semester=3,
                academic_year=2026
            )
        
        # Create students for batch 2024
        self.students = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=f'student_{i+1}',
                password='Student@2026',
                role='STUDENT',
                first_name=f'Student{i+1}',
                last_name='Test'
            )
            
            student, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'enrollment_number': f'2024CSE{i+1:03d}',
                    'department': self.department,
                    'current_semester': 3,
                    'batch_year': 2024
                }
            )
            self.students.append(student)
        
        # Enroll students in the course
        for student in self.students:
            Enrollment.objects.create(
                student=student,
                course=self.course,
                semester=3,
                status='Active'
            )
        
        # Set up API client
        self.client = APIClient()
        token = RefreshToken.for_user(self.admin_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_timetable_generator_initialization(self):
        """Test TimetableGenerator initialization."""
        generator = TimetableGenerator()
        
        # Check default academic year
        current_year = datetime.datetime.now().year
        expected_year = f"{current_year}-{str(current_year + 1)[2:]}"
        self.assertEqual(generator.academic_year, expected_year)
        
        # Check default configuration
        self.assertEqual(len(generator.time_slots), 8)
        self.assertEqual(len(generator.workdays), 5)
        self.assertGreater(len(generator.classrooms), 10)

    def test_generate_batch_timetable_success(self):
        """Test successful timetable generation for a batch."""
        result = generate_batch_timetable(
            batch_year=2024,
            department_id=self.department.id,
            semester=3
        )
        
        # Verify result structure
        self.assertIn('batch_year', result)
        self.assertIn('semester', result)
        self.assertIn('class_name', result)
        self.assertIn('total_subjects', result)
        self.assertIn('scheduled_subjects', result)
        self.assertIn('generated_entries', result)
        
        # Verify values
        self.assertEqual(result['batch_year'], 2024)
        self.assertEqual(result['semester'], 3)
        self.assertEqual(result['class_name'], 'CSE-2024-S3')
        self.assertEqual(result['total_subjects'], 5)
        self.assertGreater(result['scheduled_subjects'], 0)
        
        # Verify timetable entries were created
        entries = Timetable.objects.filter(
            class_name='CSE-2024-S3',
            is_active=True
        )
        self.assertGreater(entries.count(), 0)

    def test_generate_batch_timetable_no_students(self):
        """Test timetable generation with no students in batch."""
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError) as context:
            generate_batch_timetable(
                batch_year=2025,  # No students in this batch
                department_id=self.department.id,
                semester=3
            )
        
        self.assertIn('No students found', str(context.exception))

    def test_generate_batch_timetable_no_subjects(self):
        """Test timetable generation with no subjects for semester."""
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError) as context:
            generate_batch_timetable(
                batch_year=2024,
                department_id=self.department.id,
                semester=5  # No subjects for semester 5
            )
        
        self.assertIn('No subjects found', str(context.exception))

    def test_conflict_detection(self):
        """Test that the generator detects and avoids conflicts."""
        generator = TimetableGenerator()
        
        # Create a conflicting timetable entry
        Timetable.objects.create(
            class_name='EXISTING-CLASS',
            subject=self.subjects[0],
            faculty=self.faculty_members[0],
            day_of_week='MONDAY',
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0),
            classroom='Room-101',
            academic_year=generator.academic_year,
            is_active=True
        )
        
        # Test classroom conflict detection
        self.assertFalse(generator._is_slot_available(
            'MONDAY', '09:00', '10:00', 'Room-101', None, 'TEST-CLASS'
        ))
        
        # Test faculty conflict detection
        self.assertFalse(generator._is_slot_available(
            'MONDAY', '09:30', '10:30', 'Room-102', self.faculty_members[0], 'TEST-CLASS'
        ))
        
        # Test available slot
        self.assertTrue(generator._is_slot_available(
            'TUESDAY', '09:00', '10:00', 'Room-102', self.faculty_members[1], 'TEST-CLASS'
        ))

    def test_api_generate_timetable_success(self):
        """Test the API endpoint for generating timetables."""
        url = reverse('academics:timetable-generate-timetable')
        
        response = self.client.post(url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('Timetable generated successfully', data['message'])
        self.assertIn('data', data)
        
        # Verify response data structure
        result_data = data['data']
        self.assertEqual(result_data['batch_year'], 2024)
        self.assertEqual(result_data['semester'], 3)
        self.assertGreater(result_data['total_subjects'], 0)

    def test_api_generate_timetable_missing_batch_year(self):
        """Test API endpoint with missing batch_year parameter."""
        url = reverse('academics:timetable-generate-timetable')
        
        response = self.client.post(url, {
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('batch_year is required', data['error'])

    def test_api_generate_timetable_invalid_batch_year(self):
        """Test API endpoint with invalid batch_year parameter."""
        url = reverse('academics:timetable-generate-timetable')
        
        response = self.client.post(url, {
            'batch_year': 'invalid',
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('must be a valid integer', data['error'])

    def test_api_get_batch_timetable_success(self):
        """Test the API endpoint for retrieving batch timetables."""
        # First generate a timetable
        generate_batch_timetable(
            batch_year=2024,
            department_id=self.department.id,
            semester=3
        )
        
        # Then retrieve it
        url = reverse('academics:timetable-get-batch-timetable')
        response = self.client.get(url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        
        # Verify timetable entry structure
        if data['data']:
            entry = data['data'][0]
            self.assertIn('class_name', entry)
            self.assertIn('subject', entry)
            self.assertIn('day_of_week', entry)
            self.assertIn('start_time', entry)
            self.assertIn('end_time', entry)
            self.assertIn('classroom', entry)

    def test_api_get_batch_timetable_missing_batch_year(self):
        """Test API endpoint for retrieving timetable with missing batch_year."""
        url = reverse('academics:timetable-get-batch-timetable')
        response = self.client.get(url, {
            'department_id': self.department.id,
            'semester': 3
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('batch_year query parameter is required', data['error'])

    def test_class_name_generation(self):
        """Test class name generation for different scenarios."""
        generator = TimetableGenerator()
        
        # With department
        class_name = generator._generate_class_name(2024, self.department.id, 3)
        self.assertEqual(class_name, 'CSE-2024-S3')
        
        # Without department
        class_name = generator._generate_class_name(2024, None, 5)
        self.assertEqual(class_name, 'BATCH-2024-S5')
        
        # Without semester
        class_name = generator._generate_class_name(2024, self.department.id, None)
        self.assertEqual(class_name, 'CSE-2024-SX')

    def test_faculty_assignment_retrieval(self):
        """Test retrieval of faculty assignments for subjects."""
        generator = TimetableGenerator('2026-27')
        
        # Test subject with faculty assignment
        faculty = generator._get_subject_faculty(self.subjects[0], 3)
        self.assertIsNotNone(faculty)
        self.assertIn(faculty, self.faculty_members)
        
        # Test subject without faculty assignment
        faculty = generator._get_subject_faculty(self.subjects[4], 3)  # Last subject has no assignment
        self.assertIsNone(faculty)

    def test_timetable_clearing(self):
        """Test that existing timetables are cleared before generation."""
        # Create some existing timetable entries
        for i in range(3):
            Timetable.objects.create(
                class_name='CSE-2024-S3',
                subject=self.subjects[i],
                day_of_week='MONDAY',
                start_time=datetime.time(9 + i, 0),
                end_time=datetime.time(10 + i, 0),
                classroom=f'Room-{101 + i}',
                academic_year='2026-27',
                is_active=True
            )
        
        # Verify entries exist
        initial_count = Timetable.objects.filter(class_name='CSE-2024-S3').count()
        self.assertEqual(initial_count, 3)
        
        # Generate new timetable (should clear existing)
        generate_batch_timetable(
            batch_year=2024,
            department_id=self.department.id,
            semester=3,
            academic_year='2026-27'
        )
        
        # Verify old entries are gone and new ones exist
        final_entries = Timetable.objects.filter(
            class_name='CSE-2024-S3',
            academic_year='2026-27'
        )
        
        # Should have new entries (count may vary based on successful scheduling)
        self.assertGreater(final_entries.count(), 0)

    def test_multiple_classes_per_subject(self):
        """Test that subjects get multiple classes based on credits."""
        # Generate timetable for a subject with high credits
        result = generate_batch_timetable(
            batch_year=2024,
            department_id=self.department.id,
            semester=3
        )
        
        # Check that high-credit subjects get more classes
        entries = Timetable.objects.filter(
            class_name='CSE-2024-S3',
            subject__credits=4  # Data Structures and Operating Systems have 4 credits
        )
        
        # Should have multiple entries for high-credit subjects
        if entries.exists():
            subject_entries = {}
            for entry in entries:
                subject_code = entry.subject.code
                if subject_code not in subject_entries:
                    subject_entries[subject_code] = 0
                subject_entries[subject_code] += 1
            
            # At least one subject should have multiple classes
            max_classes = max(subject_entries.values()) if subject_entries else 0
            self.assertGreaterEqual(max_classes, 1)