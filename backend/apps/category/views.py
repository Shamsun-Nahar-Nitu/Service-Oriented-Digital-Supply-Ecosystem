from rest_framework import viewsets

from apps.core.permissions import IsStaffOrReadOnly

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
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["is_active", "parent"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_date"]
