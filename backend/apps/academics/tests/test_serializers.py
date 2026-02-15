"""
Test suite for academics serializers.

This module tests the serializers for Department, Course, Subject, and Timetable
models including nested serialization functionality.
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from academics.models import Department, Course, Subject, Timetable
from academics.serializers import (
    DepartmentSerializer, DepartmentDetailSerializer,
    CourseSerializer, CourseDetailSerializer,
    SubjectSerializer, TimetableSerializer
)
from datetime import time


class AcademicsSerializersTestCase(TestCase):
    """Test case for academics serializers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        
        # Create test data
        self.department = Department.objects.create(
            name="Computer Science and Engineering",
            code="CSE",
            description="Department of Computer Science and Engineering"
        )
        
        self.course = Course.objects.create(
            name="Bachelor of Technology in Computer Science",
            code="B.Tech CSE",
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        self.subject = Subject.objects.create(
            name="Data Structures and Algorithms",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4,
            is_mandatory=True
        )
        
        self.timetable = Timetable.objects.create(
            class_name="CSE-A",
            subject=self.subject,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room_number="CS-101",
            academic_year="2024-25"
        )
    
    def test_department_serializer(self):
        """Test DepartmentSerializer functionality."""
        serializer = DepartmentSerializer(self.department)
        data = serializer.data
        
        # Test basic fields
        self.assertEqual(data['name'], "Computer Science and Engineering")
        self.assertEqual(data['code'], "CSE")
        self.assertEqual(data['description'], "Department of Computer Science and Engineering")
        
        # Test computed field
        self.assertEqual(data['total_courses'], 1)
        
        # Test read-only fields are present
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_department_detail_serializer(self):
        """Test DepartmentDetailSerializer with nested courses."""
        serializer = DepartmentDetailSerializer(self.department)
        data = serializer.data
        
        # Test that courses are included
        self.assertIn('courses', data)
        self.assertEqual(len(data['courses']), 1)
        
        # Test course data structure
        course_data = data['courses'][0]
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        self.assertEqual(course_data['code'], "B.Tech CSE")
        self.assertEqual(course_data['credits'], 160)
    
    def test_course_serializer_with_nested_department(self):
        """Test CourseSerializer with nested Department information."""
        serializer = CourseSerializer(self.course)
        data = serializer.data
        
        # Test basic course fields
        self.assertEqual(data['name'], "Bachelor of Technology in Computer Science")
        self.assertEqual(data['code'], "B.Tech CSE")
        self.assertEqual(data['credits'], 160)
        
        # Test nested department data
        self.assertIn('department', data)
        dept_data = data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
        self.assertEqual(dept_data['code'], "CSE")
        self.assertEqual(dept_data['total_courses'], 1)
        
        # Test computed field
        self.assertEqual(data['total_subjects'], 1)
    
    def test_course_serializer_create(self):
        """Test creating a course using CourseSerializer."""
        # Create another department for testing
        dept2 = Department.objects.create(name="Electronics", code="ECE")
        
        data = {
            'name': 'Bachelor of Technology in Electronics',
            'code': 'B.Tech ECE',
            'department_id': dept2.id,
            'credits': 160,
            'duration_years': 4,
            'description': 'Electronics course'
        }
        
        serializer = CourseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        course = serializer.save()
        self.assertEqual(course.name, 'Bachelor of Technology in Electronics')
        self.assertEqual(course.department, dept2)
    
    def test_course_serializer_validation(self):
        """Test CourseSerializer validation."""
        data = {
            'name': 'Test Course',
            'code': 'TEST',
            'department_id': 99999,  # Non-existent department
            'credits': 160
        }
        
        serializer = CourseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('department_id', serializer.errors)
    
    def test_course_detail_serializer(self):
        """Test CourseDetailSerializer with nested subjects."""
        serializer = CourseDetailSerializer(self.course)
        data = serializer.data
        
        # Test that subjects are included
        self.assertIn('subjects', data)
        self.assertEqual(len(data['subjects']), 1)
        
        # Test subject data structure
        subject_data = data['subjects'][0]
        self.assertEqual(subject_data['name'], "Data Structures and Algorithms")
        self.assertEqual(subject_data['code'], "CS201")
        self.assertEqual(subject_data['semester'], 3)
    
    def test_subject_serializer_with_nested_course(self):
        """Test SubjectSerializer with nested Course and Department information."""
        serializer = SubjectSerializer(self.subject)
        data = serializer.data
        
        # Test basic subject fields
        self.assertEqual(data['name'], "Data Structures and Algorithms")
        self.assertEqual(data['code'], "CS201")
        self.assertEqual(data['semester'], 3)
        self.assertEqual(data['semester_display'], "Semester 3")
        
        # Test nested course data (which includes department)
        self.assertIn('course', data)
        course_data = data['course']
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        
        # Test nested department within course
        self.assertIn('department', course_data)
        dept_data = course_data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
        
        # Test computed field
        self.assertEqual(data['total_timetable_entries'], 1)
    
    def test_subject_serializer_create(self):
        """Test creating a subject using SubjectSerializer."""
        data = {
            'name': 'Operating Systems',
            'code': 'CS301',
            'course_id': self.course.id,
            'semester': 5,
            'credits': 3,
            'is_mandatory': True
        }
        
        serializer = SubjectSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        subject = serializer.save()
        self.assertEqual(subject.name, 'Operating Systems')
        self.assertEqual(subject.course, self.course)
    
    def test_subject_serializer_unique_validation(self):
        """Test SubjectSerializer unique constraint validation."""
        data = {
            'name': 'Another Subject',
            'code': 'CS201',  # Same code as existing subject
            'course_id': self.course.id,  # Same course
            'semester': 4
        }
        
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_timetable_serializer_with_nested_subject(self):
        """Test TimetableSerializer with nested Subject information."""
        serializer = TimetableSerializer(self.timetable)
        data = serializer.data
        
        # Test basic timetable fields
        self.assertEqual(data['class_name'], "CSE-A")
        self.assertEqual(data['day_of_week'], "MONDAY")
        self.assertEqual(data['day_display'], "Monday")
        self.assertEqual(data['start_time'], "09:00:00")
        self.assertEqual(data['end_time'], "10:30:00")
        self.assertEqual(data['room_number'], "CS-101")
        
        # Test computed field
        self.assertEqual(data['duration_minutes'], 90)
        
        # Test nested subject data (which includes course and department)
        self.assertIn('subject', data)
        subject_data = data['subject']
        self.assertEqual(subject_data['name'], "Data Structures and Algorithms")
        
        # Test nested course within subject
        self.assertIn('course', subject_data)
        course_data = subject_data['course']
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        
        # Test nested department within course
        self.assertIn('department', course_data)
        dept_data = course_data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
    
    def test_timetable_serializer_create(self):
        """Test creating a timetable entry using TimetableSerializer."""
        data = {
            'class_name': 'CSE-B',
            'subject_id': self.subject.id,
            'day_of_week': 'TUESDAY',
            'start_time': '11:00:00',
            'end_time': '12:30:00',
            'room_number': 'CS-102',
            'academic_year': '2024-25'
        }
        
        serializer = TimetableSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        timetable = serializer.save()
        self.assertEqual(timetable.class_name, 'CSE-B')
        self.assertEqual(timetable.subject, self.subject)
    
    def test_timetable_serializer_time_validation(self):
        """Test TimetableSerializer time validation."""
        data = {
            'class_name': 'CSE-C',
            'subject_id': self.subject.id,
            'day_of_week': 'WEDNESDAY',
            'start_time': '12:00:00',
            'end_time': '11:00:00',  # End time before start time
            'academic_year': '2024-25'
        }
        
        serializer = TimetableSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_time', serializer.errors)
    
    def test_timetable_serializer_unique_validation(self):
        """Test TimetableSerializer unique constraint validation."""
        data = {
            'class_name': 'CSE-A',  # Same class
            'subject_id': self.subject.id,
            'day_of_week': 'MONDAY',  # Same day
            'start_time': '09:00:00',  # Same time
            'end_time': '10:30:00',
            'academic_year': '2024-25'  # Same academic year
        }
        
        serializer = TimetableSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_serializer_read_only_fields(self):
        """Test that read-only fields cannot be modified."""
        # Test Department serializer
        data = {'name': 'New Name', 'id': 999, 'created_at': '2025-01-01T00:00:00Z'}
        serializer = DepartmentSerializer(self.department, data=data, partial=True)
        
        if serializer.is_valid():
            updated_dept = serializer.save()
            self.assertEqual(updated_dept.name, 'New Name')
            self.assertNotEqual(updated_dept.id, 999)  # ID should not change
    
    def test_serializer_field_presence(self):
        """Test that all expected fields are present in serialized data."""
        # Test CourseSerializer
        serializer = CourseSerializer(self.course)
        data = serializer.data
        
        expected_fields = [
            'id', 'name', 'code', 'department', 'credits', 'duration_years',
            'description', 'total_subjects', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data, f"Field '{field}' missing from CourseSerializer")