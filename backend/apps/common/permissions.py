"""
Shared custom permission classes used across multiple apps.
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permission class that allows only users with ADMIN role.
    
    Usage:
        permission_classes = [IsAdminUser]
    """
    
    message = 'Only administrators can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has ADMIN role."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


def _get_object_department(obj):
    """
    Walk common FK chains to find the department of a model instance.
    Returns a Department instance or None.
    """
    # Enrollment -> student -> department
    if hasattr(obj, 'student') and hasattr(obj.student, 'department'):
        return obj.student.department
    # AcademicHistory -> student -> department
    if hasattr(obj, 'student') and hasattr(obj.student, 'department'):
        return obj.student.department
    # Grade -> assessment -> subject -> course -> department
    if hasattr(obj, 'assessment'):
        try:
            return obj.assessment.subject.course.department
        except AttributeError:
            pass
    # Assessment -> subject -> course -> department
    if hasattr(obj, 'subject'):
        try:
            return obj.subject.course.department
        except AttributeError:
            pass
    return None


class IsDepartmentHead(BasePermission):
    """
    Object-level permission for delete operations.

    Rules:
    - ADMIN: always allowed.
    - FACULTY with designation containing 'Head': allowed only if the
      object belongs to their own department.
    - All other roles (including regular Faculty): denied.

    Usage — override destroy() in a ViewSet:

        def get_permissions(self):
            if self.action == 'destroy':
                return [IsDepartmentHead()]
            ...
    """

    message = (
        'Only Admins or Department Heads within the same department '
        'may delete this record.'
    )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'ADMIN':
            return True
        if request.user.role == 'FACULTY':
            try:
                designation = request.user.faculty_profile.designation
                return 'head' in designation.lower()
            except Exception:
                return False
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        # Admin can delete anything
        if request.user.role == 'ADMIN':
            return True
        # Department Head: must be in the same department as the object
        if request.user.role == 'FACULTY':
            try:
                head_dept = request.user.faculty_profile.department
                obj_dept = _get_object_department(obj)
                if obj_dept is None:
                    # Can't determine department — deny by default
                    return False
                return head_dept == obj_dept
            except Exception:
                return False
        return False
