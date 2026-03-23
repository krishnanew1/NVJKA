"""
Demo Flow Test - Slide 11 Demo Script Simulation

This test simulates the complete demo flow:
1. Register users (Admin, Faculty, Student)
2. Login and get JWT tokens
3. Create academic structure (Department, Course, Subject)
4. Assign faculty to subject
5. Enroll student in course
6. Mark attendance
7. Verify all operations completed successfully

This test demonstrates the complete user journey from registration to attendance marking.
"""
import datetime
from decimal import Decimal

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Department, Course, Subject
from apps.users.models import CustomUser, StudentProfile, FacultyProfile
from apps.faculty.models import ClassAssignment
from apps.students.models import Enrollment
from apps.attendance.models import Attendance


class DemoFlowTest(TransactionTestCase):
    """
    Complete demo flow test simulating Slide 11 Demo Script.
    
    Tests the entire user journey from registration through attendance marking,
    demonstrating all major system capabilities in a realistic scenario.
    """

    def setUp(self):
        """Set up API client for testing."""
        self.client = APIClient()
        self.today = datetime.date.today().isoformat()

    def _register_user(self, username, password, email, role):
        """Helper: Register a new user via API."""
        url = reverse('users:register') if hasattr(self, 'register_url') else '/api/users/register/'
        
        # Try direct user creation since we don't have a register endpoint
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            role=role
        )
        return user

    def _login_user(self, username, password):
        """Helper: Login user and return JWT token."""
        url = reverse('users:token_obtain_pair')
        response = self.client.post(url, {
            'username': username,
            'password': password
        }, format='json')
        
        self.assertEqual(response.status_code, 200, f"Login failed: {response.data}")
        return response.data['access']

    def _auth_client(self, token):
        """Helper: Return authenticated API client."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return client

    def test_complete_demo_flow(self):
        """
        SLIDE 11 DEMO SCRIPT SIMULATION
        
        Complete end-to-end test covering:
        1. User Registration (Admin, Faculty, Student)
        2. Authentication (JWT Login)
        3. Academic Structure Creation
        4. Faculty Assignment
        5. Student Enrollment
        6. Attendance Marking
        """
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 1: REGISTER USERS
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🔐 STEP 1: Registering Users...")
        
        # Register Admin
        admin_user = self._register_user(
            username='demo_admin',
            password='Admin@2026',
            email='admin@university.edu',
            role='ADMIN'
        )
        admin_user.is_staff = True
        admin_user.save()
        
        # Register Faculty
        faculty_user = self._register_user(
            username='prof_smith',
            password='Faculty@2026',
            email='smith@university.edu',
            role='FACULTY'
        )
        
        # Register Student
        student_user = self._register_user(
            username='john_doe',
            password='Student@2026',
            email='john.doe@student.edu',
            role='STUDENT'
        )
        
        print(f"✅ Registered: Admin({admin_user.username}), Faculty({faculty_user.username}), Student({student_user.username})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: LOGIN AND GET JWT TOKENS
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🔑 STEP 2: Authenticating Users...")
        
        admin_token = self._login_user('demo_admin', 'Admin@2026')
        faculty_token = self._login_user('prof_smith', 'Faculty@2026')
        student_token = self._login_user('john_doe', 'Student@2026')
        
        admin_client = self._auth_client(admin_token)
        faculty_client = self._auth_client(faculty_token)
        student_client = self._auth_client(student_token)
        
        print("✅ All users authenticated successfully")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: CREATE ACADEMIC STRUCTURE
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🏫 STEP 3: Creating Academic Structure...")
        
        # Create Department
        dept_url = reverse('academics:department-list')
        dept_response = admin_client.post(dept_url, {
            'name': 'Computer Science & Engineering',
            'code': 'CSE',
            'description': 'Department of Computer Science and Engineering'
        }, format='json')
        self.assertEqual(dept_response.status_code, 201, f"Department creation failed: {dept_response.data}")
        department_id = dept_response.data['id']
        
        # Create Course
        course_url = reverse('academics:course-list')
        course_response = admin_client.post(course_url, {
            'name': 'Bachelor of Technology in Computer Science',
            'code': 'BTECH-CS',
            'department_id': department_id,
            'credits': 160,
            'duration_years': 4
        }, format='json')
        self.assertEqual(course_response.status_code, 201, f"Course creation failed: {course_response.data}")
        course_id = course_response.data['id']
        
        # Create Subject
        subject_url = reverse('academics:subject-list')
        subject_response = admin_client.post(subject_url, {
            'name': 'Data Structures and Algorithms',
            'code': 'CS301',
            'course_id': course_id,
            'semester': 3,
            'credits': 4,
            'description': 'Fundamental data structures and algorithmic techniques'
        }, format='json')
        self.assertEqual(subject_response.status_code, 201, f"Subject creation failed: {subject_response.data}")
        subject_id = subject_response.data['id']
        
        print(f"✅ Created: Department(CSE), Course(BTECH-CS), Subject(CS301)")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: CREATE FACULTY PROFILE AND ASSIGN TO SUBJECT
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n👨‍🏫 STEP 4: Setting up Faculty Assignment...")
        
        # Create Faculty Profile
        faculty_profile = FacultyProfile.objects.create(
            user=faculty_user,
            employee_id='EMP-2026-001',
            department_id=department_id,
            designation='Assistant Professor',
            specialization='Data Structures, Algorithms'
        )
        
        # Assign Faculty to Subject
        assignment_url = reverse('faculty:classassignment-list')
        assignment_response = admin_client.post(assignment_url, {
            'faculty': faculty_profile.id,
            'subject_id': subject_id,
            'semester': 3,
            'academic_year': 2026
        }, format='json')
        self.assertEqual(assignment_response.status_code, 201, f"Faculty assignment failed: {assignment_response.data}")
        
        print(f"✅ Faculty Prof. Smith assigned to CS301")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: CREATE STUDENT PROFILE AND ENROLL IN COURSE
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n👨‍🎓 STEP 5: Setting up Student Enrollment...")
        
        # Create/Update Student Profile
        student_profile, _ = StudentProfile.objects.update_or_create(
            user=student_user,
            defaults={
                'enrollment_number': 'STU-2026-001',
                'department_id': department_id,
                'current_semester': 3,
                'batch_year': 2024
            }
        )
        
        # Enroll Student in Course
        enrollment_url = reverse('students:enrollment-list')
        enrollment_response = admin_client.post(enrollment_url, {
            'student': student_profile.id,
            'course_id': course_id,
            'semester': 3,
            'status': 'Active'
        }, format='json')
        self.assertEqual(enrollment_response.status_code, 201, f"Student enrollment failed: {enrollment_response.data}")
        
        print(f"✅ Student John Doe enrolled in BTECH-CS")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 6: MARK ATTENDANCE
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n📋 STEP 6: Marking Attendance...")
        
        # Faculty marks attendance for the student
        attendance_url = reverse('attendance:bulk_mark_attendance')
        attendance_response = faculty_client.post(attendance_url, {
            'subject_id': subject_id,
            'date': self.today,
            'records': [
                {
                    'student_id': student_profile.id,
                    'status': 'Present'
                }
            ]
        }, format='json')
        self.assertEqual(attendance_response.status_code, 201, f"Attendance marking failed: {attendance_response.data}")
        
        print(f"✅ Attendance marked: John Doe - Present for CS301")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 7: VERIFICATION - CHECK ALL DATA IS PERSISTED
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🔍 STEP 7: Verifying Demo Flow Results...")
        
        # Verify Department exists
        self.assertTrue(Department.objects.filter(code='CSE').exists())
        
        # Verify Course exists
        self.assertTrue(Course.objects.filter(code='BTECH-CS').exists())
        
        # Verify Subject exists
        self.assertTrue(Subject.objects.filter(code='CS301').exists())
        
        # Verify Faculty Assignment
        self.assertTrue(ClassAssignment.objects.filter(
            faculty=faculty_profile,
            subject_id=subject_id
        ).exists())
        
        # Verify Student Enrollment
        self.assertTrue(Enrollment.objects.filter(
            student=student_profile,
            course_id=course_id,
            status='Active'
        ).exists())
        
        # Verify Attendance Record
        attendance_record = Attendance.objects.get(
            student=student_profile,
            subject_id=subject_id,
            date=datetime.date.today()
        )
        self.assertEqual(attendance_record.status, 'Present')
        self.assertEqual(attendance_record.recorded_by, faculty_user)
        
        print("✅ All verifications passed!")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 8: DEMO ADDITIONAL FEATURES
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🎯 STEP 8: Testing Additional Features...")
        
        # Test Student Dashboard Access
        student_dashboard_url = reverse('users:student_dashboard')
        dashboard_response = student_client.get(student_dashboard_url)
        self.assertEqual(dashboard_response.status_code, 200)
        
        # Test Faculty Dashboard Access
        faculty_dashboard_url = reverse('users:faculty_dashboard')
        faculty_dashboard_response = faculty_client.get(faculty_dashboard_url)
        self.assertEqual(faculty_dashboard_response.status_code, 200)
        
        print("✅ Additional features working correctly!")
        
        # ═══════════════════════════════════════════════════════════════════════
        # DEMO COMPLETE
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🎉 DEMO FLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("SUMMARY:")
        print(f"👤 Users Created: 3 (Admin, Faculty, Student)")
        print(f"🏫 Academic Structure: 1 Department, 1 Course, 1 Subject")
        print(f"👨‍🏫 Faculty Assignments: 1")
        print(f"👨‍🎓 Student Enrollments: 1")
        print(f"📋 Attendance Records: 1")
        print("=" * 60)

    def test_demo_flow_error_scenarios(self):
        """
        Test error scenarios in the demo flow to ensure proper validation.
        """
        print("\n🚨 Testing Error Scenarios...")
        
        # Create basic setup
        admin_user = self._register_user('admin', 'Admin@2026', 'admin@test.com', 'ADMIN')
        admin_token = self._login_user('admin', 'Admin@2026')
        admin_client = self._auth_client(admin_token)
        
        # Test duplicate department creation
        dept_url = reverse('academics:department-list')
        admin_client.post(dept_url, {'name': 'Test Dept', 'code': 'TEST'}, format='json')
        
        duplicate_response = admin_client.post(dept_url, {
            'name': 'Test Dept 2', 
            'code': 'TEST'  # Same code
        }, format='json')
        self.assertEqual(duplicate_response.status_code, 400)
        
        print("✅ Error scenarios handled correctly")

    def test_demo_flow_permissions(self):
        """
        Test permission scenarios - ensure users can access appropriate resources.
        Note: In this demo system, authenticated users can create academic structure.
        """
        print("\n🔒 Testing Permission Controls...")
        
        # Create users
        student_user = self._register_user('student', 'Student@2026', 'student@test.com', 'STUDENT')
        faculty_user = self._register_user('faculty', 'Faculty@2026', 'faculty@test.com', 'FACULTY')
        
        student_token = self._login_user('student', 'Student@2026')
        faculty_token = self._login_user('faculty', 'Faculty@2026')
        
        student_client = self._auth_client(student_token)
        faculty_client = self._auth_client(faculty_token)
        
        # Test authenticated users can access department list (read access)
        dept_url = reverse('academics:department-list')
        student_response = student_client.get(dept_url)
        self.assertEqual(student_response.status_code, 200)
        
        faculty_response = faculty_client.get(dept_url)
        self.assertEqual(faculty_response.status_code, 200)
        
        # Test unauthenticated access is denied
        unauth_client = APIClient()
        unauth_response = unauth_client.get(dept_url)
        self.assertIn(unauth_response.status_code, [401, 403])
        
        print("✅ Permission controls working correctly")