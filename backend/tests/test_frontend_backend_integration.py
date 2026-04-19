"""
Integration tests for frontend routes with backend calculations.

Tests all calculation logic that the frontend depends on:
- Attendance percentage calculations
- CGPA calculations
- Grade point calculations
- Batch aggregation
- Registration tracking statistics
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from apps.users.models import StudentProfile, FacultyProfile
from apps.academics.models import Department, Course, Subject, Program
from apps.students.models import SemesterRegistration, RegisteredCourse
from apps.faculty.models import ClassAssignment
from apps.attendance.models import Attendance
from apps.exams.models import StudentGrade

User = get_user_model()


class FrontendBackendIntegrationTest(TestCase):
    """Test frontend routes with backend calculation logic."""

    def setUp(self):
        """Set up test data."""
        # Create department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='CS Department'
        )
        
        # Create program
        self.program = Program.objects.create(
            name='B.Tech Computer Science',
            code='BTECH-CS',
            department=self.department,
            duration_years=4,
            duration_semesters=8,
            total_credits=160
        )
        
        # Create course
        self.course = Course.objects.create(
            name='B.Tech CS',
            code='BTECH-CS',
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        # Create subjects
        self.subject1 = Subject.objects.create(
            name='Data Structures',
            code='CS101',
            course=self.course,
            semester=3,
            credits=4,
            is_mandatory=True
        )
        
        self.subject2 = Subject.objects.create(
            name='Algorithms',
            code='CS201',
            course=self.course,
            semester=3,
            credits=4,
            is_mandatory=True
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )
        
        # Create faculty user
        self.faculty_user = User.objects.create_user(
            username='faculty',
            password='faculty123',
            email='faculty@test.com',
            role='FACULTY',
            is_staff=True
        )
        
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='FAC001',
            department=self.department,
            designation='Professor'
        )
        
        # Create class assignments
        ClassAssignment.objects.create(
            faculty=self.faculty_profile,
            subject=self.subject1,
            semester=3,
            academic_year=2024
        )
        
        ClassAssignment.objects.create(
            faculty=self.faculty_profile,
            subject=self.subject2,
            semester=3,
            academic_year=2024
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student',
            password='student123',
            email='student@test.com',
            role='STUDENT'
        )
        
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            reg_no='2024CS001',
            enrollment_number='EN2024001',
            department=self.department,
            program=self.program,
            current_semester=3,
            batch_year=2024
        )
        
        # Create semester registration
        self.semester_reg = SemesterRegistration.objects.create(
            student=self.student_profile,
            academic_year='2024-25',
            semester=3,
            institute_fee_paid=True,
            hostel_fee_paid=False,
            total_credits=8
        )
        
        # Register courses
        RegisteredCourse.objects.create(
            semester_registration=self.semester_reg,
            subject=self.subject1,
            is_backlog=False
        )
        
        RegisteredCourse.objects.create(
            semester_registration=self.semester_reg,
            subject=self.subject2,
            is_backlog=False
        )
        
        # Create API client
        self.client = APIClient()

    def test_attendance_percentage_calculation(self):
        """Test attendance percentage calculation for student view."""
        # Login as student
        self.client.force_authenticate(user=self.student_user)
        
        # Create attendance records for subject1
        today = date.today()
        for i in range(10):
            status_value = 'Present' if i < 8 else 'Absent'
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject1,
                date=today - timedelta(days=i+1),
                status=status_value,
                recorded_by=self.faculty_user
            )
        
        # Get attendance records
        response = self.client.get('/api/attendance/my-records/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attendance_by_subject', response.data)
        
        # Find CS101 attendance
        cs101_attendance = next(
            (item for item in response.data['attendance_by_subject'] 
             if item['subject_code'] == 'CS101'),
            None
        )
        
        self.assertIsNotNone(cs101_attendance)
        self.assertEqual(cs101_attendance['total_classes'], 10)
        self.assertEqual(cs101_attendance['attended'], 8)
        self.assertEqual(cs101_attendance['absent'], 2)
        self.assertEqual(cs101_attendance['attendance_percentage'], 80.0)

    def test_batch_wise_attendance_aggregation(self):
        """Test batch-wise attendance aggregation for faculty view."""
        # Create another student in same batch
        student2_user = User.objects.create_user(
            username='student2',
            password='student123',
            email='student2@test.com',
            role='STUDENT'
        )
        
        student2_profile = StudentProfile.objects.create(
            user=student2_user,
            reg_no='2024CS002',
            enrollment_number='EN2024002',
            department=self.department,
            program=self.program,
            current_semester=3,
            batch_year=2024
        )
        
        # Create attendance for both students
        today = date.today()
        for i in range(5):
            # Student 1: 100% attendance
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject1,
                date=today - timedelta(days=i+1),
                status='Present',
                recorded_by=self.faculty_user
            )
            
            # Student 2: 60% attendance
            status_value = 'Present' if i < 3 else 'Absent'
            Attendance.objects.create(
                student=student2_profile,
                subject=self.subject1,
                date=today - timedelta(days=i+1),
                status=status_value,
                recorded_by=self.faculty_user
            )
        
        # Login as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Get batch summary
        response = self.client.get(
            '/api/attendance/faculty/summary/',
            {'subject_id': self.subject1.id, 'batch': '2024'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['students']), 2)
        
        # Verify calculations
        student1_data = next(
            (s for s in response.data['students'] if s['reg_no'] == '2024CS001'),
            None
        )
        student2_data = next(
            (s for s in response.data['students'] if s['reg_no'] == '2024CS002'),
            None
        )
        
        self.assertIsNotNone(student1_data)
        self.assertEqual(student1_data['attendance_percentage'], 100.0)
        
        self.assertIsNotNone(student2_data)
        self.assertEqual(student2_data['attendance_percentage'], 60.0)

    def test_cgpa_calculation(self):
        """Test CGPA calculation for student grades."""
        # Create grades for student
        StudentGrade.objects.create(
            student=self.student_profile,
            subject=self.subject1,
            faculty=self.faculty_profile,
            marks_obtained=85,
            total_marks=100,
            grade_letter='A'
        )
        
        StudentGrade.objects.create(
            student=self.student_profile,
            subject=self.subject2,
            faculty=self.faculty_profile,
            marks_obtained=75,
            total_marks=100,
            grade_letter='B'
        )
        
        # Login as student
        self.client.force_authenticate(user=self.student_user)
        
        # Get grades
        response = self.client.get('/api/students/my-grades/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('grades', response.data)
        self.assertIn('statistics', response.data)
        
        # Verify CGPA calculation
        # A = 10.0, B = 8.0
        # CGPA = (10.0 + 8.0) / 2 = 9.0
        stats = response.data['statistics']
        self.assertEqual(len(response.data['grades']), 2)
        self.assertEqual(stats['cgpa'], 9.0)
        self.assertEqual(stats['average_percentage'], 80.0)

    def test_grade_point_mapping(self):
        """Test grade letter to grade point mapping."""
        grade_mappings = [
            ('A', 10.0, 90),
            ('A-', 9.0, 85),
            ('B', 8.0, 75),
            ('B-', 7.0, 70),
            ('C', 6.0, 65),
            ('C-', 5.0, 60),
            ('D', 4.0, 50),
            ('F', 0.0, 30),
        ]
        
        for grade_letter, expected_points, marks in grade_mappings:
            StudentGrade.objects.create(
                student=self.student_profile,
                subject=Subject.objects.create(
                    name=f'Test Subject {grade_letter}',
                    code=f'TEST{grade_letter}',
                    course=self.course,
                    semester=3,
                    credits=4
                ),
                faculty=self.faculty_profile,
                marks_obtained=marks,
                total_marks=100,
                grade_letter=grade_letter
            )
        
        # Login as student
        self.client.force_authenticate(user=self.student_user)
        
        # Get grades
        response = self.client.get('/api/students/my-grades/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify each grade has correct grade points
        for grade in response.data['grades']:
            expected_points = next(
                (points for letter, points, _ in grade_mappings 
                 if letter == grade['grade_letter']),
                None
            )
            self.assertEqual(grade['grade_points'], expected_points)

    def test_registration_tracking_statistics(self):
        """Test registration tracking statistics for admin."""
        # Create more students
        for i in range(5):
            user = User.objects.create_user(
                username=f'student{i+2}',
                password='student123',
                email=f'student{i+2}@test.com',
                role='STUDENT'
            )
            
            profile = StudentProfile.objects.create(
                user=user,
                reg_no=f'2024CS00{i+2}',
                enrollment_number=f'EN202400{i+2}',
                department=self.department,
                program=self.program,
                current_semester=3,
                batch_year=2024
            )
            
            # Only 3 out of 5 register
            if i < 3:
                SemesterRegistration.objects.create(
                    student=profile,
                    academic_year='2024-25',
                    semester=3,
                    institute_fee_paid=True,
                    total_credits=8
                )
        
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Get registration tracking
        response = self.client.get(
            '/api/students/registration-tracking/',
            {'academic_year': '2024-25', 'semester': 3}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistics
        # Total students: 6 (1 from setUp + 5 new)
        # Registered: 4 (1 from setUp + 3 new)
        # Pending: 2
        # Percentage: 4/6 * 100 = 66.67%
        
        self.assertEqual(response.data['summary']['total_students'], 6)
        self.assertEqual(response.data['summary']['registered_count'], 4)
        self.assertEqual(response.data['summary']['pending_count'], 2)
        self.assertAlmostEqual(
            response.data['summary']['registration_percentage'],
            66.67,
            places=2
        )

    def test_attendance_with_late_status(self):
        """Test attendance calculation including late status."""
        # Create attendance with mixed statuses
        today = date.today()
        statuses = ['Present'] * 7 + ['Late'] * 2 + ['Absent'] * 1
        
        for i, status_value in enumerate(statuses):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject1,
                date=today - timedelta(days=i+1),
                status=status_value,
                recorded_by=self.faculty_user
            )
        
        # Login as student
        self.client.force_authenticate(user=self.student_user)
        
        # Get attendance
        response = self.client.get('/api/attendance/my-records/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cs101_attendance = next(
            (item for item in response.data['attendance_by_subject'] 
             if item['subject_code'] == 'CS101'),
            None
        )
        
        # Verify counts
        self.assertEqual(cs101_attendance['total_classes'], 10)
        self.assertEqual(cs101_attendance['attended'], 7)
        self.assertEqual(cs101_attendance['late'], 2)
        self.assertEqual(cs101_attendance['absent'], 1)
        
        # Attendance percentage = (Present + Late) / Total * 100
        # = (7 + 2) / 10 * 100 = 90%
        self.assertEqual(cs101_attendance['attendance_percentage'], 90.0)

    def test_subject_grades_admin_view(self):
        """Test admin view of subject grades with statistics."""
        # Create multiple students with grades
        grade_data = [
            ('2024CS010', 90, 'A'),
            ('2024CS011', 85, 'A-'),
            ('2024CS012', 75, 'B'),
            ('2024CS013', 65, 'C'),
            ('2024CS014', 45, 'F'),
        ]
        
        for reg_no, marks, grade_letter in grade_data:
            user = User.objects.create_user(
                username=reg_no,
                password='student123',
                email=f'{reg_no}@test.com',
                role='STUDENT'
            )
            
            profile = StudentProfile.objects.create(
                user=user,
                reg_no=reg_no,
                enrollment_number=f'EN{reg_no}',
                department=self.department,
                program=self.program,
                current_semester=3,
                batch_year=2024
            )
            
            StudentGrade.objects.create(
                student=profile,
                subject=self.subject1,
                faculty=self.faculty_profile,
                marks_obtained=marks,
                total_marks=100,
                grade_letter=grade_letter
            )
        
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Get subject grades
        response = self.client.get(
            '/api/admin/subject-grades/',
            {'subject_id': self.subject1.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['grades']), 5)
        
        # Verify statistics
        stats = response.data['statistics']
        self.assertEqual(stats['total_students'], 5)
        self.assertEqual(stats['passed'], 4)  # A, A-, B, C
        self.assertEqual(stats['failed'], 1)  # F
        self.assertEqual(stats['pass_percentage'], 80.0)
        self.assertEqual(stats['average_marks'], 72.0)  # (90+85+75+65+45)/5

    def test_frontend_dashboard_data_integrity(self):
        """Test that dashboard data is consistent across all roles."""
        # Create complete data set
        today = date.today()
        
        # Attendance
        for i in range(10):
            Attendance.objects.create(
                student=self.student_profile,
                subject=self.subject1,
                date=today - timedelta(days=i+1),
                status='Present' if i < 8 else 'Absent',
                recorded_by=self.faculty_user
            )
        
        # Grades
        StudentGrade.objects.create(
            student=self.student_profile,
            subject=self.subject1,
            faculty=self.faculty_profile,
            marks_obtained=85,
            total_marks=100,
            grade_letter='A'
        )
        
        # Test student dashboard
        self.client.force_authenticate(user=self.student_user)
        student_response = self.client.get('/api/auth/dashboard/student/')
        self.assertEqual(student_response.status_code, status.HTTP_200_OK)
        self.assertEqual(student_response.data['current_semester'], 3)
        self.assertEqual(student_response.data['batch_year'], 2024)
        
        # Test faculty dashboard
        self.client.force_authenticate(user=self.faculty_user)
        faculty_response = self.client.get('/api/auth/dashboard/faculty/')
        self.assertEqual(faculty_response.status_code, status.HTTP_200_OK)
        self.assertEqual(faculty_response.data['employee_id'], 'FAC001')
        
        # Verify data consistency
        self.assertEqual(
            student_response.data['department']['code'],
            faculty_response.data['department']['code']
        )

    def test_bulk_attendance_atomic_transaction(self):
        """Test that bulk attendance marking is atomic (all-or-nothing)."""
        # Login as faculty
        self.client.force_authenticate(user=self.faculty_user)
        
        # Try to mark attendance with one invalid record
        today = date.today()
        data = {
            'subject_id': self.subject1.id,
            'date': str(today),
            'records': [
                {
                    'student_id': self.student_profile.id,
                    'status': 'Present'
                },
                {
                    'student_id': 99999,  # Invalid student ID
                    'status': 'Present'
                }
            ]
        }
        
        response = self.client.post(
            '/api/attendance/bulk-mark/',
            data,
            format='json'
        )
        
        # Should fail
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no attendance was created (atomic rollback)
        attendance_count = Attendance.objects.filter(
            subject=self.subject1,
            date=today
        ).count()
        
        self.assertEqual(attendance_count, 0)

    def test_semester_registration_credit_calculation(self):
        """Test that semester registration calculates total credits correctly."""
        # Login as student
        self.client.force_authenticate(user=self.student_user)
        
        # Create new semester registration
        data = {
            'academic_year': '2025-26',
            'semester': 4,
            'institute_fee_paid': True,
            'hostel_fee_paid': False,
            'fee_transactions': [
                {
                    'utr_no': 'UTR123456',
                    'bank_name': 'Test Bank',
                    'transaction_date': str(date.today()),
                    'amount': 50000,
                    'account_debited': 'Student Account',
                    'account_credited': 'Institute Account'
                }
            ],
            'registered_courses': [
                {'subject_id': self.subject1.id, 'is_backlog': False},
                {'subject_id': self.subject2.id, 'is_backlog': False}
            ]
        }
        
        response = self.client.post(
            '/api/students/semester-register/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify total credits = 4 + 4 = 8
        self.assertEqual(response.data['total_credits'], 8)


class CalculationEdgeCasesTest(TestCase):
    """Test edge cases in calculation logic."""

    def setUp(self):
        """Set up minimal test data."""
        self.department = Department.objects.create(
            name='Test Dept',
            code='TD',
            description='Test'
        )
        
        self.program = Program.objects.create(
            name='Test Program',
            code='TP',
            department=self.department,
            duration_years=4,
            duration_semesters=8,
            total_credits=160
        )
        
        self.course = Course.objects.create(
            name='Test Course',
            code='TC',
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        self.subject = Subject.objects.create(
            name='Test Subject',
            code='TS101',
            course=self.course,
            semester=1,
            credits=4
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            email='test@test.com',
            role='STUDENT'
        )
        
        self.profile = StudentProfile.objects.create(
            user=self.user,
            reg_no='2024TEST001',
            enrollment_number='EN2024TEST001',
            department=self.department,
            program=self.program,
            current_semester=1,
            batch_year=2024
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_attendance_percentage_with_zero_classes(self):
        """Test attendance percentage when no classes have been conducted."""
        response = self.client.get('/api/attendance/my-records/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty list or 0% attendance
        self.assertIn('attendance_by_subject', response.data)

    def test_cgpa_with_no_grades(self):
        """Test CGPA calculation when student has no grades."""
        response = self.client.get('/api/students/my-grades/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['grades']), 0)
        self.assertEqual(response.data['statistics']['cgpa'], 0.0)

    def test_attendance_percentage_all_late(self):
        """Test attendance percentage when all classes are marked late."""
        faculty_user = User.objects.create_user(
            username='faculty',
            password='faculty123',
            role='FACULTY',
            is_staff=True
        )
        
        today = date.today()
        for i in range(5):
            Attendance.objects.create(
                student=self.profile,
                subject=self.subject,
                date=today - timedelta(days=i+1),
                status='Late',
                recorded_by=faculty_user
            )
        
        response = self.client.get('/api/attendance/my-records/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        subject_attendance = next(
            (item for item in response.data['attendance_by_subject'] 
             if item['subject_code'] == 'TS101'),
            None
        )
        
        # All late should count as attended
        self.assertEqual(subject_attendance['attendance_percentage'], 100.0)


print("✅ Frontend-Backend Integration Tests Created")
print("Run with: python manage.py test backend.tests.test_frontend_backend_integration")
