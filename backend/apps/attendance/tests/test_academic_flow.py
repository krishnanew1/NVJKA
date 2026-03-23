"""
Integration test: full academic cycle — department → course → subject →
faculty assignment → student enrollment → attendance marking.

Covers:
  - Assigned faculty can mark attendance (201)
  - Unassigned faculty is rejected with 403
  - Attendance record persists in the database
"""
import datetime
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Department, Course, Subject
from apps.users.models import CustomUser, StudentProfile, FacultyProfile
from apps.faculty.models import ClassAssignment
from apps.students.models import Enrollment
from apps.attendance.models import Attendance


def _jwt(user):
    """Return a Bearer token string for the given user."""
    return f"Bearer {RefreshToken.for_user(user).access_token}"


class AcademicFlowIntegrationTest(TransactionTestCase):
    """
    Simulates a complete academic cycle and validates attendance marking rules.

    Uses TransactionTestCase so MySQL actually truncates tables between tests,
    keeping AUTO_INCREMENT counters in sync with the inserted rows.
    """

    def setUp(self):
        # ── Academic structure ──────────────────────────────────────────────
        self.department = Department.objects.create(
            name='Computer Science',
            code='CSE',
        )
        self.course = Course.objects.create(
            name='Bachelor of Technology',
            code='BTECH-CSE',
            department=self.department,
            credits=160,
            duration_years=4,
        )
        self.subject = Subject.objects.create(
            name='Data Structures',
            code='CS201',
            course=self.course,
            semester=2,
            credits=4,
        )

        # ── Assigned faculty ────────────────────────────────────────────────
        self.faculty_user = CustomUser.objects.create_user(
            username='faculty_assigned',
            password='pass1234',
            role='FACULTY',
        )
        self.faculty_profile = FacultyProfile.objects.create(
            user=self.faculty_user,
            employee_id='EMP001',
            department=self.department,
            designation='Assistant Professor',
        )
        ClassAssignment.objects.create(
            faculty=self.faculty_profile,
            subject=self.subject,
            semester=2,
            academic_year=2026,
        )

        # ── Unassigned faculty ──────────────────────────────────────────────
        self.other_faculty_user = CustomUser.objects.create_user(
            username='faculty_other',
            password='pass1234',
            role='FACULTY',
        )
        self.other_faculty_profile = FacultyProfile.objects.create(
            user=self.other_faculty_user,
            employee_id='EMP002',
            department=self.department,
            designation='Lecturer',
        )
        # NOTE: no ClassAssignment for other_faculty_profile + subject

        # ── Student ─────────────────────────────────────────────────────────
        # Note: the post_save signal auto-creates a StudentProfile for STUDENT
        # users, so we use update_or_create to set the real fields.
        self.student_user = CustomUser.objects.create_user(
            username='student_one',
            password='pass1234',
            role='STUDENT',
        )
        self.student_profile, _ = StudentProfile.objects.update_or_create(
            user=self.student_user,
            defaults={
                'enrollment_number': 'STU2026001',
                'department': self.department,
                'current_semester': 2,
                'batch_year': 2026,
            },
        )
        Enrollment.objects.create(
            student=self.student_profile,
            course=self.course,
            semester=2,
            status='Active',
        )

        self.url = reverse('attendance:bulk_mark_attendance')
        self.today = datetime.date.today().isoformat()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _client_for(self, user):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=_jwt(user))
        return client

    def _payload(self, student_id=None, status='Present'):
        return {
            'subject_id': self.subject.id,
            'date': self.today,
            'records': [
                {'student_id': student_id or self.student_profile.id, 'status': status}
            ],
        }

    # ── tests ─────────────────────────────────────────────────────────────────

    def test_assigned_faculty_can_mark_attendance(self):
        """Assigned faculty receives 201 and the record is saved to the DB."""
        client = self._client_for(self.faculty_user)
        response = client.post(self.url, self._payload(), format='json')

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['subject']['code'], 'CS201')

        # Verify the record actually exists in the database
        self.assertTrue(
            Attendance.objects.filter(
                student=self.student_profile,
                subject=self.subject,
                date=datetime.date.today(),
                status='Present',
                recorded_by=self.faculty_user,
            ).exists()
        )

    def test_unassigned_faculty_receives_403(self):
        """Faculty not assigned to the subject is forbidden."""
        client = self._client_for(self.other_faculty_user)
        response = client.post(self.url, self._payload(), format='json')

        self.assertEqual(response.status_code, 403, response.data)
        self.assertIn('not assigned', response.data.get('error', '').lower())

    def test_student_cannot_mark_attendance(self):
        """Students are not allowed to call this endpoint."""
        client = self._client_for(self.student_user)
        response = client.post(self.url, self._payload(), format='json')

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_request_is_rejected(self):
        """Unauthenticated requests must be rejected."""
        response = APIClient().post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, 401)

    def test_admin_can_mark_attendance_without_assignment(self):
        """Admin bypasses the ClassAssignment check."""
        admin_user = CustomUser.objects.create_user(
            username='admin_user',
            password='pass1234',
            role='ADMIN',
        )
        client = self._client_for(admin_user)
        response = client.post(self.url, self._payload(), format='json')

        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(
            Attendance.objects.filter(
                student=self.student_profile,
                subject=self.subject,
                recorded_by=admin_user,
            ).exists()
        )

    def test_duplicate_attendance_returns_409(self):
        """Submitting the same student+subject+date twice returns 409."""
        client = self._client_for(self.faculty_user)
        client.post(self.url, self._payload(), format='json')           # first mark
        response = client.post(self.url, self._payload(), format='json')  # duplicate

        self.assertEqual(response.status_code, 409, response.data)

    def test_future_date_is_rejected(self):
        """Attendance for a future date must be rejected."""
        future = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        payload = {
            'subject_id': self.subject.id,
            'date': future,
            'records': [{'student_id': self.student_profile.id, 'status': 'Present'}],
        }
        client = self._client_for(self.faculty_user)
        response = client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, 400, response.data)

    def test_invalid_status_is_rejected(self):
        """An unrecognised status value must be rejected before any DB write."""
        payload = {
            'subject_id': self.subject.id,
            'date': self.today,
            'records': [{'student_id': self.student_profile.id, 'status': 'PRESENT'}],
        }
        client = self._client_for(self.faculty_user)
        response = client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, 400, response.data)

    def test_nonexistent_student_returns_404(self):
        """A student_id that doesn't exist should return 404."""
        payload = {
            'subject_id': self.subject.id,
            'date': self.today,
            'records': [{'student_id': 99999, 'status': 'Present'}],
        }
        client = self._client_for(self.faculty_user)
        response = client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, 404, response.data)

    def test_per_student_status_is_persisted_correctly(self):
        """Each record's individual status is saved, not a shared one."""
        user2 = CustomUser.objects.create_user(
            username='student_two', password='pass1234', role='STUDENT'
        )
        student2, _ = StudentProfile.objects.update_or_create(
            user=user2,
            defaults={
                'enrollment_number': 'STU2026002',
                'department': self.department,
                'current_semester': 2,
                'batch_year': 2026,
            },
        )
        payload = {
            'subject_id': self.subject.id,
            'date': self.today,
            'records': [
                {'student_id': self.student_profile.id, 'status': 'Present'},
                {'student_id': student2.id, 'status': 'Absent'},
            ],
        }
        client = self._client_for(self.faculty_user)
        response = client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(
            Attendance.objects.get(student=self.student_profile, subject=self.subject).status,
            'Present',
        )
        self.assertEqual(
            Attendance.objects.get(student=student2, subject=self.subject).status,
            'Absent',
        )
