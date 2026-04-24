from rest_framework import viewsets, permissions, serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import StudentProfile
from apps.common.permissions import IsDepartmentHead
from .models import Assessment, Grade
from .utils import get_student_transcript


class IsAdminOrFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'FACULTY')


# ── Minimal inline serializers ────────────────────────────────────────────────

class AssessmentSerializer(drf_serializers.ModelSerializer):
    class Meta:
        from .models import Assessment
        model = Assessment
        fields = ['id', 'name', 'subject', 'assessment_type', 'max_marks', 'weightage', 'date_conducted']


class GradeSerializer(drf_serializers.ModelSerializer):
    class Meta:
        from .models import Grade
        model = Grade
        fields = ['id', 'student', 'assessment', 'marks_obtained', 'remarks']


# ── ViewSets ──────────────────────────────────────────────────────────────────

class AssessmentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for ``Assessment`` records.

    An Assessment defines an evaluation event for a Subject (e.g. Midterm,
    Final, Quiz) including its total marks and weightage toward the final grade.

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head whose department owns the subject.
    """
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.select_related('subject__course__department').all()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)


class GradeViewSet(viewsets.ModelViewSet):
    """
    CRUD API for ``Grade`` records.

    A Grade links a ``StudentProfile`` to an ``Assessment`` and stores the
    marks obtained along with optional remarks.

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
      Students are scoped to their own grades; Admin and Faculty see all.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head whose department owns the subject.
    """
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Grade.objects.select_related(
            'student__department', 'assessment__subject__course__department'
        )
        if user.role == 'STUDENT':
            return qs.filter(student__user=user)
        return qs.all()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)


# ── Transcript view (unchanged) ───────────────────────────────────────────────

class StudentTranscriptView(APIView):
    """
    Retrieve a complete academic transcript for a student.

    ``GET /api/exams/transcript/<student_id>/``

    Returns a JSON object containing:

    - ``student``   — name, enrollment number, department, batch year, semester.
    - ``gpa``       — cumulative GPA on a 10-point scale.
    - ``subjects``  — per-subject breakdown: average percentage, grade point,
                      letter grade, and individual assessment scores.
    - ``total_credits`` / ``total_assessments`` — summary counters.

    **Permissions**

    - Students may only retrieve their own transcript.
    - Faculty and Admin may retrieve any student's transcript.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        if request.user.role == 'STUDENT':
            try:
                if request.user.student_profile.id != student_id:
                    return Response(
                        {'error': 'You can only view your own transcript.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Exception:
                return Response(
                    {'error': 'Student profile not found for this user.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif request.user.role not in ('FACULTY', 'ADMIN'):
            return Response(
                {'error': 'You do not have permission to view transcripts.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            transcript = get_student_transcript(student_id)
            return Response(transcript, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': f'Student with id {student_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate transcript: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# ── StudentGrade Management Views ─────────────────────────────────────────────

class StudentGradeSerializer(drf_serializers.ModelSerializer):
    """Serializer for StudentGrade model."""
    student_name = drf_serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_enrollment = drf_serializers.CharField(source='student.enrollment_number', read_only=True)
    subject_name = drf_serializers.CharField(source='subject.name', read_only=True)
    subject_code = drf_serializers.CharField(source='subject.code', read_only=True)
    faculty_name = drf_serializers.CharField(source='faculty.user.get_full_name', read_only=True)
    percentage = drf_serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        from .models import StudentGrade
        model = StudentGrade
        fields = [
            'id', 'student', 'student_name', 'student_enrollment',
            'subject', 'subject_name', 'subject_code',
            'faculty', 'faculty_name',
            'marks_obtained', 'total_marks', 'grade_letter',
            'percentage', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FacultyGradeManagementView(APIView):
    """
    Faculty endpoint to submit/update grades for their assigned subjects.
    
    POST /api/faculty/grades/
    PUT /api/faculty/grades/
    
    Payload:
    {
        "subject_id": 1,
        "grades": [
            {
                "student_id": 1,
                "marks_obtained": 85,
                "total_marks": 100,
                "grade_letter": "A",
                "remarks": "Excellent performance"
            },
            ...
        ]
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        return self._save_grades(request)
    
    def put(self, request):
        return self._save_grades(request)
    
    def _save_grades(self, request):
        """Common logic for POST and PUT."""
        # Check if user is faculty
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'This endpoint is only accessible to faculty members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get faculty profile
        try:
            faculty_profile = request.user.faculty_profile
        except Exception:
            return Response(
                {'error': 'Faculty profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get request data
        subject_id = request.data.get('subject_id')
        grades_data = request.data.get('grades', [])
        
        # Validate required fields
        if not subject_id:
            return Response(
                {'error': 'subject_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not grades_data or not isinstance(grades_data, list):
            return Response(
                {'error': 'grades must be a non-empty list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get subject
        from apps.academics.models import Subject
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
        
        # Validate each grade entry
        errors = []
        for i, grade_data in enumerate(grades_data):
            if 'student_id' not in grade_data:
                errors.append({'index': i, 'error': 'student_id is required.'})
            if 'marks_obtained' not in grade_data:
                errors.append({'index': i, 'error': 'marks_obtained is required.'})
            if 'total_marks' not in grade_data:
                errors.append({'index': i, 'error': 'total_marks is required.'})
            if 'grade_letter' not in grade_data:
                errors.append({'index': i, 'error': 'grade_letter is required.'})
        
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process grades
        from .models import StudentGrade
        from django.db import transaction
        
        results = []
        try:
            with transaction.atomic():
                for grade_data in grades_data:
                    student_id = grade_data['student_id']
                    
                    # Get student
                    try:
                        student = StudentProfile.objects.get(id=student_id)
                    except StudentProfile.DoesNotExist:
                        raise ValueError(f'Student with id {student_id} not found.')
                    
                    # Create or update grade
                    grade, created = StudentGrade.objects.update_or_create(
                        student=student,
                        subject=subject,
                        defaults={
                            'faculty': faculty_profile,
                            'marks_obtained': grade_data['marks_obtained'],
                            'total_marks': grade_data['total_marks'],
                            'grade_letter': grade_data['grade_letter'],
                            'remarks': grade_data.get('remarks', '')
                        }
                    )
                    
                    results.append({
                        'student_id': student.id,
                        'student_name': student.user.get_full_name() or student.user.username,
                        'grade_letter': grade.grade_letter,
                        'result': 'created' if created else 'updated'
                    })
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to save grades: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'success': True,
            'message': f'Grades saved successfully for {len(results)} students.',
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code
            },
            'results': results
        }, status=status.HTTP_200_OK)


class StudentMyGradesView(APIView):
    """
    Student endpoint to fetch their own grades.
    
    GET /api/students/my-grades/
    
    Returns all grades for the logged-in student with calculated CGPA.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get grades for the current student."""
        # Check if user is a student
        if request.user.role != 'STUDENT':
            return Response(
                {'error': 'This endpoint is only accessible to students.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student profile
        try:
            student_profile = request.user.student_profile
        except Exception:
            return Response(
                {'error': 'Student profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all grades for this student
        from .models import StudentGrade
        grades = StudentGrade.objects.filter(
            student=student_profile
        ).select_related('subject', 'subject__course', 'faculty', 'faculty__user').order_by('-created_at')
        
        # Serialize grades
        serializer = StudentGradeSerializer(grades, many=True)
        
        # Calculate CGPA properly using credits
        total_grades = grades.count()
        total_earned_points = 0.0
        total_attempted_credits = 0.0
        
        for grade in grades:
            # Get subject credits (default to 3 if not set)
            subject_credits = float(grade.subject.credits) if grade.subject.credits else 3.0
            # Get grade point (10-point scale)
            grade_point = grade.grade_point
            # Calculate earned points for this subject
            earned_points = grade_point * subject_credits
            
            total_earned_points += earned_points
            total_attempted_credits += subject_credits
        
        # Calculate CGPA
        if total_attempted_credits > 0:
            cgpa = total_earned_points / total_attempted_credits
            average_percentage = sum(g.percentage for g in grades) / total_grades
        else:
            cgpa = 0.0
            average_percentage = 0.0
        
        return Response({
            'student': {
                'id': student_profile.id,
                'name': request.user.get_full_name() or request.user.username,
                'enrollment_number': student_profile.enrollment_number,
            },
            'grades': serializer.data,
            'statistics': {
                'total_subjects': total_grades,
                'average_percentage': round(average_percentage, 2),
                'cgpa': round(cgpa, 2)
            }
        }, status=status.HTTP_200_OK)


class AdminSubjectGradesView(APIView):
    """
    Admin endpoint to fetch all grades for a specific subject.
    
    GET /api/admin/subject-grades/?subject_id={id}
    
    Returns all student grades for the specified subject.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all grades for a specific subject."""
        # Check if user is admin
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'This endpoint is only accessible to administrators.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get subject_id from query params
        subject_id = request.query_params.get('subject_id')
        
        if not subject_id:
            return Response(
                {'error': 'subject_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get subject
        from apps.academics.models import Subject
        try:
            subject = Subject.objects.select_related('course', 'faculty', 'faculty__user').get(id=subject_id)
        except Subject.DoesNotExist:
            return Response(
                {'error': f'Subject with id {subject_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all students enrolled in this subject through RegisteredCourse
        from apps.students.models import RegisteredCourse
        registered_courses = RegisteredCourse.objects.filter(
            subject=subject,
            semester_registration__approval_status='approved'
        ).select_related('semester_registration__student', 'semester_registration__student__user')
        
        # Get existing grades for this subject
        from .models import StudentGrade
        existing_grades = StudentGrade.objects.filter(
            subject=subject
        ).select_related('student', 'student__user')
        
        # Create a map of student_id to grade
        grades_map = {grade.student.id: grade for grade in existing_grades}
        
        # Build response with all enrolled students and their grades (if any)
        grades_data = []
        total_percentage = 0
        graded_count = 0
        pass_count = 0
        fail_count = 0
        
        for reg_course in registered_courses:
            student = reg_course.semester_registration.student
            grade = grades_map.get(student.id)
            
            if grade:
                # Student has a grade
                grade_data = {
                    'id': grade.id,
                    'student_id': student.id,
                    'student_name': student.user.get_full_name() or student.user.username,
                    'student_enrollment': student.enrollment_number,
                    'marks_obtained': grade.marks_obtained,
                    'total_marks': grade.total_marks,
                    'percentage': grade.percentage,
                    'grade_letter': grade.grade_letter,
                    'remarks': grade.remarks or '',
                    'has_grade': True
                }
                total_percentage += grade.percentage
                graded_count += 1
                if grade.grade_letter != 'F':
                    pass_count += 1
                else:
                    fail_count += 1
            else:
                # Student is enrolled but no grade yet
                grade_data = {
                    'id': None,
                    'student_id': student.id,
                    'student_name': student.user.get_full_name() or student.user.username,
                    'student_enrollment': student.enrollment_number,
                    'marks_obtained': None,
                    'total_marks': None,
                    'percentage': None,
                    'grade_letter': None,
                    'remarks': 'Not graded yet',
                    'has_grade': False
                }
            
            grades_data.append(grade_data)
        
        # Sort by student enrollment number
        grades_data.sort(key=lambda x: x['student_enrollment'] or '')
        
        # Calculate statistics
        total_students = len(grades_data)
        average_percentage = (total_percentage / graded_count) if graded_count > 0 else 0
        pass_rate = (pass_count / graded_count * 100) if graded_count > 0 else 0
        
        return Response({
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'course': subject.course.name if subject.course else None,
                'faculty': subject.faculty.user.get_full_name() if subject.faculty else None,
            },
            'grades': grades_data,
            'statistics': {
                'total_students': total_students,
                'graded_students': graded_count,
                'ungraded_students': total_students - graded_count,
                'average_percentage': round(average_percentage, 2),
                'pass_count': pass_count,
                'fail_count': fail_count,
                'pass_rate': round(pass_rate, 2)
            }
        }, status=status.HTTP_200_OK)
