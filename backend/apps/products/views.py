from rest_framework import viewsets

from .filters import ProductFilter
from .models import Product
from .permissions import ProductPermission
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    /api/v1/products/

    Customers/vendors see only active, issue-free, non-expired products
    unless they are staff (admin/manager) or the owning vendor, who can see
    everything including drafts and flagged stock.
    """

    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]
    filterset_class = ProductFilter
    search_fields = ["product_name", "brand", "sku", "description"]
    ordering_fields = ["mrp", "created_date", "product_name"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "vendor", "inventory")
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()
        if user.role in (user.Role.ADMIN, user.Role.MANAGER):
            return queryset
        if user.role == user.Role.VENDOR:
            # Vendors see their own catalog (including inactive items) plus
            # everyone else's active listings.
            from django.db.models import Q

            return queryset.filter(
                Q(vendor=user) | Q(is_active=True, issues=Product.IssueStatus.NONE)
            )
        return queryset.filter(is_active=True, issues=Product.IssueStatus.NONE)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_vendor:
            serializer.save(vendor=user)
        else:
            serializer.save()
