#!/usr/bin/env python
"""
Test script for faculty list endpoint.

This script tests the /api/users/faculty/ endpoint.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from apps.users.views import FacultyListView
from apps.users.models import CustomUser, FacultyProfile


def test_faculty_list_endpoint():
    """Test faculty list API endpoint."""
    
    print("=" * 80)
    print("FACULTY LIST ENDPOINT TEST")
    print("=" * 80)
    
    # Get or create admin user
    admin_user, created = CustomUser.objects.get_or_create(
        username='test_admin',
        defaults={
            'email': 'admin@test.com',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"\n✓ Created admin user: {admin_user.username}")
    else:
        print(f"\n✓ Using existing admin user: {admin_user.username}")
    
    # Get faculty count
    faculty_count = FacultyProfile.objects.count()
    print(f"✓ Found {faculty_count} faculty members in database")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: GET /api/users/faculty/
    print("\n" + "-" * 80)
    print("TEST 1: GET /api/users/faculty/")
    print("-" * 80)
    
    request = factory.get('/api/users/faculty/')
    force_authenticate(request, user=admin_user)
    
    view = FacultyListView.as_view()
    response = view(request)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✓ Endpoint accessible!")
        print(f"   Count: {response.data.get('count', 0)}")
        print(f"   Results: {len(response.data.get('results', []))} faculty members")
        
        # Show first 3 faculty members
        results = response.data.get('results', [])
        if results:
            print("\n   Sample Faculty:")
            for faculty in results[:3]:
                user = faculty.get('user', {})
                print(f"   - {user.get('full_name', 'N/A')} ({faculty.get('employee_id', 'N/A')})")
                print(f"     Email: {user.get('email', 'N/A')}")
                print(f"     Designation: {faculty.get('designation', 'N/A')}")
                print(f"     Department: {faculty.get('department', {}).get('name', 'N/A')}")
        else:
            print("\n   ⚠ No faculty members found")
    else:
        print(f"\n✗ Failed with status {response.status_code}")
        print(f"   Response: {response.data}")
    
    # Test 2: Verify response structure
    print("\n" + "-" * 80)
    print("TEST 2: VERIFY RESPONSE STRUCTURE")
    print("-" * 80)
    
    if response.status_code == 200 and response.data.get('results'):
        faculty = response.data['results'][0]
        
        required_fields = ['id', 'user', 'employee_id', 'department', 'designation']
        missing_fields = [field for field in required_fields if field not in faculty]
        
        if not missing_fields:
            print("\n✓ All required fields present")
            print(f"   Fields: {', '.join(required_fields)}")
            
            # Check user nested data
            user = faculty.get('user', {})
            user_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
            user_missing = [field for field in user_fields if field not in user]
            
            if not user_missing:
                print(f"✓ User nested data complete")
                print(f"   User fields: {', '.join(user_fields)}")
            else:
                print(f"✗ Missing user fields: {', '.join(user_missing)}")
        else:
            print(f"✗ Missing required fields: {', '.join(missing_fields)}")
    else:
        print("\n⚠ Skipping structure test (no data)")
    
    # Test 3: Test without authentication
    print("\n" + "-" * 80)
    print("TEST 3: TEST WITHOUT AUTHENTICATION")
    print("-" * 80)
    
    request = factory.get('/api/users/faculty/')
    # Don't authenticate
    
    view = FacultyListView.as_view()
    response = view(request)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 401 or response.status_code == 403:
        print("✓ Endpoint correctly requires authentication")
    else:
        print(f"⚠ Unexpected status code: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == '__main__':
    test_faculty_list_endpoint()
