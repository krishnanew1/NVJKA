"""
Views for attendance management.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import datetime

from .models import Attendance
from users.models import StudentProfile, FacultyProfile
from academics.models import Subject


class IsFacultyOrAdmin(IsAuthenticated):
    """
    Custom permission to only allow faculty or admin users to access the view.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        # Then check if user has FACULTY or ADMIN role
        return request.user.role in ['FACULTY', 'ADMIN']


class BulkAttendanceView(APIView):
    """
    API endpoint for bulk attendance marking.
    
    POST: Mark attendance for multiple students at once
    
    Permissions: IsAuthenticated AND User role is FACULTY or ADMIN
    
    Request Body:
    {
        "student_ids": [1, 2, 3, 4],
        "subject_id": 5,
        "date": "2026-02-11",
        "status": "PRESENT"  // or "ABSENT" or "LATE"
    }
    """
    permission_classes = [IsFacultyOrAdmin]
    
    def post(self, request):
        """
        Mark attendance for multiple students in a single transaction.
        
        Validates:
        - All required fields present
        - Subject exists
        - All students exist
        - Date is valid
        - Status is valid
        - No duplicate attendance for same student-subject-date
        
        Creates attendance records in a single database transaction.
        """
        # Extract data from request
        student_ids = request.data.get('student_ids', [])
        subject_id = request.data.get('subject_id')
        date_str = request.data.get('date')
        attendance_status = request.data.get('status', 'PRESENT')
        
        # Validate required fields
        if not student_ids:
            return Response(
                {
                    'error': 'Missing required field',
                    'detail': 'student_ids is required and must be a non-empty list'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(student_ids, list):
            return Response(
                {
                    'error': 'Invalid data type',
                    'detail': 'student_ids must be a list'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not subject_id:
            return Response(
                {
                    'error': 'Missing required field',
                    'detail': 'subject_id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not date_str:
            return Response(
                {
                    'error': 'Missing required field',
                    'detail': 'date is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status
        valid_statuses = ['PRESENT', 'ABSENT', 'LATE']
        if attendance_status not in valid_statuses:
            return Response(
                {
                    'error': 'Invalid status',
                    'detail': f'status must be one of: {", ".join(valid_statuses)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    'error': 'Invalid date format',
                    'detail': 'date must be in YYYY-MM-DD format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response(
                {
                    'error': 'Subject not found',
                    'detail': f'No subject found with id {subject_id}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get faculty profile if user is faculty
        marked_by = None
        if request.user.role == 'FACULTY':
            try:
                marked_by = request.user.faculty_profile
            except FacultyProfile.DoesNotExist:
                pass
        
        # Get all students
        students = StudentProfile.objects.filter(id__in=student_ids)
        
        if students.count() != len(student_ids):
            found_ids = set(students.values_list('id', flat=True))
            missing_ids = set(student_ids) - found_ids
            return Response(
                {
                    'error': 'Students not found',
                    'detail': f'No student profiles found for ids: {list(missing_ids)}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check for existing attendance records
        existing_attendance = Attendance.objects.filter(
            student__in=students,
            subject=subject,
            date=attendance_date
        )
        
        if existing_attendance.exists():
            existing_student_ids = list(
                existing_attendance.values_list('student__id', flat=True)
            )
            existing_enrollments = list(
                existing_attendance.values_list('student__enrollment_number', flat=True)
            )
            return Response(
                {
                    'error': 'Attendance already marked',
                    'detail': f'Attendance already exists for students: {", ".join(existing_enrollments)}',
                    'existing_student_ids': existing_student_ids
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create attendance records in a transaction
        try:
            with transaction.atomic():
                attendance_records = []
                for student in students:
                    attendance_records.append(
                        Attendance(
                            student=student,
                            subject=subject,
                            date=attendance_date,
                            status=attendance_status,
                            marked_by=marked_by
                        )
                    )
                
                # Bulk create all records
                created_records = Attendance.objects.bulk_create(attendance_records)
                
                # Prepare response data
                response_data = {
                    'message': f'Successfully marked attendance for {len(created_records)} students',
                    'count': len(created_records),
                    'subject': {
                        'id': subject.id,
                        'code': subject.code,
                        'name': subject.name
                    },
                    'date': attendance_date.isoformat(),
                    'status': attendance_status,
                    'students': [
                        {
                            'id': student.id,
                            'enrollment_number': student.enrollment_number,
                            'name': student.user.get_full_name() or student.user.username
                        }
                        for student in students
                    ]
                }
                
                if marked_by:
                    response_data['marked_by'] = {
                        'id': marked_by.id,
                        'employee_id': marked_by.employee_id,
                        'name': marked_by.user.get_full_name() or marked_by.user.username
                    }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {
                    'error': 'Database error',
                    'detail': f'Failed to create attendance records: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
