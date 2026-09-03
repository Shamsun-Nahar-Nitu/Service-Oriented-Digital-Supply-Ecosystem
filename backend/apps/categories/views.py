from rest_framework import viewsets

from apps.common.permissions import IsAdminManagerOrReadOnly

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Everyone authenticated can browse categories; only admins/managers can
    create, edit or archive them.
    """

    queryset = Category.objects.select_related("parent", "created_by").all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminManagerOrReadOnly]
    filterset_fields = ["is_active", "parent"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
