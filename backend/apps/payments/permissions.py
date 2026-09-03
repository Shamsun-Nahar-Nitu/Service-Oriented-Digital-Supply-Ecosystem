from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTransactionOwnerOrStaff(BasePermission):
    """Payment has no direct `user` field - ownership is via `payment.transaction.user`."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.is_manager:
            return True
        if request.method in SAFE_METHODS:
            return obj.transaction.user == request.user
        # Only staff can mark payments success/failed/refunded manually.
        return False
