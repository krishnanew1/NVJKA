"""
Tests for student CRUD (Create, Read, Update, Delete) functionality.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import CustomUser, StudentProfile
from apps.academics.models import Department, Program


class StudentCRUDTestCase(TestCase):
    """Test cases for student CRUD operations."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='ADMIN'
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Computer Science Department'
        )
        
        # Create program
        self.program = Program.objects.create(
            name='Bachelor of Computer Science',
            code='BCS',
            department=self.department,
            duration_years=4,
            duration_semesters=8
        )
        
        # Create student user
        self.student_user = CustomUser.objects.create_user(
            username='john_doe',
            email='john@test.com',
            password='student123',
            first_name='John',
            last_name='Doe',
            role='STUDENT'
        )
        
        # Get or update the auto-created student profile
        try:
            self.student_profile = StudentProfile.objects.get(user=self.student_user)
            self.student_profile.reg_no = '2026CS001'
            self.student_profile.enrollment_number = '2026CS001'
            self.student_profile.program = self.program
            self.student_profile.department = self.department
            self.student_profile.current_semester = 1
            self.student_profile.batch_year = 2026
            self.student_profile.save()
        except StudentProfile.DoesNotExist:
            # If signal didn't create it, create manually
            self.student_profile = StudentProfile.objects.create(
                user=self.student_user,
                reg_no='2026CS001',
                enrollment_number='2026CS001',
                program=self.program,
                department=self.department,
                current_semester=1,
                batch_year=2026
            )
        
        self.delete_url = f'/api/users/students/{self.student_profile.id}/'
    
    def test_delete_student_success(self):
        """Test successful deletion of student."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Delete student
        response = self.client.delete(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted successfully', response.data['message'])
        
        # Verify student profile is deleted
        self.assertFalse(StudentProfile.objects.filter(id=self.student_profile.id).exists())
        
        # Verify user account is deleted
        self.assertFalse(CustomUser.objects.filter(id=self.student_user.id).exists())
    
    def test_delete_student_not_found(self):
        """Test deletion of non-existent student."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to delete non-existent student
        response = self.client.delete('/api/users/students/99999/')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_delete_student_unauthenticated(self):
        """Test deletion without authentication."""
        # Don't authenticate
        response = self.client.delete(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_student_detail(self):
        """Test retrieving student details."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Get student details
        response = self.client.get(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reg_no'], '2026CS001')
        self.assertEqual(response.data['user']['username'], 'john_doe')
    
    def test_update_student_success(self):
        """Test successful update of student profile."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Update student data
        update_data = {
            'user': {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@test.com'
            },
            'current_semester': 2,
            'phone': '+91-9999999999'
        }
        
        response = self.client.patch(self.delete_url, update_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updates
        self.student_profile.refresh_from_db()
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'Jane')
        self.assertEqual(self.student_user.last_name, 'Smith')
        self.assertEqual(self.student_user.email, 'jane@test.com')
        self.assertEqual(self.student_profile.current_semester, 2)
        self.assertEqual(self.student_profile.phone, '+91-9999999999')
    
    def test_update_student_duplicate_email(self):
        """Test updating student with duplicate email."""
        # Create another user with an email
        other_user = CustomUser.objects.create_user(
            username='other_user',
            email='other@test.com',
            password='test123',
            role='STUDENT'
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to update with duplicate email
        update_data = {
            'user': {
                'email': 'other@test.com'
            }
        }
        
        response = self.client.patch(self.delete_url, update_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
