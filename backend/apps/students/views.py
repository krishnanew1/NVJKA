from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from apps.common.permissions import IsDepartmentHead
from .models import Enrollment, AcademicHistory
from .serializers import EnrollmentSerializer, AcademicHistorySerializer


class IsAdminOrFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'FACULTY')


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for student ``Enrollment`` records.

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
      Students are automatically scoped to their own enrollments;
      Admin and Faculty see all records.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head (same department as the student).

    **Filters** (via query params)

    Standard DRF filtering is available on all fields exposed by the serializer.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return Enrollment.objects.filter(
                student__user=user
            ).select_related('course', 'student')
        return Enrollment.objects.all().select_related('course', 'student')

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)


class AcademicHistoryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for student ``AcademicHistory`` records.

    Stores prior academic credentials (school/college, board, year, grade).

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
      Students are scoped to their own history; Admin and Faculty see all.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head (same department as the student).
    """
    serializer_class = AcademicHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return AcademicHistory.objects.filter(student__user=user)
        return AcademicHistory.objects.all()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)
