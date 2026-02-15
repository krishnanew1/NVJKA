"""
Test suite for JWT authentication endpoints.

This module tests JWT token obtain and refresh functionality.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class JWTEndpointsTestCase(TestCase):
    """Test case for JWT authentication endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.login_url = reverse('users:token_obtain_pair')
        self.refresh_url = reverse('users:token_refresh')
        
        # Create a test user
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='STUDENT'
        )
    
    def test_jwt_login_url_exists(self):
        """Test that JWT login URL is accessible."""
        response = self.client.post(self.login_url)
        # Should return 400 (bad request) for missing credentials, not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_jwt_refresh_url_exists(self):
        """Test that JWT refresh URL is accessible."""
        response = self.client.post(self.refresh_url)
        # Should return 400 (bad request) for missing token, not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_jwt_token_obtain_with_valid_credentials(self):
        """Test JWT token obtain with valid credentials."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_jwt_token_obtain_with_invalid_credentials(self):
        """Test JWT token obtain with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_jwt_token_refresh_with_valid_token(self):
        """Test JWT token refresh with valid refresh token."""
        # First, get tokens
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Then, refresh the token
        refresh_data = {
            'refresh': refresh_token
        }
        response = self.client.post(self.refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_jwt_token_refresh_with_invalid_token(self):
        """Test JWT token refresh with invalid refresh token."""
        data = {
            'refresh': 'invalid_token'
        }
        response = self.client.post(self.refresh_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_url_patterns_are_correct(self):
        """Test that URL patterns resolve correctly."""
        self.assertEqual(self.login_url, '/api/auth/login/')
        self.assertEqual(self.refresh_url, '/api/auth/token/refresh/')