"""
Tests for student list endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import CustomUser, StudentProfile
from apps.academics.models import Department, Program


class StudentListTestCase(TestCase):
    """Test cases for student list endpoint."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('users:student_list')
        
        # Create admin user for authentication
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='ADMIN'
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Computer Science Department'
        )
        
        # Create test program
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.department,
            duration_years=4,
            total_credits=160
        )
    
    def test_list_students_empty(self):
        """Test listing students when database is empty."""
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.list_url)
        
        # Should return 200 OK with empty results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)
        self.assertIsInstance(response.data['results'], list)
    
    def test_list_students_with_data(self):
        """Test listing students when students exist."""
        # Create test student
        student_user = CustomUser.objects.create_user(
            username='john_doe',
            email='john@example.com',
            password='password123',
            role='STUDENT'
        )
        
        # Update the auto-created profile
        profile = StudentProfile.objects.get(user=student_user)
        profile.reg_no = '2026CS001'
        profile.enrollment_number = '2026CS001'
        profile.program = self.program
        profile.department = self.department
        profile.current_semester = 1
        profile.batch_year = 2026
        profile.save()
        
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.list_url)
        
        # Should return 200 OK with student data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reg_no'], '2026CS001')
        self.assertEqual(response.data['results'][0]['user']['username'], 'john_doe')
    
    def test_list_students_unauthenticated(self):
        """Test listing students without authentication."""
        response = self.client.get(self.list_url)
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_students_with_custom_data(self):
        """Test listing students with custom_data."""
        # Create test student with custom data
        student_user = CustomUser.objects.create_user(
            username='jane_doe',
            email='jane@example.com',
            password='password123',
            role='STUDENT'
        )
        
        # Update the auto-created profile
        profile = StudentProfile.objects.get(user=student_user)
        profile.reg_no = '2026CS002'
        profile.enrollment_number = '2026CS002'
        profile.program = self.program
        profile.department = self.department
        profile.current_semester = 1
        profile.batch_year = 2026
        profile.custom_data = {
            'aadhar_number': '1234-5678-9012',
            'blood_group': 'O+',
            'hostel': 'BH-1'
        }
        profile.save()
        
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.list_url)
        
        # Should return 200 OK with custom data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['custom_data']['aadhar_number'], '1234-5678-9012')
        self.assertEqual(response.data['results'][0]['custom_data']['blood_group'], 'O+')
        self.assertEqual(response.data['results'][0]['custom_data']['hostel'], 'BH-1')
    
    def test_list_students_ordering(self):
        """Test that students are ordered by created_at descending."""
        # Create multiple students
        for i in range(3):
            student_user = CustomUser.objects.create_user(
                username=f'student_{i}',
                email=f'student{i}@example.com',
                password='password123',
                role='STUDENT'
            )
            
            profile = StudentProfile.objects.get(user=student_user)
            profile.reg_no = f'2026CS00{i+1}'
            profile.enrollment_number = f'2026CS00{i+1}'
            profile.program = self.program
            profile.save()
        
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.list_url)
        
        # Should return 200 OK with 3 students
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
        # Most recent should be first (student_2)
        self.assertEqual(response.data['results'][0]['user']['username'], 'student_2')
        self.assertEqual(response.data['results'][2]['user']['username'], 'student_0')
