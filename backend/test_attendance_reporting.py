"""
Test script for Faculty Attendance Reporting feature.

Tests the new AttendanceReportSubmission model and API endpoints:
- GET /api/attendance/faculty/summary/
- POST /api/attendance/faculty/submit-report/
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import FacultyProfile, StudentProfile
from apps.academics.models import Subject
from apps.attendance.models import Attendance, AttendanceReportSubmission
from datetime import date, timedelta
import random

User = get_user_model()


def create_test_attendance_data():
    """Create sample attendance data for testing."""
    print("\n" + "="*80)
    print("CREATING TEST ATTENDANCE DATA")
    print("="*80)
    
    try:
        # Get Anuraj Singh's faculty profile and subjects
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        subjects = Subject.objects.filter(faculty=faculty)
        
        if not subjects.exists():
            print("❌ No subjects assigned to Anuraj Singh")
            return False
        
        subject = subjects.first()
        print(f"\n✓ Using subject: {subject.name} ({subject.code})")
        
        # Get students enrolled in this subject's course
        from apps.students.models import Enrollment
        enrollments = Enrollment.objects.filter(
            course=subject.course,
            semester=subject.semester,
            status='Active'
        )[:5]  # Limit to 5 students for testing
        
        if not enrollments.exists():
            print("❌ No students enrolled in this subject")
            return False
        
        print(f"✓ Found {enrollments.count()} students")
        
        # Create attendance records for the past 10 days
        today = date.today()
        created_count = 0
        
        for i in range(10):
            attendance_date = today - timedelta(days=i)
            
            for enrollment in enrollments:
                student = enrollment.student
                
                # Random attendance status (80% present, 10% absent, 10% late)
                rand = random.random()
                if rand < 0.8:
                    status = 'Present'
                elif rand < 0.9:
                    status = 'Absent'
                else:
                    status = 'Late'
                
                # Create or update attendance record
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'recorded_by': user
                    }
                )
                
                if created:
                    created_count += 1
        
        print(f"\n✓ Created {created_count} attendance records")
        print(f"✓ Subject: {subject.name}")
        print(f"✓ Students: {enrollments.count()}")
        print(f"✓ Days: 10")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_attendance_summary():
    """Test the attendance summary endpoint."""
    print("\n" + "="*80)
    print("TEST 1: ATTENDANCE SUMMARY ENDPOINT")
    print("="*80)
    
    try:
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Get Anuraj Singh's user
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        # Create API client
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Make request
        print("\n📡 GET /api/attendance/faculty/summary/")
        response = client.get('/api/attendance/faculty/summary/')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"\n✓ SUCCESS")
            print(f"\nFaculty: {data['faculty']['name']} ({data['faculty']['employee_id']})")
            print(f"Subjects: {len(data['subjects'])}")
            
            for subject_data in data['subjects']:
                subject = subject_data['subject']
                batches = subject_data['batches']
                
                print(f"\n📚 Subject: {subject['name']} ({subject['code']})")
                print(f"   Batches: {len(batches)}")
                
                for batch_string, batch_info in batches.items():
                    print(f"\n   📅 Batch: {batch_string}")
                    print(f"      Students: {len(batch_info['students'])}")
                    print(f"      Average Attendance: {batch_info['batch_average']}%")
                    
                    # Show first 3 students
                    for i, student in enumerate(batch_info['students'][:3]):
                        print(f"      {i+1}. {student['name']} ({student['reg_no']})")
                        print(f"         Attended: {student['attended']}/{student['total_classes']} ({student['attendance_percentage']}%)")
        else:
            print(f"❌ FAILED: {response.data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_submit_report():
    """Test the submit attendance report endpoint."""
    print("\n" + "="*80)
    print("TEST 2: SUBMIT ATTENDANCE REPORT ENDPOINT")
    print("="*80)
    
    try:
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Get Anuraj Singh's user
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        
        # Get first subject
        subject = Subject.objects.filter(faculty=faculty).first()
        
        if not subject:
            print("❌ No subjects assigned to faculty")
            return
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        # Create API client
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Make request
        print("\n📡 POST /api/attendance/faculty/submit-report/")
        payload = {
            'subject_id': subject.id,
            'batch_string': '2024-IMG'
        }
        print(f"Payload: {payload}")
        
        response = client.post('/api/attendance/faculty/submit-report/', payload, format='json')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.data
            print(f"\n✓ SUCCESS")
            print(f"\nMessage: {data['message']}")
            print(f"Submission ID: {data['submission']['id']}")
            print(f"Subject: {data['submission']['subject']['name']}")
            print(f"Batch: {data['submission']['batch_string']}")
            print(f"Submitted At: {data['submission']['submitted_at']}")
            print(f"Is Reviewed: {data['submission']['is_reviewed']}")
            
            # Verify in database
            submission = AttendanceReportSubmission.objects.get(id=data['submission']['id'])
            print(f"\n✓ Verified in database:")
            print(f"   Faculty: {submission.faculty.user.get_full_name()}")
            print(f"   Subject: {submission.subject.name}")
            print(f"   Batch: {submission.batch_string}")
            print(f"   Reviewed: {submission.is_reviewed_by_admin}")
            
        else:
            print(f"❌ FAILED: {response.data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_model():
    """Test the AttendanceReportSubmission model."""
    print("\n" + "="*80)
    print("TEST 3: ATTENDANCEREPORTSUBMISSION MODEL")
    print("="*80)
    
    try:
        # Get faculty and subject
        user = User.objects.get(username='anuraj_s')
        faculty = FacultyProfile.objects.get(user=user)
        subject = Subject.objects.filter(faculty=faculty).first()
        
        if not subject:
            print("❌ No subjects assigned to faculty")
            return
        
        # Create submission
        submission = AttendanceReportSubmission.objects.create(
            faculty=faculty,
            subject=subject,
            batch_string='2023-CSE'
        )
        
        print(f"\n✓ Created submission:")
        print(f"   ID: {submission.id}")
        print(f"   Faculty: {submission.faculty.user.get_full_name()}")
        print(f"   Subject: {submission.subject.name}")
        print(f"   Batch: {submission.batch_string}")
        print(f"   Submitted At: {submission.submitted_at}")
        print(f"   Is Reviewed: {submission.is_reviewed_by_admin}")
        print(f"   String representation: {str(submission)}")
        
        # Test querying
        submissions = AttendanceReportSubmission.objects.filter(faculty=faculty)
        print(f"\n✓ Total submissions by this faculty: {submissions.count()}")
        
        # Test ordering
        latest = AttendanceReportSubmission.objects.first()
        print(f"✓ Latest submission: {latest}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("\n" + "="*80)
    print("FACULTY ATTENDANCE REPORTING - TEST SUITE")
    print("="*80)
    
    # Create test data
    if create_test_attendance_data():
        # Run tests
        test_model()
        test_attendance_summary()
        test_submit_report()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")
