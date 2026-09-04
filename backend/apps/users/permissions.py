from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Only accounts with role=ADMIN may manage other users."""

    message = "Only admins can manage user accounts."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == user.Role.ADMIN)
