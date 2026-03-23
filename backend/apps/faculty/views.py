from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import ClassAssignment
from .serializers import ClassAssignmentSerializer


class IsAdminOrFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'FACULTY')


class ClassAssignmentViewSet(viewsets.ModelViewSet):
    """
    Class Assignment API:
    - Faculty see only their own assigned classes.
    - Admins see and manage all assignments.
    """
    serializer_class = ClassAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'FACULTY':
            try:
                faculty_profile = user.faculty_profile
                return ClassAssignment.objects.filter(
                    faculty=faculty_profile
                ).select_related('subject', 'subject__course', 'faculty', 'faculty__user')
            except ObjectDoesNotExist:
                # Return empty queryset if faculty profile doesn't exist
                return ClassAssignment.objects.none()
        # Admin sees everything
        return ClassAssignment.objects.all().select_related('subject', 'subject__course', 'faculty', 'faculty__user')

    def list(self, request, *args, **kwargs):
        """Override list to handle missing faculty profile gracefully."""
        if request.user.role == 'FACULTY':
            try:
                faculty_profile = request.user.faculty_profile
            except ObjectDoesNotExist:
                return Response(
                    {"detail": "No faculty profile found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        # Only admins can create, update, or delete assignments
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]
