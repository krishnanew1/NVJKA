"""
Tests for user registration endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import CustomUser, StudentProfile, FacultyProfile
from apps.academics.models import Department, Program


class UserRegistrationTestCase(TestCase):
    """Test cases for user registration endpoint."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.register_url = reverse('users:register')
        
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
    
    def test_register_student_success(self):
        """Test successful student registration."""
        data = {
            'user': {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'SecurePass123',
                'role': 'STUDENT'
            },
            'profile': {
                'reg_no': '2026CS001',
                'dob': '2005-05-15',
                'gender': 'M',
                'phone': '+91-9876543210',
                'address': '123 Main St',
                'program_id': self.program.id,
                'department_id': self.department.id,
                'current_semester': 1,
                'batch_year': 2026,
                'custom_data': {
                    'aadhar_number': '1234-5678-9012',
                    'blood_group': 'O+'
                }
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # Debug: print response if failed
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('profile', response.data)
        
        # Verify user was created
        user = CustomUser.objects.get(username='john_doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.role, 'STUDENT')
        
        # Verify student profile was created
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.reg_no, '2026CS001')
        self.assertEqual(profile.custom_data['aadhar_number'], '1234-5678-9012')
        self.assertEqual(profile.program.id, self.program.id)
    
    def test_register_faculty_success(self):
        """Test successful faculty registration."""
        data = {
            'user': {
                'username': 'prof_smith',
                'email': 'smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'password': 'SecurePass123',
                'role': 'FACULTY'
            },
            'profile': {
                'employee_id': 'EMP001',
                'department_id': self.department.id,
                'designation': 'Professor',
                'specialization': 'AI/ML',
                'date_of_joining': '2020-01-01'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Verify user was created
        user = CustomUser.objects.get(username='prof_smith')
        self.assertEqual(user.role, 'FACULTY')
        
        # Verify faculty profile was created
        profile = FacultyProfile.objects.get(user=user)
        self.assertEqual(profile.employee_id, 'EMP001')
        self.assertEqual(profile.designation, 'Professor')
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create existing user
        CustomUser.objects.create_user(
            username='john_doe',
            email='existing@example.com',
            password='password123',
            role='STUDENT'
        )
        
        data = {
            'user': {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'SecurePass123',
                'role': 'STUDENT'
            },
            'profile': {
                'reg_no': '2026CS001',
                'program_id': self.program.id
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_missing_required_fields(self):
        """Test registration with missing required fields."""
        data = {
            'user': {
                'username': 'john_doe',
                # Missing email and password
                'role': 'STUDENT'
            },
            'profile': {}
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_student_without_reg_no(self):
        """Test student registration without reg_no."""
        data = {
            'user': {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'SecurePass123',
                'role': 'STUDENT'
            },
            'profile': {
                # Missing reg_no
                'program_id': self.program.id
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_with_custom_data(self):
        """Test student registration with custom data."""
        data = {
            'user': {
                'username': 'jane_doe',
                'email': 'jane@example.com',
                'password': 'SecurePass123',
                'role': 'STUDENT'
            },
            'profile': {
                'reg_no': '2026CS002',
                'program_id': self.program.id,
                'current_semester': 1,
                'batch_year': 2026,
                'custom_data': {
                    'aadhar_number': '9876-5432-1098',
                    'samagra_id': 'SAM123456',
                    'blood_group': 'A+',
                    'parent_phone': '+91-9876543210'
                }
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify custom data was saved
        user = CustomUser.objects.get(username='jane_doe')
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.custom_data['aadhar_number'], '9876-5432-1098')
        self.assertEqual(profile.custom_data['samagra_id'], 'SAM123456')
        self.assertEqual(profile.custom_data['blood_group'], 'A+')
        self.assertEqual(len(profile.custom_data), 4)
