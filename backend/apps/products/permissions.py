from rest_framework.permissions import SAFE_METHODS, BasePermission


class ProductPermission(BasePermission):
    """
    - Read (GET/HEAD/OPTIONS): any authenticated user.
    - Create: admin, manager, or vendor.
    - Update/Delete: admin, manager, or the vendor who owns the product.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        Role = request.user.Role
        return request.user.role in (Role.ADMIN, Role.MANAGER, Role.VENDOR)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        Role = request.user.Role
        if request.user.role in (Role.ADMIN, Role.MANAGER):
            return True
        return request.user.role == Role.VENDOR and obj.vendor_id == request.user.id
