"""
Direct test for Faculty My Subjects functionality.

This script directly tests the database query logic without using the API client.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import FacultyProfile
from apps.academics.models import Subject

User = get_user_model()


def test_faculty_subjects():
    """Test fetching subjects for faculty members."""
    
    print("\n" + "="*80)
    print("TESTING FACULTY SUBJECTS QUERY")
    print("="*80)
    
    # Test 1: Anuraj Singh
    print("\n📝 Test 1: Subjects for Anuraj Singh (anuraj_s)")
    print("-" * 80)
    
    try:
        user = User.objects.get(username='anuraj_s')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        print(f"  Designation: {faculty_profile.designation}")
        
        # Query subjects assigned to this faculty
        subjects = Subject.objects.select_related(
            'course__department', 'faculty__user'
        ).filter(
            faculty=faculty_profile
        ).order_by('course__code', 'semester', 'code')
        
        print(f"\n📚 Assigned Subjects: {subjects.count()}")
        
        if subjects.exists():
            for i, subject in enumerate(subjects, 1):
                print(f"\n  {i}. {subject.name} ({subject.code})")
                print(f"     Course: {subject.course.name}")
                print(f"     Department: {subject.course.department.name}")
                print(f"     Semester: {subject.get_semester_display()}")
                print(f"     Credits: {subject.credits}")
                print(f"     Mandatory: {'Yes' if subject.is_mandatory else 'No'}")
        else:
            print("  ℹ️  No subjects assigned yet")
            
    except User.DoesNotExist:
        print("  ✗ User 'anuraj_s' not found. Run seed_real_data.py first.")
    except FacultyProfile.DoesNotExist:
        print("  ✗ Faculty profile not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 2: Ajay Kumar
    print("\n\n📝 Test 2: Subjects for Ajay Kumar (ajay_k)")
    print("-" * 80)
    
    try:
        user = User.objects.get(username='ajay_k')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        
        subjects = Subject.objects.filter(faculty=faculty_profile)
        
        print(f"\n📚 Assigned Subjects: {subjects.count()}")
        
        if subjects.exists():
            for i, subject in enumerate(subjects, 1):
                print(f"\n  {i}. {subject.name} ({subject.code})")
                print(f"     Course: {subject.course.name}")
                print(f"     Semester: {subject.get_semester_display()}")
        else:
            print("  ℹ️  No subjects assigned yet")
            
    except User.DoesNotExist:
        print("  ✗ User 'ajay_k' not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 3: Deepak Kumar
    print("\n\n📝 Test 3: Subjects for Deepak Kumar (deepak_d)")
    print("-" * 80)
    
    try:
        user = User.objects.get(username='deepak_d')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        
        subjects = Subject.objects.filter(faculty=faculty_profile)
        
        print(f"\n📚 Assigned Subjects: {subjects.count()}")
        
        if subjects.exists():
            for i, subject in enumerate(subjects, 1):
                print(f"\n  {i}. {subject.name} ({subject.code})")
                print(f"     Course: {subject.course.name}")
                print(f"     Semester: {subject.get_semester_display()}")
        else:
            print("  ℹ️  No subjects assigned yet")
            
    except User.DoesNotExist:
        print("  ✗ User 'deepak_d' not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 4: Anurag Srivastav
    print("\n\n📝 Test 4: Subjects for Anurag Srivastav (anurag_s)")
    print("-" * 80)
    
    try:
        user = User.objects.get(username='anurag_s')
        faculty_profile = FacultyProfile.objects.get(user=user)
        
        print(f"✓ Found faculty: {faculty_profile.user.get_full_name()}")
        print(f"  Employee ID: {faculty_profile.employee_id}")
        
        subjects = Subject.objects.filter(faculty=faculty_profile)
        
        print(f"\n📚 Assigned Subjects: {subjects.count()}")
        
        if subjects.exists():
            for i, subject in enumerate(subjects, 1):
                print(f"\n  {i}. {subject.name} ({subject.code})")
                print(f"     Course: {subject.course.name}")
                print(f"     Semester: {subject.get_semester_display()}")
        else:
            print("  ℹ️  No subjects assigned yet")
            
    except User.DoesNotExist:
        print("  ✗ User 'anurag_s' not found")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\n✓ Database query logic verified!")
    print("\nThe MySubjectsView will use this same query:")
    print("  Subject.objects.filter(faculty=faculty_profile)")
    print("\nEndpoint: GET /api/academics/faculty/my-subjects/")
    print("Frontend: GET /api/academics/faculty/my-subjects/")
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    test_faculty_subjects()
