"""
Test script for Faculty My Subjects endpoint.

This script tests the /api/academics/faculty/my-subjects/ endpoint
to ensure faculty members can retrieve their assigned subjects.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import FacultyProfile
from apps.academics.models import Subject, Course, Department
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_jwt_token(user):
    """Generate JWT token for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


def test_my_subjects_endpoint():
    """Test the my-subjects endpoint for faculty members."""
    
    print("\n" + "="*80)
    print("TESTING FACULTY MY SUBJECTS ENDPOINT")
    print("="*80)
    
    # Create API client
    client = APIClient()
    
    # Test 1: Get Anuraj Singh's subjects
    print("\n📝 Test 1: Fetching subjects for Anuraj Singh (anuraj_s)")
    print("-" * 80)
    
    try:
        # Get Anuraj Singh's user account
        user = User.objects.get(username='anuraj_s')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        print(f"  Designation: {faculty_profile.designation}")
        
        # Get JWT token
        token = get_jwt_token(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Make API request
        response = client.get('/api/academics/faculty/my-subjects/')
        
        print(f"\n📡 API Response:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            subjects = response.data
            print(f"  ✓ SUCCESS: Retrieved {len(subjects)} subject(s)")
            
            if subjects:
                print(f"\n📚 Assigned Subjects:")
                for i, subject in enumerate(subjects, 1):
                    print(f"\n  {i}. {subject['name']} ({subject['code']})")
                    print(f"     Course: {subject['course']['name']}")
                    print(f"     Semester: {subject['semester_display']}")
                    print(f"     Credits: {subject['credits']}")
                    print(f"     Mandatory: {'Yes' if subject['is_mandatory'] else 'No'}")
                    if subject.get('faculty_info'):
                        print(f"     Faculty: {subject['faculty_info']['name']} ({subject['faculty_info']['employee_id']})")
            else:
                print(f"\n  ℹ️  No subjects assigned yet")
        else:
            print(f"  ✗ FAILED: {response.data}")
            
    except User.DoesNotExist:
        print("  ✗ User 'anuraj_s' not found. Please run seed_real_data.py first.")
    except FacultyProfile.DoesNotExist:
        print("  ✗ Faculty profile not found for user 'anuraj_s'")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 2: Get Ajay Kumar's subjects
    print("\n\n📝 Test 2: Fetching subjects for Ajay Kumar (ajay_k)")
    print("-" * 80)
    
    try:
        # Get Ajay Kumar's user account
        user = User.objects.get(username='ajay_k')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        
        # Get JWT token
        token = get_jwt_token(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Make API request
        response = client.get('/api/academics/faculty/my-subjects/')
        
        print(f"\n📡 API Response:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            subjects = response.data
            print(f"  ✓ SUCCESS: Retrieved {len(subjects)} subject(s)")
            
            if subjects:
                print(f"\n📚 Assigned Subjects:")
                for i, subject in enumerate(subjects, 1):
                    print(f"\n  {i}. {subject['name']} ({subject['code']})")
                    print(f"     Course: {subject['course']['name']}")
                    print(f"     Semester: {subject['semester_display']}")
            else:
                print(f"\n  ℹ️  No subjects assigned yet")
        else:
            print(f"  ✗ FAILED: {response.data}")
            
    except User.DoesNotExist:
        print("  ✗ User 'ajay_k' not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 3: Test with non-faculty user (should return empty)
    print("\n\n📝 Test 3: Testing with non-faculty user (admin_demo)")
    print("-" * 80)
    
    try:
        # Get admin user
        user = User.objects.get(username='admin_demo')
        
        print(f"✓ Found user: {user.username}")
        print(f"  Role: {user.role}")
        
        # Get JWT token
        token = get_jwt_token(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Make API request
        response = client.get('/api/academics/faculty/my-subjects/')
        
        print(f"\n📡 API Response:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            subjects = response.data
            print(f"  ✓ SUCCESS: Retrieved {len(subjects)} subject(s)")
            print(f"  ℹ️  Expected: 0 subjects (user is not faculty)")
        else:
            print(f"  Response: {response.data}")
            
    except User.DoesNotExist:
        print("  ✗ User 'admin_demo' not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 4: Test without authentication (should fail)
    print("\n\n📝 Test 4: Testing without authentication")
    print("-" * 80)
    
    try:
        # Clear credentials
        client.credentials()
        
        # Make API request
        response = client.get('/api/academics/faculty/my-subjects/')
        
        print(f"📡 API Response:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print(f"  ✓ SUCCESS: Authentication required (as expected)")
        else:
            print(f"  ✗ UNEXPECTED: Should require authentication")
            print(f"  Response: {response.data}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\n✓ All tests completed!")
    print("\nEndpoint: GET /api/academics/faculty/my-subjects/")
    print("Purpose: Returns subjects assigned to the logged-in faculty member")
    print("Authentication: Required (JWT token)")
    print("Returns: List of Subject objects with nested course information")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    test_my_subjects_endpoint()
