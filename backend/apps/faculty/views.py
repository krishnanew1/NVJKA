from rest_framework import viewsets, permissions
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
            return ClassAssignment.objects.filter(
                faculty=user.faculty_profile
            ).select_related('subject', 'faculty')
        # Admin sees everything
        return ClassAssignment.objects.all().select_related('subject', 'faculty')

    def get_permissions(self):
        # Only admins can create, update, or delete assignments
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]
