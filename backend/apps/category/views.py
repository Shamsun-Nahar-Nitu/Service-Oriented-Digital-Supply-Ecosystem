from rest_framework import viewsets

from apps.core.permissions import IsStaffOrPublicReadOnly

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/categories/

    Read access: any authenticated user (admin, manager, vendor, customer).
    Write access: admin or manager only.
    """

    queryset = Category.objects.select_related("parent").all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrPublicReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.role in (
            self.request.user.Role.ADMIN,
            self.request.user.Role.MANAGER,
        ):
            return queryset
        return queryset.filter(is_active=True)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if not user.is_authenticated or user.role not in (
            user.Role.ADMIN,
            user.Role.MANAGER,
        ):
            return queryset.filter(is_active=True)
        return queryset
    filterset_fields = ["is_active", "parent"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_date"]
