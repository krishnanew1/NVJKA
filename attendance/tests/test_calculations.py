"""
Test cases for attendance calculation functions.
"""
from django.test import TestCase
from datetime import date, timedelta

from users.models import CustomUser, StudentProfile
from academics.models import Department, Course, Subject
from attendance.models import Attendance
from attendance.utils import calculate_attendance_percentage, get_attendance_summary


class AttendanceCalculationTestCase(TestCase):
    """
    Test cases for attendance percentage calculations.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='CS Department'
        )
        
        # Create course
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            department=self.department,
            credits=4,
            duration_years=1
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Programming Fundamentals',
            code='CS101',
            course=self.course,
            semester=1,
            credits=4
        )
        
        # Create student user (profile auto-created via signal)
        self.student_user = CustomUser.objects.create_user(
            username='student_test',
            password='testpass123',
            email='student@test.com',
            first_name='John',
            last_name='Doe',
            role='STUDENT'
        )
        
        # Update student profile
        self.student_profile = self.student_user.student_profile
        self.student_profile.enrollment_number = '2026CS001'
        self.student_profile.department = self.department
        self.student_profile.save()
    
    def test_attendance_percentage_with_8_present_2_absent(self):
        """
        Test that attendance percentage is correctly calculated as 80%
        when there are 8 PRESENT and 2 ABSENT records.
        """
        # Create 10 attendance records: 8 Present, 2 Absent
        base_date = date.today()
        
        # Create 8 PRESENT records
        for i in range(8):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        
        # Create 2 ABSENT records
        for i in range(8, 10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        # Calculate attendance percentage
        percentage = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        
        # Assert percentage is 80%
        self.assertEqual(percentage, 80.0)
        
        # Verify total records
        total_records = Attendance.objects.filter(
            student=self.student_profile,
            subject=self.subject
        ).count()
        self.assertEqual(total_records, 10)
        
        # Verify present count
        present_count = Attendance.objects.filter(
            student=self.student_profile,
            subject=self.subject,
            status='PRESENT'
        ).count()
        self.assertEqual(present_count, 8)
        
        # Verify absent count
        absent_count = Attendance.objects.filter(
            student=self.student_profile,
            subject=self.subject,
            status='ABSENT'
        ).count()
        self.assertEqual(absent_count, 2)
    
    def test_attendance_percentage_with_all_present(self):
        """
        Test that attendance percentage is 100% when all records are PRESENT.
        """
        # Create 10 PRESENT records
        base_date = date.today()
        for i in range(10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        
        percentage = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(percentage, 100.0)
    
    def test_attendance_percentage_with_all_absent(self):
        """
        Test that attendance percentage is 0% when all records are ABSENT.
        """
        # Create 10 ABSENT records
        base_date = date.today()
        for i in range(10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        percentage = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(percentage, 0.0)
    
    def test_attendance_percentage_with_no_records(self):
        """
        Test that attendance percentage is 0% when there are no records.
        """
        percentage = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(percentage, 0.0)
    
    def test_attendance_percentage_includes_late_as_attended(self):
        """
        Test that LATE status is counted as attended in percentage calculation.
        """
        # Create 7 PRESENT, 2 LATE, 1 ABSENT
        base_date = date.today()
        
        for i in range(7):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        
        for i in range(7, 9):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='LATE'
            )
        
        Attendance.objects.create(
            student=self.student_profile,
            subject=self.subject,
            date=base_date - timedelta(days=9),
            status='ABSENT'
        )
        
        # 7 PRESENT + 2 LATE = 9 attended out of 10 = 90%
        percentage = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(percentage, 90.0)
    
    def test_attendance_summary_returns_correct_counts(self):
        """
        Test that get_attendance_summary returns correct counts and percentage.
        """
        # Create 8 PRESENT, 2 ABSENT
        base_date = date.today()
        
        for i in range(8):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        
        for i in range(8, 10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        summary = get_attendance_summary(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(summary['total'], 10)
        self.assertEqual(summary['present'], 8)
        self.assertEqual(summary['absent'], 2)
        self.assertEqual(summary['late'], 0)
        self.assertEqual(summary['attended'], 8)
        self.assertEqual(summary['percentage'], 80.0)
    
    def test_attendance_summary_with_mixed_statuses(self):
        """
        Test attendance summary with PRESENT, ABSENT, and LATE statuses.
        """
        # Create 5 PRESENT, 3 LATE, 2 ABSENT
        base_date = date.today()
        
        for i in range(5):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        
        for i in range(5, 8):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='LATE'
            )
        
        for i in range(8, 10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        summary = get_attendance_summary(
            self.student_profile,
            self.subject
        )
        
        self.assertEqual(summary['total'], 10)
        self.assertEqual(summary['present'], 5)
        self.assertEqual(summary['late'], 3)
        self.assertEqual(summary['absent'], 2)
        self.assertEqual(summary['attended'], 8)  # 5 + 3
        self.assertEqual(summary['percentage'], 80.0)
    
    def test_attendance_percentage_for_specific_subject(self):
        """
        Test that percentage calculation works for a specific subject.
        """
        # Create another subject
        subject2 = Subject.objects.create(
            name='Data Structures',
            code='CS201',
            course=self.course,
            semester=2,
            credits=4
        )
        
        # Create attendance for subject 1: 8 PRESENT, 2 ABSENT (80%)
        base_date = date.today()
        for i in range(8):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        for i in range(8, 10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        # Create attendance for subject 2: 6 PRESENT, 4 ABSENT (60%)
        for i in range(10, 16):
            Attendance.objects.create(
                student=self.student_profile,
                subject=subject2,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        for i in range(16, 20):
            Attendance.objects.create(
                student=self.student_profile,
                subject=subject2,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        # Check subject 1 percentage
        percentage1 = calculate_attendance_percentage(
            self.student_profile,
            self.subject
        )
        self.assertEqual(percentage1, 80.0)
        
        # Check subject 2 percentage
        percentage2 = calculate_attendance_percentage(
            self.student_profile,
            subject2
        )
        self.assertEqual(percentage2, 60.0)
    
    def test_overall_attendance_percentage_without_subject(self):
        """
        Test that percentage calculation works for overall attendance (no subject filter).
        """
        # Create another subject
        subject2 = Subject.objects.create(
            name='Data Structures',
            code='CS201',
            course=self.course,
            semester=2,
            credits=4
        )
        
        # Create attendance for subject 1: 8 PRESENT, 2 ABSENT
        base_date = date.today()
        for i in range(8):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        for i in range(8, 10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        # Create attendance for subject 2: 6 PRESENT, 4 ABSENT
        for i in range(10, 16):
            Attendance.objects.create(
                student=self.student_profile,
                subject=subject2,
                date=base_date - timedelta(days=i),
                status='PRESENT'
            )
        for i in range(16, 20):
            Attendance.objects.create(
                student=self.student_profile,
                subject=subject2,
                date=base_date - timedelta(days=i),
                status='ABSENT'
            )
        
        # Overall: 14 PRESENT out of 20 = 70%
        overall_percentage = calculate_attendance_percentage(
            self.student_profile,
            subject=None
        )
        self.assertEqual(overall_percentage, 70.0)
