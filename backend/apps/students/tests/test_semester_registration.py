"""
Tests for Semester Registration, Fee Transactions, and Registered Courses.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date

from apps.users.models import StudentProfile
from apps.academics.models import Department, Course, Subject, Program
from apps.students.models import SemesterRegistration, FeeTransaction, RegisteredCourse

User = get_user_model()


class SemesterRegistrationTestCase(TestCase):
    """Test cases for semester registration system."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create department
        self.dept = Department.objects.create(
            name='Computer Science',
            code='CSE'
        )
        
        # Create program
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.dept,
            duration_years=4,
            duration_semesters=8
        )
        
        # Create course
        self.course = Course.objects.create(
            name='B.Tech Computer Science',
            code='BTECH-CSE',
            department=self.dept,
            credits=160,
            duration_years=4
        )
        
        # Create subjects
        self.subject1 = Subject.objects.create(
            name='Data Structures',
            code='CS201',
            course=self.course,
            semester=3,
            credits=4
        )
        
        self.subject2 = Subject.objects.create(
            name='Algorithms',
            code='CS202',
            course=self.course,
            semester=3,
            credits=4
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT',
            first_name='Test',
            last_name='Student'
        )
        
        # Get or update the auto-created student profile
        self.student_profile = StudentProfile.objects.get(user=self.student_user)
        self.student_profile.enrollment_number = '2025001'
        self.student_profile.department = self.dept
        self.student_profile.program = self.program
        self.student_profile.dob = date(2005, 1, 1)
        self.student_profile.gender = 'M'
        self.student_profile.phone = '1234567890'
        self.student_profile.address = 'Test Address'
        self.student_profile.batch_year = 2025
        self.student_profile.save()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            role='ADMIN',
            is_staff=True
        )
    
    def test_create_semester_registration_as_student(self):
        """Test that a student can create their own semester registration."""
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'academic_year': '2025-26',
            'semester': 'Jan-Jun 2026',
            'institute_fee_paid': True,
            'hostel_fee_paid': True,
            'hostel_room_no': 'BH-101',
            'total_credits': 8,
            'fee_transactions': [
                {
                    'utr_no': 'UTR123456',
                    'bank_name': 'Test Bank',
                    'transaction_date': '2025-12-01',
                    'amount': '50000.00',
                    'account_debited': 'Student Account',
                    'account_credited': 'Institute Account'
                }
            ],
            'registered_courses': [
                {
                    'subject_id': self.subject1.id,
                    'is_backlog': False
                },
                {
                    'subject_id': self.subject2.id,
                    'is_backlog': False
                }
            ]
        }
        
        response = self.client.post('/api/students/semester-register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['academic_year'], '2025-26')
        self.assertEqual(response.data['semester'], 'Jan-Jun 2026')
        self.assertEqual(len(response.data['fee_transactions']), 1)
        self.assertEqual(len(response.data['registered_courses']), 2)
        
        # Verify database records
        self.assertEqual(SemesterRegistration.objects.count(), 1)
        self.assertEqual(FeeTransaction.objects.count(), 1)
        self.assertEqual(RegisteredCourse.objects.count(), 2)
    
    def test_max_three_fee_transactions(self):
        """Test that a semester registration cannot have more than 3 fee transactions."""
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'academic_year': '2025-26',
            'semester': 'Jan-Jun 2026',
            'institute_fee_paid': True,
            'hostel_fee_paid': False,
            'total_credits': 8,
            'fee_transactions': [
                {
                    'utr_no': f'UTR{i}',
                    'bank_name': 'Test Bank',
                    'transaction_date': '2025-12-01',
                    'amount': '10000.00',
                    'account_debited': 'Student Account',
                    'account_credited': 'Institute Account'
                }
                for i in range(4)  # Try to create 4 transactions
            ],
            'registered_courses': []
        }
        
        response = self.client.post('/api/students/semester-register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if the error is in the response data structure
        if 'detail' in response.data and 'fee_transactions' in response.data['detail']:
            self.assertIn('fee_transactions', response.data['detail'])
        else:
            self.assertIn('fee_transactions', response.data)
    
    def test_student_can_only_view_own_registrations(self):
        """Test that students can only see their own registrations."""
        # Create another student
        other_user = User.objects.create_user(
            username='other_student',
            email='other@test.com',
            password='testpass123',
            role='STUDENT'
        )
        other_profile = StudentProfile.objects.get(user=other_user)
        other_profile.enrollment_number = '2025002'
        other_profile.department = self.dept
        other_profile.program = self.program
        other_profile.dob = date(2005, 2, 1)
        other_profile.gender = 'F'
        other_profile.phone = '9876543210'
        other_profile.address = 'Other Address'
        other_profile.batch_year = 2025
        other_profile.save()
        
        # Create registrations for both students
        reg1 = SemesterRegistration.objects.create(
            student=self.student_profile,
            academic_year='2025-26',
            semester='Jan-Jun 2026',
            total_credits=8
        )
        
        reg2 = SemesterRegistration.objects.create(
            student=other_profile,
            academic_year='2025-26',
            semester='Jan-Jun 2026',
            total_credits=8
        )
        
        # Authenticate as first student
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/students/semester-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], reg1.id)
    
    def test_admin_can_view_all_registrations(self):
        """Test that admin can view all registrations."""
        # Create registrations
        reg1 = SemesterRegistration.objects.create(
            student=self.student_profile,
            academic_year='2025-26',
            semester='Jan-Jun 2026',
            total_credits=8
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/students/semester-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        self.assertEqual(len(results), 1)
    
    def test_non_student_cannot_create_registration(self):
        """Test that non-students cannot create semester registrations."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'academic_year': '2025-26',
            'semester': 'Jan-Jun 2026',
            'institute_fee_paid': True,
            'hostel_fee_paid': False,
            'total_credits': 8,
            'fee_transactions': [],
            'registered_courses': []
        }
        
        response = self.client.post('/api/students/semester-register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unique_semester_registration(self):
        """Test that a student cannot register for the same semester twice."""
        # Create first registration
        SemesterRegistration.objects.create(
            student=self.student_profile,
            academic_year='2025-26',
            semester='Jan-Jun 2026',
            total_credits=8
        )
        
        # Try to create duplicate
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'academic_year': '2025-26',
            'semester': 'Jan-Jun 2026',
            'institute_fee_paid': True,
            'hostel_fee_paid': False,
            'total_credits': 8,
            'fee_transactions': [],
            'registered_courses': []
        }
        
        response = self.client.post('/api/students/semester-register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
