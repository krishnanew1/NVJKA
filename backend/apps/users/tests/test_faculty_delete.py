"""
Tests for faculty deletion functionality.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import CustomUser, FacultyProfile
from apps.academics.models import Department


class FacultyDeleteTestCase(TestCase):
    """Test cases for deleting faculty members."""

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
        
        # Create faculty user
        self.faculty_user = CustomUser.objects.create_user(
            username='prof_smith',
            email='smith@test.com',
            password='faculty123',
            first_name='John',
            last_name='Smith',
            role='FACULTY'
        )
        
        # Create faculty profile
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='FAC001',
            department=self.department,
            designation='Professor'
        )
        
        self.delete_url = f'/api/users/faculty/{self.faculty_profile.id}/'
    
    def test_delete_faculty_success(self):
        """Test successful deletion of faculty member."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Delete faculty
        response = self.client.delete(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('deleted successfully', response.data['message'])
        
        # Verify faculty profile is deleted
        self.assertFalse(FacultyProfile.objects.filter(id=self.faculty_profile.id).exists())
        
        # Verify user account is deleted
        self.assertFalse(CustomUser.objects.filter(id=self.faculty_user.id).exists())
    
    def test_delete_faculty_not_found(self):
        """Test deletion of non-existent faculty."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to delete non-existent faculty
        response = self.client.delete('/api/users/faculty/99999/')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_delete_faculty_unauthenticated(self):
        """Test deletion without authentication."""
        # Don't authenticate
        response = self.client.delete(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_faculty_detail(self):
        """Test retrieving faculty details."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Get faculty details
        response = self.client.get(self.delete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'FAC001')
        self.assertEqual(response.data['user']['username'], 'prof_smith')
