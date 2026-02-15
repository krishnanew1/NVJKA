"""
Test cases for user profiles, signals, and dashboard access.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser, StudentProfile, FacultyProfile
from academics.models import Department


class ProfileSignalTestCase(TestCase):
    """
    Test automatic profile creation via signals.
    """
    
    def test_student_profile_auto_created_on_user_creation(self):
        """
        Test that a StudentProfile is automatically created when a user
        with role='STUDENT' is created.
        """
        # Create a student user
        student_user = CustomUser.objects.create_user(
            username='test_student',
            password='testpass123',
            email='student@test.com',
            role='STUDENT'
        )
        
        # Assert that the user was created
        self.assertIsNotNone(student_user)
        self.assertEqual(student_user.role, 'STUDENT')
        
        # Assert that a StudentProfile was automatically created
        self.assertTrue(hasattr(student_user, 'student_profile'))
        self.assertIsNotNone(student_user.student_profile)
        
        # Verify the profile is linked to the correct user
        self.assertEqual(student_user.student_profile.user, student_user)
        
        # Verify default values were set
        self.assertEqual(student_user.student_profile.enrollment_number, f'TEMP_{student_user.id}')
        self.assertEqual(student_user.student_profile.batch_year, 2026)
    
    def test_faculty_profile_not_auto_created(self):
        """
        Test that FacultyProfile is NOT automatically created when a user
        with role='FACULTY' is created (because department is required).
        """
        # Create a faculty user
        faculty_user = CustomUser.objects.create_user(
            username='test_faculty',
            password='testpass123',
            email='faculty@test.com',
            role='FACULTY'
        )
        
        # Assert that the user was created
        self.assertIsNotNone(faculty_user)
        self.assertEqual(faculty_user.role, 'FACULTY')
        
        # Assert that FacultyProfile was NOT automatically created
        self.assertFalse(hasattr(faculty_user, 'faculty_profile'))
    
    def test_admin_profile_not_created(self):
        """
        Test that no profile is created for ADMIN users.
        """
        # Create an admin user
        admin_user = CustomUser.objects.create_user(
            username='test_admin',
            password='testpass123',
            email='admin@test.com',
            role='ADMIN'
        )
        
        # Assert that the user was created
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user.role, 'ADMIN')
        
        # Assert that no profiles were created
        self.assertFalse(hasattr(admin_user, 'student_profile'))
        self.assertFalse(hasattr(admin_user, 'faculty_profile'))


class StudentDashboardAccessTestCase(TestCase):
    """
    Test student dashboard access with role-based permissions.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a department for testing
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='CS Department'
        )
        
        # Create a student user (profile auto-created via signal)
        self.student_user = CustomUser.objects.create_user(
            username='student_test',
            password='testpass123',
            email='student@test.com',
            first_name='John',
            last_name='Doe',
            role='STUDENT'
        )
        
        # Update the student profile with proper data
        self.student_user.student_profile.enrollment_number = '2026CS001'
        self.student_user.student_profile.department = self.department
        self.student_user.student_profile.current_semester = 3
        self.student_user.student_profile.save()
        
        # Create a faculty user
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_test',
            password='testpass123',
            email='faculty@test.com',
            first_name='Jane',
            last_name='Smith',
            role='FACULTY'
        )
        
        # Manually create faculty profile (not auto-created)
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='FAC2026001',
            department=self.department,
            designation='Professor'
        )
        
        # URLs
        self.student_dashboard_url = reverse('users:student_dashboard')
        self.faculty_dashboard_url = reverse('users:faculty_dashboard')
    
    def test_student_can_access_student_dashboard(self):
        """
        Test that a student user can successfully access the student dashboard.
        """
        # Authenticate as student
        self.client.force_authenticate(user=self.student_user)
        
        # Access student dashboard
        response = self.client.get(self.student_dashboard_url)
        
        # Assert successful access
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response data
        self.assertEqual(response.data['enrollment_number'], '2026CS001')
        self.assertEqual(response.data['user']['username'], 'student_test')
        self.assertEqual(response.data['user']['email'], 'student@test.com')
        self.assertEqual(response.data['user']['full_name'], 'John Doe')
        self.assertEqual(response.data['user']['role'], 'STUDENT')
        self.assertEqual(response.data['department']['code'], 'CS')
        self.assertEqual(response.data['current_semester'], 3)
        self.assertEqual(response.data['batch_year'], 2026)
    
    def test_student_cannot_access_faculty_dashboard(self):
        """
        Test that a student user gets 403 Forbidden when trying to access
        the faculty dashboard.
        """
        # Authenticate as student
        self.client.force_authenticate(user=self.student_user)
        
        # Try to access faculty dashboard
        response = self.client.get(self.faculty_dashboard_url)
        
        # Assert forbidden access
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
    
    def test_unauthenticated_user_cannot_access_student_dashboard(self):
        """
        Test that unauthenticated users cannot access the student dashboard.
        """
        # Don't authenticate
        response = self.client.get(self.student_dashboard_url)
        
        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_student_can_update_profile(self):
        """
        Test that a student can update their own profile via PATCH.
        """
        # Authenticate as student
        self.client.force_authenticate(user=self.student_user)
        
        # Update profile data
        update_data = {
            'current_semester': 4,
            'enrollment_number': '2026CS002'
        }
        
        response = self.client.patch(
            self.student_dashboard_url,
            data=update_data,
            format='json'
        )
        
        # Assert successful update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_semester'], 4)
        self.assertEqual(response.data['enrollment_number'], '2026CS002')
        
        # Verify database was updated
        self.student_user.student_profile.refresh_from_db()
        self.assertEqual(self.student_user.student_profile.current_semester, 4)
        self.assertEqual(self.student_user.student_profile.enrollment_number, '2026CS002')


