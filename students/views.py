"""
Views for student enrollment and academic management.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from .models import Enrollment
from users.models import StudentProfile
from academics.models import Course


class IsAdmin(IsAuthenticated):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        # Then check if user has ADMIN role
        return request.user.role == 'ADMIN'


class EnrollStudentView(APIView):
    """
    API endpoint for enrolling students in courses.
    
    POST: Enroll a student in a course
    
    Permissions: IsAuthenticated AND User role is ADMIN
    
    Request Body:
    {
        "student_id": 1,
        "course_id": 2
    }
    """
    permission_classes = [IsAdmin]
    
    def post(self, request):
        """
        Enroll a student in a course.
        
        Validates:
        - Student exists
        - Course exists
        - Student is not already enrolled in the course
        
        Creates an Enrollment record with status='ENROLLED'
        """
        # Extract data from request
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id')
        
        # Validate required fields
        if not student_id:
            return Response(
                {
                    'error': 'Missing required field',
                    'detail': 'student_id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not course_id:
            return Response(
                {
                    'error': 'Missing required field',
                    'detail': 'course_id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get student profile
        try:
            student = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    'error': 'Student not found',
                    'detail': f'No student profile found with id {student_id}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {
                    'error': 'Course not found',
                    'detail': f'No course found with id {course_id}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if student is already enrolled
        existing_enrollment = Enrollment.objects.filter(
            student=student,
            course=course
        ).first()
        
        if existing_enrollment:
            return Response(
                {
                    'error': 'Already enrolled',
                    'detail': f'Student {student.enrollment_number} is already enrolled in {course.code}',
                    'enrollment': {
                        'id': existing_enrollment.id,
                        'status': existing_enrollment.status,
                        'date_enrolled': existing_enrollment.date_enrolled
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        try:
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                status='ENROLLED'
            )
            
            return Response(
                {
                    'message': 'Student enrolled successfully',
                    'enrollment': {
                        'id': enrollment.id,
                        'student': {
                            'id': student.id,
                            'enrollment_number': student.enrollment_number,
                            'name': student.user.get_full_name() or student.user.username
                        },
                        'course': {
                            'id': course.id,
                            'code': course.code,
                            'name': course.name,
                            'credits': course.credits
                        },
                        'status': enrollment.status,
                        'date_enrolled': enrollment.date_enrolled
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        except IntegrityError as e:
            # Handle any database integrity errors
            return Response(
                {
                    'error': 'Database error',
                    'detail': 'Failed to create enrollment due to database constraint'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
