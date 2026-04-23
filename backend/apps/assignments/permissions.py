from rest_framework.permissions import BasePermission


class IsFaculty(BasePermission):
    message = 'Faculty privileges required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'FACULTY'
        )


class IsStudent(BasePermission):
    message = 'Student privileges required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'STUDENT'
        )


class IsAssignmentOwner(BasePermission):
    message = 'You do not have permission to access this assignment.'

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(obj, 'created_by_id', None) == request.user.id
        )
