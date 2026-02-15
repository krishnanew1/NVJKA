"""
Test cases for bulk attendance marking API endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta

from users.models import CustomUser, StudentProfile, FacultyProfile
from academics.models import Department, Course, Subject
from attendance.models import Attendance


class BulkAttendanceViewTestCase(TestCase):
    """
    Test cases for the BulkAttendanceView API endpoint.
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
        
        # Create course
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            department=self.department,
            credits=4,
            duration_years=1
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Programming Fundamentals',
            code='CS101',
            course=self.course,
            semester=1,
            credits=4
        )
        
        # Create faculty user
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_test',
            password='testpass123',
            email='faculty@test.com',
            first_name='Jane',
            last_name='Smith',
            role='FACULTY'
        )
        
        # Create faculty profile
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='FAC2026001',
            department=self.department,
            designation='Professor'
        )
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            password='testpass123',
            email='admin@test.com',
            role='ADMIN'
        )
        
        # Create student users (profiles auto-created via signal)
        self.students = []
        for i in range(1, 6):
            student_user = CustomUser.objects.create_user(
                username=f'student{i}',
                password='testpass123',
                email=f'student{i}@test.com',
                first_name=f'Student{i}',
                last_name='Test',
                role='STUDENT'
            )
            student_profile = student_user.student_profile
            student_profile.enrollment_number = f'2026CS00{i}'
            student_profile.department = self.department
            student_profile.save()
            self.students.append(student_profile)
        
        # Create a regular student user (for permission testing)
        self.student_user = CustomUser.objects.create_user(
            username='student_regular',
            password='testpass123',
            email='student@test.com',
            role='STUDENT'
        )
        
        # URL
        self.bulk_attendance_url = reverse('attendance:bulk_mark_attendance')
    
    def test_faculty_can_mark_bulk_attendance(self):
        """
        Test that a faculty member can successfully mark attendance for multiple students.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Mark attendance for all students
        data = {
            'student_ids': [s.id for s in self.students],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(response.data['status'], 'PRESENT')
        
        # Verify attendance records were created
        attendance_count = Attendance.objects.filter(
            subject=self.subject,
            date=date.today()
        ).count()
        self.assertEqual(attendance_count, 5)
        
        # Verify all students have attendance
        for student in self.students:
            attendance = Attendance.objects.get(
                student=student,
                subject=self.subject,
                date=date.today()
            )
            self.assertEqual(attendance.status, 'PRESENT')
            self.assertEqual(attendance.marked_by, self.faculty_profile)
    
    def test_admin_can_mark_bulk_attendance(self):
        """
        Test that an admin user can mark bulk attendance.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'student_ids': [s.id for s in self.students[:3]],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'ABSENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['status'], 'ABSENT')
    
    def test_student_cannot_mark_attendance(self):
        """
        Test that student users cannot mark attendance.
        """
        # Authenticate as student
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_user_cannot_mark_attendance(self):
        """
        Test that unauthenticated users cannot mark attendance.
        """
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_missing_student_ids_returns_error(self):
        """
        Test that missing student_ids returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_ids', response.data['detail'])
    
    def test_empty_student_ids_returns_error(self):
        """
        Test that empty student_ids list returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non-empty', response.data['detail'])
    
    def test_missing_subject_id_returns_error(self):
        """
        Test that missing subject_id returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('subject_id', response.data['detail'])
    
    def test_missing_date_returns_error(self):
        """
        Test that missing date returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': self.subject.id,
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data['detail'])
    
    def test_invalid_date_format_returns_error(self):
        """
        Test that invalid date format returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': self.subject.id,
            'date': '11-02-2026',  # Wrong format
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('YYYY-MM-DD', response.data['detail'])
    
    def test_invalid_status_returns_error(self):
        """
        Test that invalid status returns a validation error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'INVALID'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid status', response.data['error'])
    
    def test_invalid_subject_id_returns_error(self):
        """
        Test that invalid subject_id returns a 404 error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id],
            'subject_id': 99999,  # Non-existent
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert not found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Subject not found', response.data['error'])
    
    def test_invalid_student_ids_returns_error(self):
        """
        Test that invalid student_ids return a 404 error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [99999, 99998],  # Non-existent
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert not found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Students not found', response.data['error'])
    
    def test_duplicate_attendance_returns_error(self):
        """
        Test that marking attendance twice for the same day returns an error.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [s.id for s in self.students],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        # First request (should succeed)
        response1 = self.client.post(self.bulk_attendance_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second request (should fail)
        response2 = self.client.post(self.bulk_attendance_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already marked', response2.data['error'])
    
    def test_mark_attendance_with_late_status(self):
        """
        Test marking attendance with LATE status.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        data = {
            'student_ids': [self.students[0].id, self.students[1].id],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'LATE'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'LATE')
        
        # Verify status in database
        for student in self.students[:2]:
            attendance = Attendance.objects.get(
                student=student,
                subject=self.subject,
                date=date.today()
            )
            self.assertEqual(attendance.status, 'LATE')
    
    def test_transaction_rollback_on_error(self):
        """
        Test that if an error occurs, no attendance records are created (transaction rollback).
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Mix valid and invalid student IDs
        data = {
            'student_ids': [self.students[0].id, 99999],
            'subject_id': self.subject.id,
            'date': date.today().isoformat(),
            'status': 'PRESENT'
        }
        
        response = self.client.post(self.bulk_attendance_url, data, format='json')
        
        # Assert error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify no attendance records were created
        attendance_count = Attendance.objects.filter(
            subject=self.subject,
            date=date.today()
        ).count()
        self.assertEqual(attendance_count, 0)
