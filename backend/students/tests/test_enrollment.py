"""
Test cases for student enrollment API endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import CustomUser, StudentProfile
from academics.models import Department, Course
from students.models import Enrollment


class EnrollStudentViewTestCase(TestCase):
    """
    Test cases for the EnrollStudentView API endpoint.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='CS Department'
        )
        
        # Create courses
        self.course1 = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            department=self.department,
            credits=4,
            duration_years=1
        )
        
        self.course2 = Course.objects.create(
            name='Data Structures',
            code='CS201',
            department=self.department,
            credits=4,
            duration_years=1
        )
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            password='testpass123',
            email='admin@test.com',
            role='ADMIN'
        )
        
        # Create student user (profile auto-created via signal)
        self.student_user = CustomUser.objects.create_user(
            username='student_test',
            password='testpass123',
            email='student@test.com',
            role='STUDENT'
        )
        
        # Update student profile
        self.student_profile = self.student_user.student_profile
        self.student_profile.enrollment_number = '2026CS001'
        self.student_profile.department = self.department
        self.student_profile.save()
        
        # Create faculty user (for permission testing)
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_test',
            password='testpass123',
            email='faculty@test.com',
            role='FACULTY'
        )
        
        # URL
        self.enroll_url = reverse('students:enroll_student')
    
    def test_admin_can_enroll_student(self):
        """
        Test that an admin user can successfully enroll a student in a course.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Enroll student in course
        data = {
            'student_id': self.student_profile.id,
            'course_id': self.course1.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert successful enrollment
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Student enrolled successfully')
        
        # Verify enrollment data
        enrollment_data = response.data['enrollment']
        self.assertEqual(enrollment_data['student']['id'], self.student_profile.id)
        self.assertEqual(enrollment_data['student']['enrollment_number'], '2026CS001')
        self.assertEqual(enrollment_data['course']['id'], self.course1.id)
        self.assertEqual(enrollment_data['course']['code'], 'CS101')
        self.assertEqual(enrollment_data['status'], 'ENROLLED')
        
        # Verify enrollment was created in database
        enrollment = Enrollment.objects.get(
            student=self.student_profile,
            course=self.course1
        )
        self.assertIsNotNone(enrollment)
        self.assertEqual(enrollment.status, 'ENROLLED')
    
    def test_cannot_enroll_student_twice_in_same_course(self):
        """
        Test that enrolling a student in the same course twice returns an error.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # First enrollment
        data = {
            'student_id': self.student_profile.id,
            'course_id': self.course1.id
        }
        response1 = self.client.post(self.enroll_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to enroll again
        response2 = self.client.post(self.enroll_url, data, format='json')
        
        # Assert error response
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)
        self.assertEqual(response2.data['error'], 'Already enrolled')
        self.assertIn('enrollment', response2.data)
    
    def test_non_admin_cannot_enroll_student(self):
        """
        Test that non-admin users (student, faculty) cannot enroll students.
        """
        # Test with student user
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'student_id': self.student_profile.id,
            'course_id': self.course1.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test with faculty user
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_user_cannot_enroll_student(self):
        """
        Test that unauthenticated users cannot enroll students.
        """
        data = {
            'student_id': self.student_profile.id,
            'course_id': self.course1.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_missing_student_id_returns_error(self):
        """
        Test that missing student_id returns a validation error.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Missing student_id
        data = {
            'course_id': self.course1.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('student_id', response.data['detail'])
    
    def test_missing_course_id_returns_error(self):
        """
        Test that missing course_id returns a validation error.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Missing course_id
        data = {
            'student_id': self.student_profile.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('course_id', response.data['detail'])
    
    def test_invalid_student_id_returns_error(self):
        """
        Test that an invalid student_id returns a 404 error.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Invalid student_id
        data = {
            'student_id': 99999,  # Non-existent
            'course_id': self.course1.id
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert not found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Student not found')
    
    def test_invalid_course_id_returns_error(self):
        """
        Test that an invalid course_id returns a 404 error.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Invalid course_id
        data = {
            'student_id': self.student_profile.id,
            'course_id': 99999  # Non-existent
        }
        
        response = self.client.post(self.enroll_url, data, format='json')
        
        # Assert not found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Course not found')
    
    def test_admin_can_enroll_student_in_multiple_courses(self):
        """
        Test that an admin can enroll the same student in multiple different courses.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Enroll in first course
        data1 = {
            'student_id': self.student_profile.id,
            'course_id': self.course1.id
        }
        response1 = self.client.post(self.enroll_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Enroll in second course
        data2 = {
            'student_id': self.student_profile.id,
            'course_id': self.course2.id
        }
        response2 = self.client.post(self.enroll_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Verify both enrollments exist
        enrollments = Enrollment.objects.filter(student=self.student_profile)
        self.assertEqual(enrollments.count(), 2)
