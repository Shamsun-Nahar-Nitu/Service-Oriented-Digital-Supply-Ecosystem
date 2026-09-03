from rest_framework import viewsets

from apps.common.permissions import IsVendorOwnerOrStaff

from .filters import ProductFilter
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Catalog browsing is open to any authenticated role (customers need to
    see products to buy them). Writing is restricted:
      - Admin/Manager: can create/edit/delete any product.
      - Vendor: can create products (auto-assigned to themselves) and can
        only edit/delete their own.
      - Customer: read-only.
    """

    queryset = Product.objects.select_related("category", "vendor").all()
    serializer_class = ProductSerializer
    permission_classes = [IsVendorOwnerOrStaff]
    filterset_class = ProductFilter
    search_fields = ["product_name", "sku", "brand", "description"]
    ordering_fields = ["mrp", "created_at", "product_name"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Customers should only ever see live, purchasable products.
        if user.is_authenticated and user.is_customer:
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_vendor:
            serializer.save(vendor=user)
        else:
            serializer.save()
