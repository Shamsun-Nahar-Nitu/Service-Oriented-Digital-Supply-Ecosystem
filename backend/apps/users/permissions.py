from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only users with role=admin (or Django superusers) may proceed."""

    message = "Only administrators can manage user accounts."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin)
