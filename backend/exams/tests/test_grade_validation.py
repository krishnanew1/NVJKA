from django.test import TestCase
from django.core.exceptions import ValidationError
from exams.models import Assessment, Grade
from academics.models import Subject, Course, Department
from users.models import CustomUser
from students.models import Enrollment


class GradeValidationTestCase(TestCase):
    """Test Grade model validation logic"""

    def setUp(self):
        # Create department
        self.department = Department.objects.create(
            name="Computer Science",
            code="CS"
        )

        # Create course
        self.course = Course.objects.create(
            name="B.Tech Computer Science",
            code="BTCS",
            department=self.department,
            credits=160,
            duration_years=4
        )

        # Create subject
        self.subject = Subject.objects.create(
            name="Data Structures",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4
        )

        # Create student user (signal will auto-create StudentProfile)
        self.student_user = CustomUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass123",
            role="STUDENT"
        )

        # Get the auto-created student profile and update it
        self.student_profile = self.student_user.student_profile
        self.student_profile.enrollment_number = "2026CS001"
        self.student_profile.batch_year = 2026
        self.student_profile.save()

        # Create enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student_profile,
            course=self.course,
            status="ENROLLED"
        )

        # Create assessment
        self.assessment = Assessment.objects.create(
            name="Midterm Exam",
            subject=self.subject,
            max_marks=100,
            weightage=30.0,
            assessment_type="EXAM"
        )

    def test_valid_grade_creation(self):
        """Test creating a grade with valid marks"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=85
        )
        self.assertEqual(grade.marks_obtained, 85)
        self.assertEqual(grade.percentage, 85.0)

    def test_grade_exceeds_max_marks_raises_error(self):
        """Test that marks_obtained > max_marks raises ValidationError"""
        grade = Grade(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=105  # Exceeds max_marks of 100
        )
        with self.assertRaises(ValidationError) as context:
            grade.save()
        
        self.assertIn('marks_obtained', context.exception.message_dict)

    def test_grade_at_max_marks_is_valid(self):
        """Test that marks_obtained == max_marks is valid"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=100
        )
        self.assertEqual(grade.marks_obtained, 100)
        self.assertEqual(grade.percentage, 100.0)

    def test_grade_zero_marks_is_valid(self):
        """Test that zero marks is valid"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=0
        )
        self.assertEqual(grade.marks_obtained, 0)
        self.assertEqual(grade.percentage, 0.0)

    def test_grade_percentage_calculation(self):
        """Test percentage property calculation"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=75
        )
        self.assertEqual(grade.percentage, 75.0)

    def test_grade_weighted_marks_calculation(self):
        """Test weighted_marks property calculation"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=80  # 80% of 100
        )
        # 80% * 30% weightage = 24
        self.assertEqual(grade.weighted_marks, 24.0)

    def test_grade_letter_grade_a(self):
        """Test letter grade A (90-100)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=95
        )
        self.assertEqual(grade.get_letter_grade(), 'A')

    def test_grade_letter_grade_b(self):
        """Test letter grade B (80-89)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=85
        )
        self.assertEqual(grade.get_letter_grade(), 'B')

    def test_grade_letter_grade_c(self):
        """Test letter grade C (70-79)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=75
        )
        self.assertEqual(grade.get_letter_grade(), 'C')

    def test_grade_letter_grade_d(self):
        """Test letter grade D (60-69)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=65
        )
        self.assertEqual(grade.get_letter_grade(), 'D')

    def test_grade_letter_grade_f(self):
        """Test letter grade F (<60)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=45
        )
        self.assertEqual(grade.get_letter_grade(), 'F')

    def test_unique_constraint_student_assessment(self):
        """Test that a student can only have one grade per assessment"""
        Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=80
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            Grade.objects.create(
                student=self.student_profile,
                assessment=self.assessment,
                marks_obtained=90
            )

    def test_assessment_str_representation(self):
        """Test Assessment string representation"""
        self.assertEqual(
            str(self.assessment),
            "CS201 - Midterm Exam (100 marks)"
        )

    def test_grade_str_representation(self):
        """Test Grade string representation"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assessment=self.assessment,
            marks_obtained=85
        )
        expected = "2026CS001 - Midterm Exam: 85/100"
        self.assertEqual(str(grade), expected)
