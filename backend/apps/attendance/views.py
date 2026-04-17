from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Count, Q
from datetime import datetime

from .models import Attendance
from apps.users.models import StudentProfile
from apps.academics.models import Subject
from apps.faculty.models import ClassAssignment


VALID_STATUSES = ('Present', 'Absent', 'Late')


class IsFacultyOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ('FACULTY', 'ADMIN')


class BulkAttendanceView(APIView):
    """
    POST /api/attendance/bulk-mark/

    Payload:
    {
        "subject_id": 1,
        "date": "2026-03-15",
        "records": [
            {"student_id": 1, "status": "Present"},
            {"student_id": 2, "status": "Absent"},
            {"student_id": 3, "status": "Late"}
        ]
    }

    - Faculty: must be assigned to the subject via ClassAssignment
    - Admin: bypasses assignment check
    - Entire batch rolls back if any record fails
    """
    permission_classes = [IsFacultyOrAdmin]

    def post(self, request):
        data = request.data
        subject_id = data.get('subject_id')
        date_str = data.get('date')
        records = data.get('records')

        # --- Basic field validation ---
        if not subject_id:
            return Response({'error': 'subject_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not date_str:
            return Response({'error': 'date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not records or not isinstance(records, list):
            return Response({'error': 'records must be a non-empty list.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Parse date ---
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Get subject ---
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': f'Subject with id {subject_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # --- Authorization: faculty must be assigned to this subject ---
        if request.user.role == 'FACULTY':
            try:
                faculty_profile = request.user.faculty_profile
            except Exception:
                return Response({'error': 'Faculty profile not found for this user.'}, status=status.HTTP_403_FORBIDDEN)

            if not ClassAssignment.objects.filter(faculty=faculty_profile, subject=subject).exists():
                return Response(
                    {'error': 'You are not assigned to this subject and cannot mark its attendance.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # --- Validate each record ---
        errors = []
        for i, rec in enumerate(records):
            if 'student_id' not in rec:
                errors.append({'index': i, 'error': 'student_id is required.'})
            if 'status' not in rec:
                errors.append({'index': i, 'error': 'status is required.'})
            elif rec['status'] not in VALID_STATUSES:
                errors.append({'index': i, 'error': f"status must be one of: {', '.join(VALID_STATUSES)}."})

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        student_ids = [rec['student_id'] for rec in records]

        # --- Verify all students exist ---
        students_qs = StudentProfile.objects.filter(id__in=student_ids)
        found_ids = set(students_qs.values_list('id', flat=True))
        missing = set(student_ids) - found_ids
        if missing:
            return Response({'error': f'Student IDs not found: {sorted(missing)}'}, status=status.HTTP_404_NOT_FOUND)

        students_map = {s.id: s for s in students_qs}

        # --- Atomic bulk create ---
        results = []
        try:
            with transaction.atomic():
                for rec in records:
                    student = students_map[rec['student_id']]
                    attendance = Attendance(
                        student=student,
                        subject=subject,
                        date=attendance_date,
                        status=rec['status'],
                        recorded_by=request.user,
                    )
                    try:
                        attendance.clean()  # validates date not in future
                    except ValidationError as e:
                        raise e

                    attendance.save()
                    results.append({'student_id': student.id, 'status': rec['status'], 'result': 'created'})

        except ValidationError as e:
            return Response({'error': 'Validation failed.', 'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response(
                {'error': 'Duplicate attendance record detected. Entire batch rolled back.', 'detail': str(e)},
                status=status.HTTP_409_CONFLICT
            )

        return Response({
            'message': f'Attendance marked for {len(results)} students.',
            'subject': {'id': subject.id, 'code': subject.code, 'name': subject.name},
            'date': attendance_date.isoformat(),
            'recorded_by': request.user.username,
            'count': len(results),
            'records': results,
        }, status=status.HTTP_201_CREATED)



class StudentAttendanceView(APIView):
    """
    GET /api/attendance/my-records/
    
    Returns attendance statistics for the logged-in student.
    Groups attendance by subject and calculates percentages.
    Optionally returns detailed records if ?details=true is passed.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get attendance records for the current student."""
        # Check if user is a student
        if request.user.role != 'STUDENT':
            return Response(
                {'error': 'This endpoint is only accessible to students.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student profile
        try:
            student_profile = request.user.student_profile
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'No student profile found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if detailed records are requested
        include_details = request.query_params.get('details', 'false').lower() == 'true'
        
        # Get all attendance records for this student
        attendance_records = Attendance.objects.filter(
            student=student_profile
        ).select_related('subject', 'subject__course').order_by('-date')
        
        # Group by subject and calculate statistics
        subjects_stats = {}
        detailed_records = {}
        
        for record in attendance_records:
            subject_id = record.subject.id
            
            if subject_id not in subjects_stats:
                subjects_stats[subject_id] = {
                    'subject': {
                        'id': record.subject.id,
                        'name': record.subject.name,
                        'code': record.subject.code,
                        'semester': record.subject.semester,
                        'credits': record.subject.credits,
                    },
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                }
                if include_details:
                    detailed_records[subject_id] = []
            
            subjects_stats[subject_id]['total'] += 1
            
            if record.status == 'Present':
                subjects_stats[subject_id]['present'] += 1
            elif record.status == 'Absent':
                subjects_stats[subject_id]['absent'] += 1
            elif record.status == 'Late':
                subjects_stats[subject_id]['late'] += 1
            
            # Add detailed record if requested
            if include_details:
                detailed_records[subject_id].append({
                    'date': record.date.isoformat(),
                    'status': record.status,
                    'recorded_by': record.recorded_by.get_full_name() or record.recorded_by.username
                })
        
        # Calculate percentages
        attendance_summary = []
        for subject_id, stats in subjects_stats.items():
            total = stats['total']
            present = stats['present']
            late = stats['late']
            
            # Count late as present for percentage calculation
            effective_present = present + late
            percentage = (effective_present / total * 100) if total > 0 else 0
            
            summary_item = {
                'subject': stats['subject'],
                'total_classes': total,
                'present': present,
                'absent': stats['absent'],
                'late': late,
                'percentage': round(percentage, 2)
            }
            
            if include_details:
                summary_item['records'] = detailed_records[subject_id]
            
            attendance_summary.append(summary_item)
        
        # Sort by subject code
        attendance_summary.sort(key=lambda x: x['subject']['code'])
        
        return Response({
            'student': {
                'id': student_profile.id,
                'enrollment_number': student_profile.enrollment_number,
                'name': request.user.get_full_name() or request.user.username,
            },
            'attendance': attendance_summary,
            'total_subjects': len(attendance_summary)
        }, status=status.HTTP_200_OK)



class AttendanceRecordsView(APIView):
    """
    GET /api/attendance/records/
    
    Fetch attendance records for a specific subject and date.
    Query params: subject_id, date
    
    PATCH /api/attendance/records/
    
    Update attendance records for a specific subject and date.
    Payload: {
        "subject_id": 1,
        "date": "2026-03-15",
        "records": [
            {"student_id": 1, "status": "Present"},
            {"student_id": 2, "status": "Absent"}
        ]
    }
    """
    permission_classes = [IsFacultyOrAdmin]
    
    def get(self, request):
        """Fetch attendance records for a specific subject and date."""
        subject_id = request.query_params.get('subject_id')
        date_str = request.query_params.get('date')
        
        # Validate parameters
        if not subject_id:
            return Response({'error': 'subject_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not date_str:
            return Response({'error': 'date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse date
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': f'Subject with id {subject_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Authorization: faculty must be assigned to this subject
        if request.user.role == 'FACULTY':
            try:
                faculty_profile = request.user.faculty_profile
            except Exception:
                return Response({'error': 'Faculty profile not found for this user.'}, status=status.HTTP_403_FORBIDDEN)
            
            if not ClassAssignment.objects.filter(faculty=faculty_profile, subject=subject).exists():
                return Response(
                    {'error': 'You are not assigned to this subject.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get all students enrolled in this subject's course and semester
        from apps.students.models import Enrollment
        enrollments = Enrollment.objects.filter(
            course=subject.course,
            semester=subject.semester,
            status='Active'
        ).select_related('student', 'student__user')
        
        # Get existing attendance records for this date
        attendance_records = Attendance.objects.filter(
            subject=subject,
            date=attendance_date
        ).select_related('student', 'student__user')
        
        # Create a map of student_id to attendance status
        attendance_map = {record.student.id: record.status for record in attendance_records}
        
        # Build response with all enrolled students
        students_data = []
        for enrollment in enrollments:
            student = enrollment.student
            students_data.append({
                'student_id': student.id,
                'name': student.user.get_full_name() or student.user.username,
                'roll_number': student.enrollment_number,
                'status': attendance_map.get(student.id, None)  # None if not marked
            })
        
        return Response({
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code
            },
            'date': attendance_date.isoformat(),
            'students': students_data,
            'has_records': len(attendance_records) > 0
        }, status=status.HTTP_200_OK)
    
    def patch(self, request):
        """Update attendance records for a specific subject and date."""
        data = request.data
        subject_id = data.get('subject_id')
        date_str = data.get('date')
        records = data.get('records')
        
        # Basic field validation
        if not subject_id:
            return Response({'error': 'subject_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not date_str:
            return Response({'error': 'date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not records or not isinstance(records, list):
            return Response({'error': 'records must be a non-empty list.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse date
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': f'Subject with id {subject_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Authorization: faculty must be assigned to this subject
        if request.user.role == 'FACULTY':
            try:
                faculty_profile = request.user.faculty_profile
            except Exception:
                return Response({'error': 'Faculty profile not found for this user.'}, status=status.HTTP_403_FORBIDDEN)
            
            if not ClassAssignment.objects.filter(faculty=faculty_profile, subject=subject).exists():
                return Response(
                    {'error': 'You are not assigned to this subject and cannot update its attendance.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validate each record
        errors = []
        for i, rec in enumerate(records):
            if 'student_id' not in rec:
                errors.append({'index': i, 'error': 'student_id is required.'})
            if 'status' not in rec:
                errors.append({'index': i, 'error': 'status is required.'})
            elif rec['status'] not in VALID_STATUSES:
                errors.append({'index': i, 'error': f"status must be one of: {', '.join(VALID_STATUSES)}."})
        
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        student_ids = [rec['student_id'] for rec in records]
        
        # Verify all students exist
        students_qs = StudentProfile.objects.filter(id__in=student_ids)
        found_ids = set(students_qs.values_list('id', flat=True))
        missing = set(student_ids) - found_ids
        if missing:
            return Response({'error': f'Student IDs not found: {sorted(missing)}'}, status=status.HTTP_404_NOT_FOUND)
        
        students_map = {s.id: s for s in students_qs}
        
        # Update or create attendance records
        results = []
        try:
            with transaction.atomic():
                for rec in records:
                    student = students_map[rec['student_id']]
                    
                    # Try to get existing record
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=attendance_date,
                        defaults={
                            'status': rec['status'],
                            'recorded_by': request.user,
                        }
                    )
                    
                    results.append({
                        'student_id': student.id,
                        'status': rec['status'],
                        'result': 'created' if created else 'updated'
                    })
        
        except ValidationError as e:
            return Response({'error': 'Validation failed.', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Update failed.', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Attendance updated for {len(results)} students.',
            'subject': {'id': subject.id, 'code': subject.code, 'name': subject.name},
            'date': attendance_date.isoformat(),
            'updated_by': request.user.username,
            'count': len(results),
            'records': results,
        }, status=status.HTTP_200_OK)


class FacultyAttendanceSummaryView(APIView):
    """
    GET /api/faculty/attendance-summary/
    
    Returns attendance summary for all students in subjects assigned to the logged-in faculty.
    Calculates attendance percentage for each student per subject.
    Groups students by batch (extracted from reg_no).
    
    Query params:
    - subject_id (optional): Filter by specific subject
    - batch (optional): Filter by specific batch string (e.g., '2024')
    
    Response:
    {
        "faculty": {...},
        "subjects": [
            {
                "subject": {...},
                "batches": {
                    "2024": {
                        "batch_string": "2024",
                        "students": [
                            {
                                "student_id": 1,
                                "reg_no": "2024001",
                                "name": "John Doe",
                                "total_classes": 20,
                                "attended": 18,
                                "attendance_percentage": 90.0
                            },
                            ...
                        ],
                        "batch_average": 85.5
                    }
                }
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get attendance summary for faculty's assigned subjects."""
        # Check if user is faculty
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'This endpoint is only accessible to faculty members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get faculty profile
        try:
            faculty_profile = request.user.faculty_profile
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Faculty profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get query parameters
        subject_id_filter = request.query_params.get('subject_id')
        batch_filter = request.query_params.get('batch')
        
        # Get subjects assigned to this faculty
        subjects_query = Subject.objects.filter(faculty=faculty_profile).select_related('course')
        
        if subject_id_filter:
            subjects_query = subjects_query.filter(id=subject_id_filter)
        
        subjects = list(subjects_query)
        
        if not subjects:
            return Response({
                'faculty': {
                    'id': faculty_profile.id,
                    'name': request.user.get_full_name() or request.user.username,
                    'employee_id': faculty_profile.employee_id
                },
                'subjects': [],
                'message': 'No subjects assigned to this faculty member.'
            }, status=status.HTTP_200_OK)
        
        # Build response data
        subjects_data = []
        
        for subject in subjects:
            # Get all students enrolled in this subject's course and semester
            from apps.students.models import Enrollment
            enrollments = Enrollment.objects.filter(
                course=subject.course,
                semester=subject.semester,
                status='Active'
            ).select_related('student', 'student__user')
            
            # Group students by batch (extract year from reg_no)
            batches_data = {}
            
            for enrollment in enrollments:
                student = enrollment.student
                reg_no = student.enrollment_number or ''
                
                # Extract batch year from reg_no (first 4 digits)
                batch_year = reg_no[:4] if len(reg_no) >= 4 and reg_no[:4].isdigit() else 'Unknown'
                
                # Apply batch filter if specified
                if batch_filter and batch_year != batch_filter:
                    continue
                
                # Get attendance records for this student and subject
                attendance_records = Attendance.objects.filter(
                    student=student,
                    subject=subject
                )
                
                total_classes = attendance_records.count()
                attended = attendance_records.filter(
                    Q(status='Present') | Q(status='Late')
                ).count()
                
                attendance_percentage = (attended / total_classes * 100) if total_classes > 0 else 0
                
                # Initialize batch if not exists
                if batch_year not in batches_data:
                    batches_data[batch_year] = {
                        'batch_string': batch_year,
                        'students': [],
                        'total_percentage': 0,
                        'student_count': 0
                    }
                
                # Add student data
                student_data = {
                    'student_id': student.id,
                    'reg_no': reg_no,
                    'name': student.user.get_full_name() or student.user.username,
                    'total_classes': total_classes,
                    'attended': attended,
                    'attendance_percentage': round(attendance_percentage, 2)
                }
                
                batches_data[batch_year]['students'].append(student_data)
                batches_data[batch_year]['total_percentage'] += attendance_percentage
                batches_data[batch_year]['student_count'] += 1
            
            # Calculate batch averages
            for batch_year, batch_info in batches_data.items():
                if batch_info['student_count'] > 0:
                    batch_info['batch_average'] = round(
                        batch_info['total_percentage'] / batch_info['student_count'], 2
                    )
                else:
                    batch_info['batch_average'] = 0
                
                # Remove temporary fields
                del batch_info['total_percentage']
                del batch_info['student_count']
            
            subjects_data.append({
                'subject': {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'semester': subject.semester,
                    'course': {
                        'id': subject.course.id,
                        'name': subject.course.name,
                        'code': subject.course.code
                    }
                },
                'batches': batches_data
            })
        
        return Response({
            'faculty': {
                'id': faculty_profile.id,
                'name': request.user.get_full_name() or request.user.username,
                'employee_id': faculty_profile.employee_id
            },
            'subjects': subjects_data
        }, status=status.HTTP_200_OK)


class SubmitAttendanceReportView(APIView):
    """
    POST /api/faculty/submit-attendance-report/
    
    Submit an attendance report for a specific subject and batch.
    Creates an AttendanceReportSubmission record for admin review.
    
    Payload:
    {
        "subject_id": 1,
        "batch_string": "2024-IMG"
    }
    
    Response:
    {
        "success": true,
        "message": "Attendance report submitted successfully.",
        "submission": {
            "id": 1,
            "subject": {...},
            "batch_string": "2024-IMG",
            "submitted_at": "2026-04-18T10:30:00Z",
            "is_reviewed": false
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Submit an attendance report."""
        # Check if user is faculty
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'This endpoint is only accessible to faculty members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get faculty profile
        try:
            faculty_profile = request.user.faculty_profile
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Faculty profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get request data
        subject_id = request.data.get('subject_id')
        batch_string = request.data.get('batch_string')
        
        # Validate required fields
        if not subject_id:
            return Response(
                {'error': 'subject_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not batch_string:
            return Response(
                {'error': 'batch_string is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get subject
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response(
                {'error': f'Subject with id {subject_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify faculty is assigned to this subject
        if subject.faculty != faculty_profile:
            return Response(
                {'error': 'You are not assigned to this subject.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create submission record
        from .models import AttendanceReportSubmission
        
        try:
            submission = AttendanceReportSubmission.objects.create(
                faculty=faculty_profile,
                subject=subject,
                batch_string=batch_string
            )
            
            return Response({
                'success': True,
                'message': 'Attendance report submitted successfully.',
                'submission': {
                    'id': submission.id,
                    'subject': {
                        'id': subject.id,
                        'name': subject.name,
                        'code': subject.code
                    },
                    'batch_string': submission.batch_string,
                    'submitted_at': submission.submitted_at.isoformat(),
                    'is_reviewed': submission.is_reviewed_by_admin
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to submit attendance report.', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
