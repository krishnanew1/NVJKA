"""
Test suite for academics views.

This module tests the ModelViewSets for Department, Course, and Subject
models including authentication, filtering, and API functionality.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from academics.models import Department, Course, Subject, Timetable
from datetime import time


class AcademicsViewsTestCase(TestCase):
    """Test case for academics API views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='ADMIN'
        )
        
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
    
    def authenticate(self):
        """Authenticate the test client."""
        self.client.force_authenticate(user=self.user)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        # Test department list without authentication
        url = reverse('academics:department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test course list without authentication
        url = reverse('academics:course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test subject list without authentication
        url = reverse('academics:subject-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_department_list_authenticated(self):
        """Test authenticated access to department list."""
        self.authenticate()
        
        url = reverse('academics:department-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Computer Science and Engineering")
        self.assertEqual(response.data['results'][0]['code'], "CSE")
    
    def test_department_detail_authenticated(self):
        """Test authenticated access to department detail."""
        self.authenticate()
        
        url = reverse('academics:department-detail', kwargs={'pk': self.department.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Computer Science and Engineering")
        
        # Test that detailed serializer includes courses
        self.assertIn('courses', response.data)
        self.assertEqual(len(response.data['courses']), 1)
    
    def test_department_create_authenticated(self):
        """Test creating a department with authentication."""
        self.authenticate()
        
        url = reverse('academics:department-list')
        data = {
            'name': 'Electronics and Communication Engineering',
            'code': 'ECE',
            'description': 'Department of Electronics and Communication Engineering'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Electronics and Communication Engineering')
        self.assertEqual(response.data['code'], 'ECE')
        
        # Verify department was created in database
        self.assertTrue(Department.objects.filter(code='ECE').exists())
    
    def test_department_filtering_by_name(self):
        """Test filtering departments by name."""
        self.authenticate()
        
        # Create another department
        Department.objects.create(name='Electronics', code='ECE')
        
        url = reverse('academics:department-list')
        response = self.client.get(url, {'name': 'Electronics'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
    
    def test_department_filtering_by_code(self):
        """Test filtering departments by code."""
        self.authenticate()
        
        url = reverse('academics:department-list')
        response = self.client.get(url, {'code': 'CSE'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'CSE')
    
    def test_department_search(self):
        """Test searching departments."""
        self.authenticate()
        
        url = reverse('academics:department-list')
        response = self.client.get(url, {'search': 'Computer'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Computer', response.data['results'][0]['name'])
    
    def test_course_list_with_nested_department(self):
        """Test course list includes nested department information."""
        self.authenticate()
        
        url = reverse('academics:course-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        course_data = response.data['results'][0]
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        
        # Test nested department data
        self.assertIn('department', course_data)
        dept_data = course_data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
        self.assertEqual(dept_data['code'], "CSE")
    
    def test_course_create_with_department_id(self):
        """Test creating a course with department_id."""
        self.authenticate()
        
        url = reverse('academics:course-list')
        data = {
            'name': 'Master of Technology in Computer Science',
            'code': 'M.Tech CSE',
            'department_id': self.department.id,
            'credits': 80,
            'duration_years': 2
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Master of Technology in Computer Science')
        self.assertEqual(response.data['department']['id'], self.department.id)
    
    def test_course_filtering_by_department(self):
        """Test filtering courses by department."""
        self.authenticate()
        
        # Create another department and course
        dept2 = Department.objects.create(name='Electronics', code='ECE')
        Course.objects.create(name='B.Tech ECE', code='BTECE', department=dept2, credits=160)
        
        url = reverse('academics:course-list')
        response = self.client.get(url, {'department': self.department.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['department']['id'], self.department.id)
    
    def test_course_filtering_by_department_name(self):
        """Test filtering courses by department name."""
        self.authenticate()
        
        url = reverse('academics:course-list')
        response = self.client.get(url, {'department__name': 'Computer Science and Engineering'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_subject_list_with_nested_course_and_department(self):
        """Test subject list includes nested course and department information."""
        self.authenticate()
        
        url = reverse('academics:subject-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        subject_data = response.data['results'][0]
        self.assertEqual(subject_data['name'], "Data Structures and Algorithms")
        
        # Test nested course data
        self.assertIn('course', subject_data)
        course_data = subject_data['course']
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        
        # Test nested department within course
        self.assertIn('department', course_data)
        dept_data = course_data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
    
    def test_subject_create_with_course_id(self):
        """Test creating a subject with course_id."""
        self.authenticate()
        
        url = reverse('academics:subject-list')
        data = {
            'name': 'Operating Systems',
            'code': 'CS301',
            'course_id': self.course.id,
            'semester': 5,
            'credits': 3,
            'is_mandatory': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Operating Systems')
        self.assertEqual(response.data['course']['id'], self.course.id)
    
    def test_subject_filtering_by_semester(self):
        """Test filtering subjects by semester."""
        self.authenticate()
        
        # Create another subject in different semester
        Subject.objects.create(
            name='Database Systems', code='CS401', 
            course=self.course, semester=7, credits=3
        )
        
        url = reverse('academics:subject-list')
        response = self.client.get(url, {'semester': 3})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['semester'], 3)
    
    def test_subject_filtering_by_course_department(self):
        """Test filtering subjects by course department."""
        self.authenticate()
        
        url = reverse('academics:subject-list')
        response = self.client.get(url, {'course__department__code': 'CSE'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_timetable_list_with_full_nesting(self):
        """Test timetable list includes full nested information."""
        self.authenticate()
        
        url = reverse('academics:timetable-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        timetable_data = response.data['results'][0]
        self.assertEqual(timetable_data['class_name'], "CSE-A")
        
        # Test full nesting: timetable -> subject -> course -> department
        subject_data = timetable_data['subject']
        self.assertEqual(subject_data['name'], "Data Structures and Algorithms")
        
        course_data = subject_data['course']
        self.assertEqual(course_data['name'], "Bachelor of Technology in Computer Science")
        
        dept_data = course_data['department']
        self.assertEqual(dept_data['name'], "Computer Science and Engineering")
    
    def test_api_ordering(self):
        """Test API ordering functionality."""
        self.authenticate()
        
        # Create additional departments
        Department.objects.create(name='Electronics', code='ECE')
        Department.objects.create(name='Mechanical', code='MECH')
        
        url = reverse('academics:department-list')
        response = self.client.get(url, {'ordering': 'name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [dept['name'] for dept in response.data['results']]
        self.assertEqual(names, sorted(names))
    
    def test_api_pagination(self):
        """Test API pagination."""
        self.authenticate()
        
        url = reverse('academics:department-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
    
    def test_viewset_permissions(self):
        """Test that all viewsets require authentication."""
        viewsets_urls = [
            'academics:department-list',
            'academics:course-list', 
            'academics:subject-list',
            'academics:timetable-list'
        ]
        
        for url_name in viewsets_urls:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_user_can_create_department(self):
        """Test that an Admin user can successfully create a Department via API."""
        # Ensure user has ADMIN role
        self.assertEqual(self.user.role, 'ADMIN')
        self.authenticate()
        
        url = reverse('academics:department-list')
        department_data = {
            'name': 'Mechanical Engineering',
            'code': 'MECH',
            'description': 'Department of Mechanical Engineering focusing on design and manufacturing'
        }
        
        response = self.client.post(url, department_data, format='json')
        
        # Verify successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Mechanical Engineering')
        self.assertEqual(response.data['code'], 'MECH')
        self.assertEqual(response.data['description'], 'Department of Mechanical Engineering focusing on design and manufacturing')
        
        # Verify department exists in database
        created_dept = Department.objects.get(code='MECH')
        self.assertEqual(created_dept.name, 'Mechanical Engineering')
        self.assertEqual(created_dept.description, 'Department of Mechanical Engineering focusing on design and manufacturing')
    
    def test_admin_user_can_create_course(self):
        """Test that an Admin user can successfully create a Course via API."""
        # Ensure user has ADMIN role
        self.assertEqual(self.user.role, 'ADMIN')
        self.authenticate()
        
        url = reverse('academics:course-list')
        course_data = {
            'name': 'Master of Science in Computer Science',
            'code': 'M.Sc CS',
            'department_id': self.department.id,
            'credits': 120,
            'duration_years': 2,
            'description': 'Advanced computer science program focusing on research and specialization'
        }
        
        response = self.client.post(url, course_data, format='json')
        
        # Verify successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Master of Science in Computer Science')
        self.assertEqual(response.data['code'], 'M.Sc CS')
        self.assertEqual(response.data['credits'], 120)
        self.assertEqual(response.data['duration_years'], 2)
        
        # Verify nested department information is included
        self.assertIn('department', response.data)
        self.assertEqual(response.data['department']['id'], self.department.id)
        self.assertEqual(response.data['department']['name'], self.department.name)
        
        # Verify course exists in database
        created_course = Course.objects.get(code='M.Sc CS')
        self.assertEqual(created_course.name, 'Master of Science in Computer Science')
        self.assertEqual(created_course.department, self.department)
    
    def test_unauthenticated_user_cannot_create_department(self):
        """Test that an unauthenticated user gets 401 error when trying to create a Department."""
        # Do not authenticate the client
        url = reverse('academics:department-list')
        department_data = {
            'name': 'Unauthorized Department',
            'code': 'UNAUTH',
            'description': 'This should not be created'
        }
        
        response = self.client.post(url, department_data, format='json')
        
        # Verify 401 Unauthorized response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify department was not created in database
        self.assertFalse(Department.objects.filter(code='UNAUTH').exists())
    
    def test_unauthenticated_user_cannot_create_course(self):
        """Test that an unauthenticated user gets 401 error when trying to create a Course."""
        # Do not authenticate the client
        url = reverse('academics:course-list')
        course_data = {
            'name': 'Unauthorized Course',
            'code': 'UNAUTH',
            'department_id': self.department.id,
            'credits': 100,
            'duration_years': 4
        }
        
        response = self.client.post(url, course_data, format='json')
        
        # Verify 401 Unauthorized response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify course was not created in database
        self.assertFalse(Course.objects.filter(code='UNAUTH').exists())
    
    def test_different_user_roles_can_create_resources(self):
        """Test that users with different roles can create academic resources."""
        # Test with FACULTY role
        faculty_user = CustomUser.objects.create_user(
            username='facultyuser',
            email='faculty@example.com',
            password='facultypass123',
            role='FACULTY'
        )
        
        self.client.force_authenticate(user=faculty_user)
        
        url = reverse('academics:department-list')
        department_data = {
            'name': 'Faculty Created Department',
            'code': 'FCD',
            'description': 'Department created by faculty user'
        }
        
        response = self.client.post(url, department_data, format='json')
        
        # Verify faculty user can also create departments
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Faculty Created Department')
        
        # Test with STUDENT role
        student_user = CustomUser.objects.create_user(
            username='studentuser',
            email='student@example.com',
            password='studentpass123',
            role='STUDENT'
        )
        
        self.client.force_authenticate(user=student_user)
        
        course_data = {
            'name': 'Student Created Course',
            'code': 'SCC',
            'department_id': self.department.id,
            'credits': 80,
            'duration_years': 3
        }
        
        url = reverse('academics:course-list')
        response = self.client.post(url, course_data, format='json')
        
        # Verify student user can also create courses (based on IsAuthenticated permission)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Student Created Course')
    
    def test_authentication_required_for_all_crud_operations(self):
        """Test that authentication is required for all CRUD operations."""
        # Test CREATE operations without authentication
        create_urls_and_data = [
            ('academics:department-list', {'name': 'Test Dept', 'code': 'TD'}),
            ('academics:course-list', {'name': 'Test Course', 'code': 'TC', 'department_id': self.department.id, 'credits': 100}),
            ('academics:subject-list', {'name': 'Test Subject', 'code': 'TS', 'course_id': self.course.id, 'semester': 1}),
        ]
        
        for url_name, data in create_urls_and_data:
            with self.subTest(operation='CREATE', url=url_name):
                url = reverse(url_name)
                response = self.client.post(url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test UPDATE operations without authentication
        update_urls_and_data = [
            ('academics:department-detail', self.department.pk, {'name': 'Updated Dept'}),
            ('academics:course-detail', self.course.pk, {'name': 'Updated Course'}),
            ('academics:subject-detail', self.subject.pk, {'name': 'Updated Subject'}),
        ]
        
        for url_name, pk, data in update_urls_and_data:
            with self.subTest(operation='UPDATE', url=url_name):
                url = reverse(url_name, kwargs={'pk': pk})
                response = self.client.put(url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                
                response = self.client.patch(url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test DELETE operations without authentication
        delete_urls = [
            ('academics:department-detail', self.department.pk),
            ('academics:course-detail', self.course.pk),
            ('academics:subject-detail', self.subject.pk),
        ]
        
        for url_name, pk in delete_urls:
            with self.subTest(operation='DELETE', url=url_name):
                url = reverse(url_name, kwargs={'pk': pk})
                response = self.client.delete(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)