from rest_framework import permissions
from core.constants import Roles

class IsTenantUser(permissions.BasePermission):
    """
    Ensures the user belongs to the same university as the resource being accessed.
    Crucial for Multi-Tenancy isolation.
    """
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'university'):
            return True
        return obj.university == request.user.university


class HasRole(permissions.BasePermission):
    """
    Base class to check if a user has a specific role.
    Usage requires subclassing or dynamic generation.
    """
    required_role = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.roles.filter(role=self.required_role).exists()


class IsStudent(HasRole):
    required_role = Roles.STUDENT

class IsHOD(HasRole):
    required_role = Roles.HOD

class IsDepartmentCommittee(HasRole):
    required_role = Roles.DEPARTMENT_COMMITTEE
