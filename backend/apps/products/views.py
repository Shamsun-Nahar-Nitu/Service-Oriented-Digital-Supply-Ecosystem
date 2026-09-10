from django.db.models import Q
from django.utils import timezone
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

    def _public_filter(self):
        return Q(
            is_active=True,
            issues=Product.IssueStatus.NONE,
        ) & (Q(expire_date__isnull=True) | Q(expire_date__gte=timezone.now().date()))

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "vendor", "inventory")
        user = self.request.user

        public_filter = self._public_filter()

        if not user.is_authenticated:
            return queryset.filter(public_filter)
        if user.role in (user.Role.ADMIN, user.Role.MANAGER):
            return queryset
        if user.role == user.Role.VENDOR:
            # Vendors see their own catalog (including inactive items) plus
            # everyone else's active listings.
            return queryset.filter(
                Q(vendor=user) | public_filter
            )
        return queryset.filter(public_filter)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if not user.is_authenticated:
            return queryset.filter(self._public_filter())
        if user.role in (user.Role.ADMIN, user.Role.MANAGER):
            return queryset
        if user.role == user.Role.VENDOR:
            return queryset.filter(Q(vendor=user) | self._public_filter())
        return queryset.filter(self._public_filter())

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_vendor:
            serializer.save(vendor=user)
        else:
            serializer.save()
