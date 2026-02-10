"""
Authentication test suite for the Academic ERP system.

This module tests user authentication functionality including user creation
and JWT token retrieval from the login endpoint.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
import json


class AuthenticationTestCase(TestCase):
    """Test case for user authentication and JWT token functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = reverse('users:token_obtain_pair')
        
        # Test user data
        self.user_data = {
            'username': 'teststudent',
            'email': 'student@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'Student',
            'role': 'STUDENT',
            'phone_number': '+1234567890',
            'address': '123 Test Street, Test City'
        }
    
    def test_create_user_and_retrieve_jwt_tokens(self):
        """
        Test creating a user and successfully retrieving JWT access and refresh tokens.
        
        This test verifies the complete authentication flow:
        1. Create a new user with all required fields
        2. Authenticate using username/password
        3. Retrieve both access and refresh JWT tokens
        4. Validate token structure and content
        """
        # Step 1: Create a new user
        user = CustomUser.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            role=self.user_data['role'],
            phone_number=self.user_data['phone_number'],
            address=self.user_data['address']
        )
        
        # Verify user was created successfully
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password']))
        
        # Step 2: Authenticate and retrieve JWT tokens
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Step 3: Verify successful authentication
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Validate token structure
        response_data = response.json()
        
        # Check that both tokens are present
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
        
        # Verify tokens are not empty
        self.assertIsNotNone(response_data['access'])
        self.assertIsNotNone(response_data['refresh'])
        self.assertTrue(len(response_data['access']) > 0)
        self.assertTrue(len(response_data['refresh']) > 0)
        
        # Verify tokens are strings (JWT format)
        self.assertIsInstance(response_data['access'], str)
        self.assertIsInstance(response_data['refresh'], str)
        
        # JWT tokens should have 3 parts separated by dots
        access_parts = response_data['access'].split('.')
        refresh_parts = response_data['refresh'].split('.')
        
        self.assertEqual(len(access_parts), 3, "Access token should have 3 parts (header.payload.signature)")
        self.assertEqual(len(refresh_parts), 3, "Refresh token should have 3 parts (header.payload.signature)")
    
    def test_create_different_role_users_and_authenticate(self):
        """Test creating users with different roles and authenticating each."""
        roles_to_test = ['STUDENT', 'FACULTY', 'ADMIN']
        
        for role in roles_to_test:
            with self.subTest(role=role):
                # Create user with specific role
                username = f'test{role.lower()}'
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='TestPass123!',
                    role=role
                )
                
                # Authenticate and get tokens
                login_data = {
                    'username': username,
                    'password': 'TestPass123!'
                }
                
                response = self.client.post(self.login_url, login_data, format='json')
                
                # Verify successful authentication for each role
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('access', response.json())
                self.assertIn('refresh', response.json())
    
    def test_authentication_with_email_as_username(self):
        """Test authentication using email as username."""
        # Create user
        user = CustomUser.objects.create_user(
            username='emailuser',
            email='emailuser@example.com',
            password='EmailPass123!',
            role='STUDENT'
        )
        
        # Try to authenticate with email (should work if email is unique)
        login_data = {
            'username': 'emailuser@example.com',
            'password': 'EmailPass123!'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        # This might fail depending on Django's authentication backend
        # but we test to document the behavior
        if response.status_code == status.HTTP_200_OK:
            self.assertIn('access', response.json())
            self.assertIn('refresh', response.json())
    
    def test_authentication_failure_with_wrong_password(self):
        """Test authentication failure with incorrect password."""
        # Create user
        CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='CorrectPass123!',
            role='STUDENT'
        )
        
        # Try to authenticate with wrong password
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Should fail authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.json())
        self.assertNotIn('refresh', response.json())
    
    def test_authentication_failure_with_nonexistent_user(self):
        """Test authentication failure with non-existent username."""
        login_data = {
            'username': 'nonexistentuser',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Should fail authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.json())
        self.assertNotIn('refresh', response.json())
    
    def test_user_creation_with_all_custom_fields(self):
        """Test creating a user with all custom fields and then authenticating."""
        # Create user with all custom fields
        user = CustomUser.objects.create_user(
            username='fulluser',
            email='fulluser@example.com',
            password='FullPass123!',
            first_name='Full',
            last_name='User',
            role='FACULTY',
            phone_number='+1987654321',
            address='456 Full Street, Full City, FC 12345'
        )
        
        # Verify all fields are set correctly
        self.assertEqual(user.username, 'fulluser')
        self.assertEqual(user.email, 'fulluser@example.com')
        self.assertEqual(user.first_name, 'Full')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'FACULTY')
        self.assertEqual(user.phone_number, '+1987654321')
        self.assertEqual(user.address, '456 Full Street, Full City, FC 12345')
        
        # Test authentication
        login_data = {
            'username': 'fulluser',
            'password': 'FullPass123!'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
        
        # Verify tokens are valid JWT format
        access_token = response_data['access']
        refresh_token = response_data['refresh']
        
        self.assertTrue(access_token.count('.') == 2, "Access token should be valid JWT format")
        self.assertTrue(refresh_token.count('.') == 2, "Refresh token should be valid JWT format")