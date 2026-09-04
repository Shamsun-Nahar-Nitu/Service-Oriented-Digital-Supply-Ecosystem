"""
Reusable, role-based permission classes.

The project has four user roles (see apps.users.models.User.Role):
ADMIN, MANAGER, VENDOR, CUSTOMER. Rather than re-implementing role checks in
every view, each role gets a small BasePermission here, plus a couple of
composite/object-level helpers used across apps.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def _has_role(request, *roles):
    user = request.user
    return bool(user and user.is_authenticated and user.role in roles)


class IsAdmin(BasePermission):
    message = "This action is restricted to admin users."

    def has_permission(self, request, view):
        return _has_role(
            request, request.user.Role.ADMIN if request.user.is_authenticated else None
        )


class IsManager(BasePermission):
    message = "This action is restricted to manager users."

    def has_permission(self, request, view):
        return _has_role(
            request, request.user.Role.MANAGER if request.user.is_authenticated else None
        )


class IsVendor(BasePermission):
    message = "This action is restricted to vendor users."

    def has_permission(self, request, view):
        return _has_role(
            request, request.user.Role.VENDOR if request.user.is_authenticated else None
        )


class IsCustomer(BasePermission):
    message = "This action is restricted to customer users."

    def has_permission(self, request, view):
        return _has_role(
            request, request.user.Role.CUSTOMER if request.user.is_authenticated else None
        )


class IsAdminOrManager(BasePermission):
    message = "This action is restricted to admin or manager users."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        Role = request.user.Role
        return _has_role(request, Role.ADMIN, Role.MANAGER)


class IsAdminOrReadOnly(BasePermission):
    """Anyone authenticated can read; only admins can write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role == request.user.Role.ADMIN


class IsStaffOrReadOnly(BasePermission):
    """Anyone authenticated can read; admins or managers can write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        if not (request.user and request.user.is_authenticated):
            return False
        Role = request.user.Role
        return request.user.role in (Role.ADMIN, Role.MANAGER)


class IsOwnerOrAdminManager(BasePermission):
    """
    Object-level permission: the resource's owner (matched via a `user` or
    `vendor` attribute on the object) may access it, and admins/managers may
    always access it regardless of ownership.
    """

    owner_fields = ("user", "vendor")

    def has_object_permission(self, request, view, obj):
        user = request.user
        Role = user.Role
        if user.role in (Role.ADMIN, Role.MANAGER):
            return True
        for field in self.owner_fields:
            owner = getattr(obj, field, None)
            if owner is not None:
                return owner == user
        return False
