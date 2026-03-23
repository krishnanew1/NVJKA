"""
End-to-end system test: full academic demo flow.

Scenario
--------
1.  An Admin authenticates and receives a JWT token.
2.  Academic structure is created: Department → Course → Subject (4 credits).
3.  A Faculty member is created and assigned to the Subject via ClassAssignment.
4.  A Student is created and enrolled in the Course.
5.  The assigned Faculty marks attendance for the Student (Present).
6.  Two exam assessments are created (Midterm 80/100, Final 90/100).
7.  Grades are posted for both assessments.
8.  The Transcript API is called and the returned CGPA is asserted.

Expected GPA calculation
------------------------
    Midterm : 80 / 100 = 80.0 %  → grade_point = 8.0
    Final   : 90 / 100 = 90.0 %  → grade_point = 9.0
    avg_percentage = (80 + 90) / 2 = 85.0 %
    grade_point    = 85.0 / 10   = 8.5
    GPA            = (8.5 × 4 credits) / 4 credits = 8.5
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
from apps.exams.models import Assessment, Grade


# ── helpers ───────────────────────────────────────────────────────────────────

def _bearer(user):
    """Return a valid Bearer token string for *user*."""
    return f"Bearer {RefreshToken.for_user(user).access_token}"


def _authed(user):
    """Return an APIClient pre-loaded with *user*'s JWT."""
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=_bearer(user))
    return c


# ── test class ────────────────────────────────────────────────────────────────

