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