class FacultyDashboardAccessTestCase(TestCase):
    """
    Test faculty dashboard access with role-based permissions.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='CS Department'
        )
        
        # Create a faculty user
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_test',
            password='testpass123',
            email='faculty@test.com',
            first_name='Jane',
            last_name='Smith',
            role='FACULTY'
        )
        
        # Manually create faculty profile
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='FAC2026001',
            department=self.department,
            designation='Professor',
            specialization='Machine Learning'
        )
        
        # Create a student user
        self.student_user = CustomUser.objects.create_user(
            username='student_test',
            password='testpass123',
            email='student@test.com',
            role='STUDENT'
        )
        
        # URLs
        self.student_dashboard_url = reverse('users:student_dashboard')
        self.faculty_dashboard_url = reverse('users:faculty_dashboard')
    
    def test_faculty_can_access_faculty_dashboard(self):
        """
        Test that a faculty user can successfully access the faculty dashboard.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Access faculty dashboard
        response = self.client.get(self.faculty_dashboard_url)
        
        # Assert successful access
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response data
        self.assertEqual(response.data['employee_id'], 'FAC2026001')
        self.assertEqual(response.data['user']['username'], 'faculty_test')
        self.assertEqual(response.data['user']['email'], 'faculty@test.com')
        self.assertEqual(response.data['user']['full_name'], 'Jane Smith')
        self.assertEqual(response.data['user']['role'], 'FACULTY')
        self.assertEqual(response.data['department']['code'], 'CS')
        self.assertEqual(response.data['designation'], 'Professor')
        self.assertEqual(response.data['specialization'], 'Machine Learning')
    
    def test_faculty_cannot_access_student_dashboard(self):
        """
        Test that a faculty user gets 403 Forbidden when trying to access
        the student dashboard.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Try to access student dashboard
        response = self.client.get(self.student_dashboard_url)
        
        # Assert forbidden access
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
    
    def test_faculty_can_update_profile(self):
        """
        Test that a faculty member can update their own profile via PATCH.
        """
        # Authenticate as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Update profile data
        update_data = {
            'designation': 'Associate Professor',
            'specialization': 'Deep Learning'
        }
        
        response = self.client.patch(
            self.faculty_dashboard_url,
            data=update_data,
            format='json'
        )
        
        # Assert successful update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['designation'], 'Associate Professor')
        self.assertEqual(response.data['specialization'], 'Deep Learning')
        
        # Verify database was updated
        self.faculty_profile.refresh_from_db()
        self.assertEqual(self.faculty_profile.designation, 'Associate Professor')
        self.assertEqual(self.faculty_profile.specialization, 'Deep Learning')


class ProfileValidationTestCase(TestCase):
    """
    Test profile validation rules.
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
        
        # Create two student users
        self.student1 = CustomUser.objects.create_user(
            username='student1',
            password='testpass123',
            role='STUDENT'
        )
        self.student1.student_profile.enrollment_number = '2026CS001'
        self.student1.student_profile.save()
        
        self.student2 = CustomUser.objects.create_user(
            username='student2',
            password='testpass123',
            role='STUDENT'
        )
        
        self.student_dashboard_url = reverse('users:student_dashboard')
    
    def test_duplicate_enrollment_number_rejected(self):
        """
        Test that duplicate enrollment numbers are rejected.
        """
        # Authenticate as student2
        self.client.force_authenticate(user=self.student2)
        
        # Try to use student1's enrollment number
        update_data = {
            'enrollment_number': '2026CS001'  # Already used by student1
        }
        
        response = self.client.patch(
            self.student_dashboard_url,
            data=update_data,
            format='json'
        )
        
        # Assert validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('enrollment_number', response.data)
    
    def test_invalid_semester_rejected(self):
        """
        Test that invalid semester values are rejected.
        """
        # Authenticate as student2
        self.client.force_authenticate(user=self.student2)
        
        # Try to set invalid semester
        update_data = {
            'current_semester': 0  # Invalid: must be >= 1
        }
        
        response = self.client.patch(
            self.student_dashboard_url,
            data=update_data,
            format='json'
        )
        
        # Assert validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_semester', response.data)