class FinalSystemTest(TransactionTestCase):
    """
    Full end-to-end integration test covering authentication, academic setup,
    attendance marking, grade posting, and GPA calculation.

    Uses ``TransactionTestCase`` so MySQL's AUTO_INCREMENT counters are reset
    between tests (avoids OneToOne duplicate-key errors from the signal that
    auto-creates StudentProfile).
    """

    # ── Expected GPA (pre-calculated, see module docstring) ──────────────────
    EXPECTED_GPA = 8.5

    def setUp(self):
        """Build the complete academic world needed for every test method."""

        # ── 1. Admin user ─────────────────────────────────────────────────────
        self.admin = CustomUser.objects.create_user(
            username='admin_demo',
            password='Admin@1234',
            role='ADMIN',
            is_staff=True,
        )

        # ── 2. Academic structure ─────────────────────────────────────────────
        self.department = Department.objects.create(
            name='Computer Science',
            code='CSE',
        )
        self.course = Course.objects.create(
            name='B.Tech Computer Science',
            code='BTECH-CS',
            department=self.department,
            credits=160,
            duration_years=4,
        )
        # Subject with 4 credits — used in GPA weighting
        self.subject = Subject.objects.create(
            name='Data Structures',
            code='CS301',
            course=self.course,
            semester=3,
            credits=4,
        )

        # ── 3. Faculty ────────────────────────────────────────────────────────
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_demo',
            password='Faculty@1234',
            role='FACULTY',
        )
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='EMP-DEMO-01',
            department=self.department,
            designation='Assistant Professor',
        )
        self.assignment = ClassAssignment.objects.create(
            faculty=self.faculty_profile,
            subject=self.subject,
            semester=3,
            academic_year=2026,
        )

        # ── 4. Student ────────────────────────────────────────────────────────
        self.student_user = CustomUser.objects.create_user(
            username='student_demo',
            password='Student@1234',
            role='STUDENT',
        )
        # Signal auto-creates a StudentProfile; update it with real data.
        self.student_profile, _ = StudentProfile.objects.update_or_create(
            user=self.student_user,
            defaults={
                'enrollment_number': 'STU-DEMO-001',
                'department': self.department,
                'current_semester': 3,
                'batch_year': 2024,
            },
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student_profile,
            course=self.course,
            semester=3,
            status='Active',
        )

        # ── 5. Assessments ────────────────────────────────────────────────────
        self.midterm = Assessment.objects.create(
            name='Midterm',
            subject=self.subject,
            max_marks=Decimal('100'),
            weightage=Decimal('40'),
        )
        self.final = Assessment.objects.create(
            name='Final',
            subject=self.subject,
            max_marks=Decimal('100'),
            weightage=Decimal('60'),
        )

        # ── URL shortcuts ─────────────────────────────────────────────────────
        self.attendance_url = reverse('attendance:bulk_mark_attendance')
        self.transcript_url = reverse(
            'exams:student_transcript',
            kwargs={'student_id': self.student_profile.id},
        )
        self.today = datetime.date.today().isoformat()

    # ── Step 1: Authentication ────────────────────────────────────────────────

    def test_01_jwt_authentication(self):
        """
        Posting valid credentials to the token endpoint must return
        both access and refresh tokens.
        """
        url = reverse('users:token_obtain_pair')
        response = APIClient().post(
            url,
            {'username': 'admin_demo', 'password': 'Admin@1234'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    # ── Step 2: Academic structure already created in setUp ───────────────────

    def test_02_academic_structure_exists(self):
        """Department, Course, Subject, ClassAssignment are all persisted."""
        self.assertEqual(Department.objects.filter(code='CSE').count(), 1)
        self.assertEqual(Course.objects.filter(code='BTECH-CS').count(), 1)
        self.assertEqual(Subject.objects.filter(code='CS301').count(), 1)
        self.assertTrue(
            ClassAssignment.objects.filter(
                faculty=self.faculty_profile,
                subject=self.subject,
            ).exists()
        )

    # ── Step 3: Student enrollment ────────────────────────────────────────────

    def test_03_student_enrollment_exists(self):
        """Student is enrolled in the course with Active status."""
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student_profile,
                course=self.course,
                status='Active',
            ).exists()
        )

    # ── Step 4: Mark attendance via API ──────────────────────────────────────

    def test_04_faculty_marks_attendance(self):
        """
        Assigned faculty can mark attendance for the student.
        The record must be persisted with status Present.
        """
        client = _authed(self.faculty_user)
        payload = {
            'subject_id': self.subject.id,
            'date': self.today,
            'records': [
                {'student_id': self.student_profile.id, 'status': 'Present'},
            ],
        }
        response = client.post(self.attendance_url, payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)

        record = Attendance.objects.get(
            student=self.student_profile,
            subject=self.subject,
            date=datetime.date.today(),
        )
        self.assertEqual(record.status, 'Present')
        self.assertEqual(record.recorded_by, self.faculty_user)

    # ── Step 5: Post exam grades via API ──────────────────────────────────────

    def _post_grade(self, assessment, marks):
        """Helper: POST a grade via the grades API as admin."""
        url = reverse('exams:grade-list')
        client = _authed(self.admin)
        response = client.post(
            url,
            {
                'student': self.student_profile.id,
                'assessment': assessment.id,
                'marks_obtained': str(marks),
            },
            format='json',
        )
        return response

    def test_05_post_exam_grades(self):
        """
        Admin can post Midterm (80/100) and Final (90/100) grades.
        Both Grade records must be persisted with correct marks.
        """
        r1 = self._post_grade(self.midterm, '80.00')
        self.assertEqual(r1.status_code, 201, r1.data)

        r2 = self._post_grade(self.final, '90.00')
        self.assertEqual(r2.status_code, 201, r2.data)

        self.assertEqual(
            Grade.objects.filter(student=self.student_profile).count(), 2
        )
        midterm_grade = Grade.objects.get(
            student=self.student_profile, assessment=self.midterm
        )
        self.assertEqual(midterm_grade.marks_obtained, Decimal('80.00'))

    # ── Step 6: Transcript API + GPA assertion ────────────────────────────────

    def test_06_transcript_gpa_matches_expected(self):
        """
        THE ULTIMATE ASSERT.

        After posting Midterm=80 and Final=90 for a 4-credit subject:

            avg_percentage = (80 + 90) / 2 = 85.0
            grade_point    = 85.0 / 10     = 8.5
            GPA            = (8.5 × 4) / 4 = 8.5

        The Transcript API must return gpa == 8.5.
        """
        # Post grades first
        self._post_grade(self.midterm, '80.00')
        self._post_grade(self.final, '90.00')

        # Call transcript as admin
        client = _authed(self.admin)
        response = client.get(self.transcript_url)

        self.assertEqual(response.status_code, 200, response.data)

        data = response.data
        # Student info
        self.assertEqual(
            data['student']['enrollment_number'], 'STU-DEMO-001'
        )
        # Subject breakdown
        self.assertEqual(len(data['subjects']), 1)
        subject_entry = data['subjects'][0]
        self.assertEqual(subject_entry['subject_code'], 'CS301')
        self.assertAlmostEqual(
            float(subject_entry['average_percentage']), 85.0, places=1
        )
        self.assertAlmostEqual(
            float(subject_entry['grade_point']), 8.5, places=1
        )
        # Final CGPA
        self.assertAlmostEqual(
            float(data['gpa']), self.EXPECTED_GPA, places=1,
            msg=(
                f"Expected GPA {self.EXPECTED_GPA} but got {data['gpa']}. "
                f"Full response: {data}"
            ),
        )

    # ── Step 7: Student can only see their own transcript ─────────────────────

    def test_07_student_cannot_view_other_transcript(self):
        """
        A student requesting another student's transcript must receive 403.
        """
        other_user = CustomUser.objects.create_user(
            username='other_student', password='pass1234', role='STUDENT'
        )
        # other_student tries to read self.student_profile's transcript
        client = _authed(other_user)
        response = client.get(self.transcript_url)
        self.assertEqual(response.status_code, 403, response.data)

    # ── Step 8: Student can view their own transcript ─────────────────────────

    def test_08_student_can_view_own_transcript(self):
        """Student calling the transcript endpoint for themselves gets 200."""
        self._post_grade(self.midterm, '80.00')
        self._post_grade(self.final, '90.00')

        client = _authed(self.student_user)
        response = client.get(self.transcript_url)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertAlmostEqual(float(response.data['gpa']), self.EXPECTED_GPA, places=1)
