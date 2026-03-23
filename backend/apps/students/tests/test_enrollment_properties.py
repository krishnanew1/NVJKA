"""
Property-based tests for Student Enrollment Validation.

Property: For any generated student and course, the system must strictly
prevent a second 'Active' enrollment for the same student in the same
course during the same semester.

Validates: Requirements 2.2 and 8.4
Runs minimum 100 iterations via Hypothesis settings.
"""
from django.db import IntegrityError

from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase  # Required for DB transaction isolation

from apps.users.models import CustomUser, StudentProfile
from apps.academics.models import Department, Course
from apps.students.models import Enrollment


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_department(suffix: str) -> Department:
    return Department.objects.get_or_create(
        code=f"D{suffix}",
        defaults={"name": f"Department {suffix}"}
    )[0]


def make_course(department: Department, suffix: str) -> Course:
    return Course.objects.get_or_create(
        code=f"C{suffix}",
        defaults={
            "name": f"Course {suffix}",
            "department": department,
            "credits": 4,
            "duration_years": 4,
        }
    )[0]


def make_student(suffix: str) -> StudentProfile:
    user, _ = CustomUser.objects.get_or_create(
        username=f"student_{suffix}",
        defaults={
            "email": f"student_{suffix}@test.com",
            "role": "STUDENT",
        }
    )
    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "enrollment_number": f"ENR{suffix}",
            "batch_year": 2024,
        }
    )
    return profile


# ---------------------------------------------------------------------------
# Property-based test class
# ---------------------------------------------------------------------------

class EnrollmentDuplicatePreventionPropertyTest(TestCase):
    """
    Property: Duplicate Active enrollment for the same (student, course, semester)
    must always be rejected — regardless of the generated input values.
    """

    @given(
        student_suffix=st.from_regex(r"[A-Z]{4}[0-9]{3}", fullmatch=True),
        course_suffix=st.from_regex(r"[A-Z]{3}[0-9]{3}", fullmatch=True),
        semester=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_duplicate_active_enrollment_is_rejected(
        self, student_suffix, course_suffix, semester
    ):
        """
        Property: Creating a second Active enrollment for the same
        (student, course, semester) triple must always raise IntegrityError.

        Validates Requirements 2.2 and 8.4.
        """
        dept = make_department(course_suffix[:3])
        course = make_course(dept, course_suffix)
        student = make_student(student_suffix)

        # First enrollment — must always succeed
        Enrollment.objects.filter(
            student=student, course=course, semester=semester
        ).delete()

        first = Enrollment.objects.create(
            student=student,
            course=course,
            semester=semester,
            status="Active",
        )
        self.assertEqual(first.status, "Active")

        # Second enrollment with identical (student, course, semester) — must fail
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=student,
                course=course,
                semester=semester,
                status="Active",
            )

    @given(
        student_suffix=st.from_regex(r"[A-Z]{4}[0-9]{3}", fullmatch=True),
        course_suffix=st.from_regex(r"[A-Z]{3}[0-9]{3}", fullmatch=True),
        semester=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_different_semester_allows_new_enrollment(
        self, student_suffix, course_suffix, semester
    ):
        """
        Property: The same student can enroll in the same course in a
        *different* semester — the constraint is (student, course, semester).

        Validates that the unique_together constraint is scoped correctly.
        """
        # Ensure two distinct semesters exist
        assume(semester < 10)
        other_semester = semester + 1

        dept = make_department(course_suffix[:3])
        course = make_course(dept, course_suffix)
        student = make_student(student_suffix)

        # Clean slate for this combination
        Enrollment.objects.filter(
            student=student, course=course
        ).delete()

        e1 = Enrollment.objects.create(
            student=student, course=course,
            semester=semester, status="Active"
        )
        e2 = Enrollment.objects.create(
            student=student, course=course,
            semester=other_semester, status="Active"
        )

        self.assertNotEqual(e1.pk, e2.pk)
        self.assertEqual(
            Enrollment.objects.filter(student=student, course=course).count(), 2
        )

    @given(
        student_suffix=st.from_regex(r"[A-Z]{4}[0-9]{3}", fullmatch=True),
        course_suffix_a=st.from_regex(r"[A-Z]{3}[0-9]{3}", fullmatch=True),
        course_suffix_b=st.from_regex(r"[A-Z]{3}[0-9]{3}", fullmatch=True),
        semester=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_same_student_different_courses_same_semester_is_allowed(
        self, student_suffix, course_suffix_a, course_suffix_b, semester
    ):
        """
        Property: A student can be enrolled in two *different* courses
        in the same semester — only identical (student, course, semester)
        triples are blocked.
        """
        assume(course_suffix_a != course_suffix_b)

        dept = make_department("GEN")
        course_a = make_course(dept, course_suffix_a)
        course_b = make_course(dept, course_suffix_b)
        student = make_student(student_suffix)

        # Clean slate
        Enrollment.objects.filter(
            student=student, course__in=[course_a, course_b], semester=semester
        ).delete()

        e1 = Enrollment.objects.create(
            student=student, course=course_a,
            semester=semester, status="Active"
        )
        e2 = Enrollment.objects.create(
            student=student, course=course_b,
            semester=semester, status="Active"
        )

        self.assertNotEqual(e1.pk, e2.pk)

    @given(
        student_suffix=st.from_regex(r"[A-Z]{4}[0-9]{3}", fullmatch=True),
        course_suffix=st.from_regex(r"[A-Z]{3}[0-9]{3}", fullmatch=True),
        semester=st.integers(min_value=1, max_value=10),
        status=st.sampled_from(["Completed", "Dropped"]),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_non_active_status_still_blocked_by_unique_constraint(
        self, student_suffix, course_suffix, semester, status
    ):
        """
        Property: The unique_together constraint applies regardless of status.
        Even a Dropped/Completed re-enrollment for the same semester is blocked
        at the database level, preventing any data inconsistency.
        """
        dept = make_department(course_suffix[:3])
        course = make_course(dept, course_suffix)
        student = make_student(student_suffix)

        Enrollment.objects.filter(
            student=student, course=course, semester=semester
        ).delete()

        Enrollment.objects.create(
            student=student, course=course,
            semester=semester, status="Active"
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=student, course=course,
                semester=semester, status=status,
            )
