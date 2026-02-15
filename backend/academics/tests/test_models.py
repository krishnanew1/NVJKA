"""
Test suite for academics models.

This module tests the Department, Course, Subject, and Timetable models
to ensure proper functionality and relationships.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from academics.models import Department, Course, Subject, Timetable
from datetime import time


class AcademicsModelsTestCase(TestCase):
    """Test case for academics models."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test department
        self.department = Department.objects.create(
            name="Computer Science and Engineering",
            code="CSE",
            description="Department of Computer Science and Engineering"
        )
        
        # Create a test course
        self.course = Course.objects.create(
            name="Bachelor of Technology in Computer Science",
            code="B.Tech CSE",
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        # Create a test subject
        self.subject = Subject.objects.create(
            name="Data Structures and Algorithms",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4,
            is_mandatory=True
        )
    
    def test_department_creation(self):
        """Test Department model creation and string representation."""
        self.assertEqual(self.department.name, "Computer Science and Engineering")
        self.assertEqual(self.department.code, "CSE")
        self.assertEqual(str(self.department), "CSE - Computer Science and Engineering")
    
    def test_department_unique_constraints(self):
        """Test Department unique constraints."""
        from django.db import transaction
        
        # Test unique name constraint
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Department.objects.create(
                    name="Computer Science and Engineering",  # Same name as setUp
                    code="CSE2"
                )
        
        # Test unique code constraint  
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Department.objects.create(
                    name="Computer Science Engineering",
                    code="CSE"  # Same code as setUp
                )
    
    def test_course_creation(self):
        """Test Course model creation and string representation."""
        self.assertEqual(self.course.name, "Bachelor of Technology in Computer Science")
        self.assertEqual(self.course.code, "B.Tech CSE")
        self.assertEqual(self.course.department, self.department)
        self.assertEqual(self.course.credits, 160)
        self.assertEqual(str(self.course), "B.Tech CSE - Bachelor of Technology in Computer Science")
    
    def test_course_foreign_key_relationship(self):
        """Test Course-Department foreign key relationship."""
        # Test forward relationship
        self.assertEqual(self.course.department, self.department)
        
        # Test reverse relationship
        self.assertIn(self.course, self.department.courses.all())
    
    def test_course_cascade_delete(self):
        """Test that deleting department cascades to courses."""
        course_id = self.course.id
        self.department.delete()
        
        # Course should be deleted when department is deleted
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(id=course_id)
    
    def test_subject_creation(self):
        """Test Subject model creation and string representation."""
        self.assertEqual(self.subject.name, "Data Structures and Algorithms")
        self.assertEqual(self.subject.code, "CS201")
        self.assertEqual(self.subject.course, self.course)
        self.assertEqual(self.subject.semester, 3)
        self.assertEqual(str(self.subject), "CS201 - Data Structures and Algorithms (Sem 3)")
    
    def test_subject_foreign_key_relationship(self):
        """Test Subject-Course foreign key relationship."""
        # Test forward relationship
        self.assertEqual(self.subject.course, self.course)
        
        # Test reverse relationship
        self.assertIn(self.subject, self.course.subjects.all())
    
    def test_subject_unique_together_constraint(self):
        """Test Subject unique_together constraint for code and course."""
        from django.db import transaction
        
        # Should not be able to create another subject with same code in same course
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Subject.objects.create(
                    name="Another Subject",
                    code="CS201",  # Same code
                    course=self.course,  # Same course
                    semester=4
                )
    
    def test_timetable_creation(self):
        """Test Timetable model creation and string representation."""
        timetable = Timetable.objects.create(
            class_name="CSE-A",
            subject=self.subject,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room_number="CS-101",
            academic_year="2024-25"
        )
        
        self.assertEqual(timetable.class_name, "CSE-A")
        self.assertEqual(timetable.subject, self.subject)
        self.assertEqual(timetable.day_of_week, "MONDAY")
        self.assertEqual(str(timetable), "CSE-A - CS201 (MONDAY 09:00:00-10:30:00)")
    
    def test_timetable_foreign_key_relationship(self):
        """Test Timetable-Subject foreign key relationship."""
        timetable = Timetable.objects.create(
            class_name="CSE-A",
            subject=self.subject,
            day_of_week="TUESDAY",
            start_time=time(11, 0),
            end_time=time(12, 30),
            academic_year="2024-25"
        )
        
        # Test forward relationship
        self.assertEqual(timetable.subject, self.subject)
        
        # Test reverse relationship
        self.assertIn(timetable, self.subject.timetable_entries.all())
    
    def test_timetable_time_validation(self):
        """Test Timetable time validation."""
        timetable = Timetable(
            class_name="CSE-A",
            subject=self.subject,
            day_of_week="WEDNESDAY",
            start_time=time(12, 0),
            end_time=time(11, 0),  # End time before start time
            academic_year="2024-25"
        )
        
        # Should raise ValidationError when clean() is called
        with self.assertRaises(ValidationError):
            timetable.clean()
    
    def test_timetable_unique_constraints(self):
        """Test Timetable unique constraints."""
        from django.db import transaction
        
        # Create first timetable entry
        Timetable.objects.create(
            class_name="CSE-A",
            subject=self.subject,
            day_of_week="THURSDAY",
            start_time=time(14, 0),
            end_time=time(15, 30),
            academic_year="2024-25"
        )
        
        # Try to create conflicting entry (same class, day, time, year)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Timetable.objects.create(
                    class_name="CSE-A",  # Same class
                    subject=self.subject,
                    day_of_week="THURSDAY",  # Same day
                    start_time=time(14, 0),  # Same start time
                    end_time=time(16, 0),
                    academic_year="2024-25"  # Same academic year
                )
    
    def test_model_ordering(self):
        """Test model ordering."""
        # Create additional test data
        dept2 = Department.objects.create(name="Electronics", code="ECE")
        course2 = Course.objects.create(
            name="B.Tech ECE", code="B.Tech ECE", 
            department=dept2, credits=160
        )
        
        # Test department ordering
        departments = list(Department.objects.all())
        self.assertEqual(departments[0].code, "CSE")
        self.assertEqual(departments[1].code, "ECE")
        
        # Test course ordering
        courses = list(Course.objects.all())
        self.assertEqual(courses[0].code, "B.Tech CSE")
        self.assertEqual(courses[1].code, "B.Tech ECE")
    
    def test_model_verbose_names(self):
        """Test model verbose names."""
        self.assertEqual(Department._meta.verbose_name, "Department")
        self.assertEqual(Department._meta.verbose_name_plural, "Departments")
        self.assertEqual(Course._meta.verbose_name, "Course")
        self.assertEqual(Course._meta.verbose_name_plural, "Courses")
        self.assertEqual(Subject._meta.verbose_name, "Subject")
        self.assertEqual(Subject._meta.verbose_name_plural, "Subjects")
        self.assertEqual(Timetable._meta.verbose_name, "Timetable Entry")
        self.assertEqual(Timetable._meta.verbose_name_plural, "Timetable Entries")