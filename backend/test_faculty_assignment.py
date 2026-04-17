#!/usr/bin/env python
"""
Test script for faculty assignment to subjects.

This script tests:
1. Listing subjects with faculty information
2. Assigning faculty to subjects
3. Unassigning faculty from subjects
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.academics.models import Subject
from apps.users.models import FacultyProfile
from apps.academics.serializers import SubjectSerializer


def test_faculty_assignment():
    """Test faculty assignment functionality."""
    
    print("=" * 80)
    print("FACULTY ASSIGNMENT TEST")
    print("=" * 80)
    
    # Get all subjects
    subjects = Subject.objects.all()
    print(f"\n✓ Found {subjects.count()} subjects in database")
    
    # Get all faculty
    faculty = FacultyProfile.objects.all()
    print(f"✓ Found {faculty.count()} faculty members in database")
    
    if not subjects.exists() or not faculty.exists():
        print("\n⚠ No subjects or faculty found. Run seed_real_data command first.")
        return
    
    print("\n" + "-" * 80)
    print("SUBJECTS WITH FACULTY INFORMATION")
    print("-" * 80)
    
    # Serialize and display subjects
    serializer = SubjectSerializer(subjects, many=True)
    for subject_data in serializer.data:
        print(f"\n📚 {subject_data['name']} ({subject_data['code']})")
        print(f"   Course: {subject_data['course']['name']}")
        print(f"   Semester: {subject_data['semester_display']}")
        print(f"   Credits: {subject_data['credits']}")
        
        if subject_data['faculty_info']:
            faculty_info = subject_data['faculty_info']
            print(f"   👨‍🏫 Faculty: {faculty_info['name']} ({faculty_info['employee_id']})")
            print(f"      Designation: {faculty_info['designation']}")
        else:
            print(f"   👨‍🏫 Faculty: Not assigned")
    
    # Test assigning faculty to a subject
    print("\n" + "-" * 80)
    print("TESTING FACULTY ASSIGNMENT")
    print("-" * 80)
    
    # Get a subject without faculty
    unassigned_subject = subjects.filter(faculty__isnull=True).first()
    
    if unassigned_subject:
        print(f"\n📚 Subject: {unassigned_subject.name} ({unassigned_subject.code})")
        print(f"   Current Faculty: None")
        
        # Get a faculty member
        faculty_member = faculty.first()
        print(f"\n👨‍🏫 Assigning Faculty: {faculty_member.user.get_full_name()} ({faculty_member.employee_id})")
        
        # Assign faculty
        unassigned_subject.faculty = faculty_member
        unassigned_subject.save()
        
        # Verify assignment
        unassigned_subject.refresh_from_db()
        serializer = SubjectSerializer(unassigned_subject)
        
        print(f"\n✓ Faculty assigned successfully!")
        print(f"   Faculty: {serializer.data['faculty_info']['name']}")
        print(f"   Employee ID: {serializer.data['faculty_info']['employee_id']}")
        print(f"   Designation: {serializer.data['faculty_info']['designation']}")
    else:
        print("\n⚠ All subjects already have faculty assigned")
    
    # Test unassigning faculty
    print("\n" + "-" * 80)
    print("TESTING FACULTY UNASSIGNMENT")
    print("-" * 80)
    
    assigned_subject = subjects.filter(faculty__isnull=False).first()
    
    if assigned_subject:
        print(f"\n📚 Subject: {assigned_subject.name} ({assigned_subject.code})")
        print(f"   Current Faculty: {assigned_subject.faculty.user.get_full_name()}")
        
        # Unassign faculty
        assigned_subject.faculty = None
        assigned_subject.save()
        
        # Verify unassignment
        assigned_subject.refresh_from_db()
        serializer = SubjectSerializer(assigned_subject)
        
        print(f"\n✓ Faculty unassigned successfully!")
        print(f"   Faculty: {serializer.data['faculty_info']}")
    else:
        print("\n⚠ No subjects with faculty assigned")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == '__main__':
    test_faculty_assignment()
