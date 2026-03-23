from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
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
