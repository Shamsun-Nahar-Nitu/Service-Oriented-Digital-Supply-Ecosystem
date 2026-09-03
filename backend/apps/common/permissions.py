"""
Role-based permission classes shared by every app.

The project has four roles (see apps.users.models.User.Role):
    ADMIN    - full access to everything.
    MANAGER  - operational staff: manage catalog, inventory, view all orders.
    VENDOR   - manages only the products/inventory they own.
    CUSTOMER - browses catalog, places orders/payments for themselves.

Keeping these here (rather than duplicating role checks in every viewset)
means the access matrix is defined once and is easy to audit.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def _role(request):
    user = request.user
    return getattr(user, "role", None) if user and user.is_authenticated else None


class IsAdmin(BasePermission):
    """Full access, admin only."""

    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAdminOrManager(BasePermission):
    """Back-office staff: admins and managers."""

    message = "Only administrators or managers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_manager)
        )


class IsAdminManagerOrReadOnly(BasePermission):
    """Anyone authenticated can read (list/retrieve); only staff can write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin or request.user.is_manager


class IsVendorOwnerOrStaff(BasePermission):
    """
    Vendors may create/update/delete only their own objects (object must
    expose a `vendor` attribute). Admins/managers bypass the ownership check.
    Everyone authenticated can read. Customers are read-only - they browse
    the catalog but never own product records.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin or request.user.is_manager or request.user.is_vendor

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin or request.user.is_manager:
            return True
        owner = getattr(obj, "vendor", None)
        return owner is not None and owner == request.user


class IsOwnerOrStaff(BasePermission):
    """
    Generic "you can only see/touch your own record unless you're staff"
    rule, used for transactions/payments (`obj.user`) and profile endpoints.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.is_manager:
            return True
        owner = getattr(obj, "user", None)
        return owner is not None and owner == request.user
