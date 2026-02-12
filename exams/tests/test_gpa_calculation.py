from django.test import TestCase
from decimal import Decimal
from exams.models import Assessment, Grade
from exams.utils import (
    calculate_gpa,
    get_letter_grade_from_percentage,
    get_grade_point_from_percentage,
    calculate_subject_average,
    get_student_transcript
)
from academics.models import Subject, Course, Department
from users.models import CustomUser, StudentProfile
from students.models import Enrollment


class GPACalculationTestCase(TestCase):
    """Test GPA calculation functionality"""

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

        # Create subjects with different credits
        self.subject1 = Subject.objects.create(
            name="Data Structures",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4
        )
        
        self.subject2 = Subject.objects.create(
            name="Algorithms",
            code="CS202",
            course=self.course,
            semester=3,
            credits=3
        )
        
        self.subject3 = Subject.objects.create(
            name="Database Systems",
            code="CS301",
            course=self.course,
            semester=4,
            credits=4
        )

        # Create student
        self.student_user = CustomUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass123",
            role="STUDENT",
            first_name="John",
            last_name="Doe"
        )

        self.student_profile = self.student_user.student_profile
        self.student_profile.enrollment_number = "2026CS001"
        self.student_profile.batch_year = 2026
        self.student_profile.department = self.department
        self.student_profile.save()

        # Create enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student_profile,
            course=self.course,
            status="ENROLLED"
        )

    def test_gpa_calculation_single_subject(self):
        """Test GPA calculation with grades in one subject"""
        # Create assessment
        assessment = Assessment.objects.create(
            name="Midterm Exam",
            subject=self.subject1,
            max_marks=100,
            weightage=50.0,
            assessment_type="EXAM"
        )
        
        # Create grade: 80% = 8.0 grade point
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment,
            marks_obtained=80
        )
        
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('8.00'))
        self.assertEqual(result['total_credits'], 4)
        self.assertEqual(result['grades_count'], 1)
        self.assertEqual(len(result['subject_grades']), 1)

    def test_gpa_calculation_multiple_subjects(self):
        """Test GPA calculation with grades in multiple subjects"""
        # Subject 1: 90% (4 credits) = 9.0 * 4 = 36
        assessment1 = Assessment.objects.create(
            name="DS Exam",
            subject=self.subject1,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=90
        )
        
        # Subject 2: 80% (3 credits) = 8.0 * 3 = 24
        assessment2 = Assessment.objects.create(
            name="Algo Exam",
            subject=self.subject2,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment2,
            marks_obtained=80
        )
        
        # Expected GPA: (36 + 24) / (4 + 3) = 60 / 7 = 8.57
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('8.57'))
        self.assertEqual(result['total_credits'], 7)
        self.assertEqual(result['grades_count'], 2)
        self.assertEqual(len(result['subject_grades']), 2)

    def test_gpa_calculation_multiple_assessments_per_subject(self):
        """Test GPA calculation with multiple assessments in same subject"""
        # Create two assessments for subject1
        assessment1 = Assessment.objects.create(
            name="Midterm",
            subject=self.subject1,
            max_marks=100,
            weightage=40.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=80  # 80%
        )
        
        assessment2 = Assessment.objects.create(
            name="Final",
            subject=self.subject1,
            max_marks=100,
            weightage=60.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment2,
            marks_obtained=90  # 90%
        )
        
        # Average: (80 + 90) / 2 = 85% = 8.5 grade point
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('8.50'))
        self.assertEqual(result['total_credits'], 4)
        self.assertEqual(result['grades_count'], 2)
        self.assertEqual(len(result['subject_grades']), 1)
        self.assertEqual(result['subject_grades'][0]['assessments_count'], 2)

    def test_gpa_calculation_no_grades(self):
        """Test GPA calculation when student has no grades"""
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('0.0'))
        self.assertEqual(result['total_credits'], 0)
        self.assertEqual(result['grades_count'], 0)
        self.assertEqual(len(result['subject_grades']), 0)

    def test_gpa_calculation_perfect_score(self):
        """Test GPA calculation with 100% scores"""
        assessment = Assessment.objects.create(
            name="Exam",
            subject=self.subject1,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment,
            marks_obtained=100
        )
        
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('10.00'))

    def test_gpa_calculation_failing_grade(self):
        """Test GPA calculation with failing grades"""
        assessment = Assessment.objects.create(
            name="Exam",
            subject=self.subject1,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment,
            marks_obtained=40  # 40% = 4.0 grade point
        )
        
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('4.00'))

    def test_gpa_calculation_weighted_by_credits(self):
        """Test that GPA is properly weighted by subject credits"""
        # High grade in low-credit subject
        assessment1 = Assessment.objects.create(
            name="Algo Exam",
            subject=self.subject2,  # 3 credits
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=100  # 10.0 * 3 = 30
        )
        
        # Low grade in high-credit subject
        assessment2 = Assessment.objects.create(
            name="DS Exam",
            subject=self.subject1,  # 4 credits
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment2,
            marks_obtained=70  # 7.0 * 4 = 28
        )
        
        # Expected: (30 + 28) / (3 + 4) = 58 / 7 = 8.29
        result = calculate_gpa(self.student_profile.id)
        
        self.assertEqual(result['gpa'], Decimal('8.29'))

    def test_gpa_calculation_nonexistent_student(self):
        """Test GPA calculation with invalid student ID"""
        with self.assertRaises(StudentProfile.DoesNotExist):
            calculate_gpa(99999)

    def test_letter_grade_conversion(self):
        """Test percentage to letter grade conversion"""
        self.assertEqual(get_letter_grade_from_percentage(95), 'A')
        self.assertEqual(get_letter_grade_from_percentage(90), 'A')
        self.assertEqual(get_letter_grade_from_percentage(85), 'B')
        self.assertEqual(get_letter_grade_from_percentage(80), 'B')
        self.assertEqual(get_letter_grade_from_percentage(75), 'C')
        self.assertEqual(get_letter_grade_from_percentage(70), 'C')
        self.assertEqual(get_letter_grade_from_percentage(65), 'D')
        self.assertEqual(get_letter_grade_from_percentage(60), 'D')
        self.assertEqual(get_letter_grade_from_percentage(55), 'F')
        self.assertEqual(get_letter_grade_from_percentage(0), 'F')

    def test_grade_point_conversion(self):
        """Test percentage to grade point conversion"""
        self.assertEqual(get_grade_point_from_percentage(100), Decimal('10.0'))
        self.assertEqual(get_grade_point_from_percentage(85), Decimal('8.5'))
        self.assertEqual(get_grade_point_from_percentage(75), Decimal('7.5'))
        self.assertEqual(get_grade_point_from_percentage(0), Decimal('0.0'))

    def test_subject_average_calculation(self):
        """Test average calculation for a specific subject"""
        # Create multiple assessments
        assessment1 = Assessment.objects.create(
            name="Quiz 1",
            subject=self.subject1,
            max_marks=50,
            weightage=20.0,
            assessment_type="QUIZ"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=40  # 80%
        )
        
        assessment2 = Assessment.objects.create(
            name="Midterm",
            subject=self.subject1,
            max_marks=100,
            weightage=40.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment2,
            marks_obtained=90  # 90%
        )
        
        result = calculate_subject_average(
            self.student_profile.id,
            self.subject1.id
        )
        
        # Average: (80 + 90) / 2 = 85%
        self.assertEqual(result['average_percentage'], Decimal('85.00'))
        self.assertEqual(result['average_grade_point'], Decimal('8.50'))
        self.assertEqual(result['letter_grade'], 'B')
        self.assertEqual(result['assessments_count'], 2)

    def test_subject_average_no_grades(self):
        """Test subject average when no grades exist"""
        result = calculate_subject_average(
            self.student_profile.id,
            self.subject1.id
        )
        
        self.assertEqual(result['average_percentage'], Decimal('0.0'))
        self.assertEqual(result['average_grade_point'], Decimal('0.0'))
        self.assertEqual(result['letter_grade'], 'F')
        self.assertEqual(result['assessments_count'], 0)

    def test_student_transcript_generation(self):
        """Test complete transcript generation"""
        # Add grades for multiple subjects
        assessment1 = Assessment.objects.create(
            name="DS Exam",
            subject=self.subject1,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=85
        )
        
        assessment2 = Assessment.objects.create(
            name="Algo Exam",
            subject=self.subject2,
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment2,
            marks_obtained=90
        )
        
        transcript = get_student_transcript(self.student_profile.id)
        
        # Verify student info
        self.assertEqual(transcript['student']['enrollment_number'], "2026CS001")
        self.assertEqual(transcript['student']['name'], "John Doe")
        self.assertEqual(transcript['student']['batch_year'], 2026)
        
        # Verify GPA
        self.assertGreater(transcript['gpa'], 0)
        self.assertEqual(transcript['total_credits'], 7)
        self.assertEqual(transcript['total_assessments'], 2)
        
        # Verify subjects
        self.assertEqual(len(transcript['subjects']), 2)
        
        # Check subject details
        for subject in transcript['subjects']:
            self.assertIn('subject_code', subject)
            self.assertIn('subject_name', subject)
            self.assertIn('credits', subject)
            self.assertIn('average_percentage', subject)
            self.assertIn('grade_point', subject)
            self.assertIn('letter_grade', subject)
            self.assertIn('assessments', subject)

    def test_gpa_subject_grades_sorted(self):
        """Test that subject grades are sorted by subject code"""
        # Create grades in reverse alphabetical order
        assessment3 = Assessment.objects.create(
            name="DB Exam",
            subject=self.subject3,  # CS301
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment3,
            marks_obtained=85
        )
        
        assessment1 = Assessment.objects.create(
            name="DS Exam",
            subject=self.subject1,  # CS201
            max_marks=100,
            weightage=100.0,
            assessment_type="EXAM"
        )
        Grade.objects.create(
            student=self.student_profile,
            assessment=assessment1,
            marks_obtained=90
        )
        
        result = calculate_gpa(self.student_profile.id)
        
        # Verify sorting
        subject_codes = [s['subject_code'] for s in result['subject_grades']]
        self.assertEqual(subject_codes, ['CS201', 'CS301'])
