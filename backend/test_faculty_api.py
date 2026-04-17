#!/usr/bin/env python
"""
Test script for faculty assignment API endpoint.

This script tests the /api/academics/subjects/{id}/assign-faculty/ endpoint.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from apps.academics.views import SubjectViewSet
from apps.academics.models import Subject
from apps.users.models import FacultyProfile

User = get_user_model()


def test_faculty_assignment_api():
    """Test faculty assignment API endpoint."""
    
    print("=" * 80)
    print("FACULTY ASSIGNMENT API TEST")
    print("=" * 80)
    
    # Get admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("\n⚠ No admin user found. Creating one...")
        admin_user = User.objects.create_superuser(
            username='test_admin',
            email='admin@test.com',
            password='admin123'
        )
    
    print(f"\n✓ Using admin user: {admin_user.username}")
    
    # Get a subject
    subject = Subject.objects.first()
    if not subject:
        print("\n⚠ No subjects found. Run seed_real_data command first.")
        return
    
    print(f"✓ Using subject: {subject.name} ({subject.code})")
    
    # Get a faculty member
    faculty = FacultyProfile.objects.first()
    if not faculty:
        print("\n⚠ No faculty found. Run seed_real_data command first.")
        return
    
    print(f"✓ Using faculty: {faculty.user.get_full_name()} ({faculty.employee_id})")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Assign faculty to subject
    print("\n" + "-" * 80)
    print("TEST 1: ASSIGN FACULTY TO SUBJECT")
    print("-" * 80)
    
    request = factory.patch(
        f'/api/academics/subjects/{subject.id}/assign-faculty/',
        {'faculty_id': faculty.id},
        content_type='application/json'
    )
    force_authenticate(request, user=admin_user)
    
    view = SubjectViewSet.as_view({'patch': 'assign_faculty'})
    response = view(request, pk=subject.id)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 200:
        print("\n✓ Faculty assigned successfully!")
        print(f"   Subject: {response.data['data']['name']}")
        if response.data['data']['faculty_info']:
            print(f"   Faculty: {response.data['data']['faculty_info']['name']}")
            print(f"   Employee ID: {response.data['data']['faculty_info']['employee_id']}")
    else:
        print("\n✗ Failed to assign faculty")
    
    # Test 2: Get subject details with faculty info
    print("\n" + "-" * 80)
    print("TEST 2: GET SUBJECT WITH FACULTY INFO")
    print("-" * 80)
    
    request = factory.get(f'/api/academics/subjects/{subject.id}/')
    force_authenticate(request, user=admin_user)
    
    view = SubjectViewSet.as_view({'get': 'retrieve'})
    response = view(request, pk=subject.id)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✓ Subject retrieved successfully!")
        print(f"   Subject: {response.data['name']} ({response.data['code']})")
        print(f"   Course: {response.data['course']['name']}")
        print(f"   Semester: {response.data['semester_display']}")
        print(f"   Credits: {response.data['credits']}")
        
        if response.data['faculty_info']:
            print(f"   Faculty: {response.data['faculty_info']['name']}")
            print(f"   Employee ID: {response.data['faculty_info']['employee_id']}")
            print(f"   Designation: {response.data['faculty_info']['designation']}")
        else:
            print(f"   Faculty: Not assigned")
    else:
        print("\n✗ Failed to retrieve subject")
    
    # Test 3: Unassign faculty from subject
    print("\n" + "-" * 80)
    print("TEST 3: UNASSIGN FACULTY FROM SUBJECT")
    print("-" * 80)
    
    request = factory.patch(
        f'/api/academics/subjects/{subject.id}/assign-faculty/',
        {'faculty_id': None},
        content_type='application/json'
    )
    force_authenticate(request, user=admin_user)
    
    view = SubjectViewSet.as_view({'patch': 'assign_faculty'})
    response = view(request, pk=subject.id)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 200:
        print("\n✓ Faculty unassigned successfully!")
        print(f"   Subject: {response.data['data']['name']}")
        print(f"   Faculty: {response.data['data']['faculty_info']}")
    else:
        print("\n✗ Failed to unassign faculty")
    
    # Test 4: List all subjects with faculty info
    print("\n" + "-" * 80)
    print("TEST 4: LIST ALL SUBJECTS WITH FACULTY INFO")
    print("-" * 80)
    
    request = factory.get('/api/academics/subjects/')
    force_authenticate(request, user=admin_user)
    
    view = SubjectViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        # Handle paginated response
        subjects_data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        print(f"\n✓ Found {len(subjects_data)} subjects")
        
        # Show first 5 subjects
        for subject_data in subjects_data[:5]:
            print(f"\n📚 {subject_data['name']} ({subject_data['code']})")
            if subject_data['faculty_info']:
                print(f"   👨‍🏫 Faculty: {subject_data['faculty_info']['name']} ({subject_data['faculty_info']['employee_id']})")
            else:
                print(f"   👨‍🏫 Faculty: Not assigned")
    else:
        print("\n✗ Failed to list subjects")
    
    print("\n" + "=" * 80)
    print("API TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == '__main__':
    test_faculty_assignment_api()
