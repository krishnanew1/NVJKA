"""
Simple test for Faculty Attendance Reporting feature.

Tests the AttendanceReportSubmission model directly.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import FacultyProfile
from apps.academics.models import Subject
from apps.attendance.models import AttendanceReportSubmission

User = get_user_model()


def test_model_creation():
    """Test creating AttendanceReportSubmission records."""
    print("\n" + "="*80)
    print("TEST: ATTENDANCEREPORTSUBMISSION MODEL")
    print("="*80)
    
    try:
        # Get Anuraj Singh's faculty profile
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        
        print(f"\n✓ Faculty: {faculty.user.get_full_name()}")
        print(f"  Employee ID: {faculty.employee_id}")
        
        # Get subjects assigned to this faculty
        subjects = Subject.objects.filter(faculty=faculty)
        print(f"\n✓ Assigned Subjects: {subjects.count()}")
        
        if not subjects.exists():
            print("❌ No subjects assigned to this faculty")
            return False
        
        for subject in subjects:
            print(f"  - {subject.name} ({subject.code})")
        
        # Create submission for first subject
        subject = subjects.first()
        
        print(f"\n📝 Creating submission for: {subject.name}")
        
        submission = AttendanceReportSubmission.objects.create(
            faculty=faculty,
            subject=subject,
            batch_string='2024-IMG'
        )
        
        print(f"\n✓ Submission Created:")
        print(f"  ID: {submission.id}")
        print(f"  Faculty: {submission.faculty.user.get_full_name()}")
        print(f"  Subject: {submission.subject.name} ({submission.subject.code})")
        print(f"  Batch: {submission.batch_string}")
        print(f"  Submitted At: {submission.submitted_at}")
        print(f"  Is Reviewed: {submission.is_reviewed_by_admin}")
        print(f"  String: {str(submission)}")
        
        # Create another submission
        submission2 = AttendanceReportSubmission.objects.create(
            faculty=faculty,
            subject=subject,
            batch_string='2023-CSE'
        )
        
        print(f"\n✓ Second Submission Created:")
        print(f"  ID: {submission2.id}")
        print(f"  Batch: {submission2.batch_string}")
        
        # Query submissions
        all_submissions = AttendanceReportSubmission.objects.filter(faculty=faculty)
        print(f"\n✓ Total Submissions by {faculty.user.get_full_name()}: {all_submissions.count()}")
        
        for sub in all_submissions:
            print(f"  - {sub.subject.code} | {sub.batch_string} | {sub.submitted_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Test filtering
        unreviewed = AttendanceReportSubmission.objects.filter(
            faculty=faculty,
            is_reviewed_by_admin=False
        )
        print(f"\n✓ Unreviewed Submissions: {unreviewed.count()}")
        
        # Test ordering (should be by -submitted_at)
        latest = AttendanceReportSubmission.objects.first()
        print(f"\n✓ Latest Submission (any faculty): {latest}")
        
        return True
        
    except User.DoesNotExist:
        print("❌ User 'anuraj_s' not found")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model_fields():
    """Test all model fields."""
    print("\n" + "="*80)
    print("TEST: MODEL FIELDS")
    print("="*80)
    
    try:
        # Get a submission
        submission = AttendanceReportSubmission.objects.first()
        
        if not submission:
            print("❌ No submissions found")
            return False
        
        print(f"\n✓ Testing submission ID: {submission.id}")
        print(f"\nRequired Fields:")
        print(f"  faculty: {submission.faculty} ✓")
        print(f"  subject: {submission.subject} ✓")
        print(f"  batch_string: {submission.batch_string} ✓")
        print(f"  submitted_at: {submission.submitted_at} ✓")
        print(f"  is_reviewed_by_admin: {submission.is_reviewed_by_admin} ✓")
        
        print(f"\nOptional Fields:")
        print(f"  reviewed_at: {submission.reviewed_at}")
        print(f"  reviewed_by: {submission.reviewed_by}")
        print(f"  notes: {submission.notes or '(empty)'}")
        
        # Test updating
        print(f"\n📝 Testing update...")
        submission.notes = "Test note from admin"
        submission.save()
        print(f"✓ Notes updated: {submission.notes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_relationships():
    """Test model relationships."""
    print("\n" + "="*80)
    print("TEST: MODEL RELATIONSHIPS")
    print("="*80)
    
    try:
        # Get faculty
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        
        # Test reverse relationship from faculty
        submissions = faculty.attendance_report_submissions.all()
        print(f"\n✓ Faculty → Submissions: {submissions.count()}")
        
        # Test reverse relationship from subject
        subject = Subject.objects.filter(faculty=faculty).first()
        if subject:
            subject_submissions = subject.attendance_report_submissions.all()
            print(f"✓ Subject → Submissions: {subject_submissions.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n" + "="*80)
    print("ATTENDANCE REPORT SUBMISSION - MODEL TESTS")
    print("="*80)
    
    # Run tests
    test_model_creation()
    test_model_fields()
    test_relationships()
    
    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80 + "\n")
