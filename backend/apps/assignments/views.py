from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Assignment, AssignmentSubmission
from .permissions import IsFaculty, IsStudent, IsAssignmentOwner
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    AssignmentSubmitSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        qs = Assignment.objects.select_related('subject', 'department', 'created_by')

        if user.role == 'FACULTY':
            return qs.filter(created_by=user)

        if user.role == 'STUDENT':
            try:
                sp = user.student_profile
            except Exception:
                return qs.none()

            return qs.filter(
                department=sp.department,
                batch_year=sp.batch_year,
                semester=sp.current_semester,
            )

        # Admin sees all
        if user.role == 'ADMIN':
            return qs

        return qs.none()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsFaculty()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if user.role == 'FACULTY' and obj.created_by_id != user.id:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'STUDENT':
            try:
                sp = user.student_profile
            except Exception:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            if not (
                obj.department_id == sp.department_id
                and obj.batch_year == sp.batch_year
                and obj.semester == sp.current_semester
            ):
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsStudent], parser_classes=[MultiPartParser, FormParser])
    def submit(self, request, pk=None):
        assignment = self.get_object()

        # Ensure student is eligible for the assignment
        try:
            sp = request.user.student_profile
        except Exception:
            return Response({'detail': 'Student profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        if not (
            assignment.department_id == sp.department_id
            and assignment.batch_year == sp.batch_year
            and assignment.semester == sp.current_semester
        ):
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not assignment.requires_submission:
            return Response({'detail': 'This assignment does not accept submissions.'}, status=status.HTTP_400_BAD_REQUEST)

        # Late policy
        now = timezone.now()
        if assignment.due_at and now > assignment.due_at and not assignment.allow_late:
            return Response({'detail': 'Submission is closed (past due date).'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssignmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission, _ = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=sp,
        )
        submission.file = serializer.validated_data.get('file') or submission.file
        submission.text_answer = serializer.validated_data.get('text_answer', submission.text_answer)
        submission.mark_submitted()
        submission.save()

        out = AssignmentSubmissionSerializer(submission, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsFaculty])
    def submissions(self, request, pk=None):
        assignment = self.get_object()
        if assignment.created_by_id != request.user.id:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        qs = assignment.submissions.select_related('student__user').all()
        data = AssignmentSubmissionSerializer(qs, many=True, context={'request': request}).data
        return Response(data, status=status.HTTP_200_OK)


class AssignmentSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optional: allows faculty to list submissions across their assignments.
    """

    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsFaculty]

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(
            assignment__created_by=self.request.user
        ).select_related('assignment', 'student__user')

