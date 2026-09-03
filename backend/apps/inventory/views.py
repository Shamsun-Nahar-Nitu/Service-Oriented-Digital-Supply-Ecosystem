from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrManager, IsVendorOwnerOrStaff

from .models import Inventory
from .serializers import InventorySerializer, RestockSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    """
    Stock levels. Vendors can see/manage stock for their own products;
    admins/managers see and manage everything. Customers never touch this
    endpoint directly (stock changes happen implicitly via transactions).
    """

    queryset = Inventory.objects.select_related("product", "product__vendor").all()
    serializer_class = InventorySerializer
    filterset_fields = ["product__category"]
    search_fields = ["product__product_name", "product__sku"]
    ordering_fields = ["quantity_available", "updated_at"]

    def get_permissions(self):
        if self.action == "restock":
            return [IsAdminOrManager()]
        return [IsVendorOwnerOrStaff()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_vendor:
            qs = qs.filter(product__vendor=user)
        return qs

    def has_object_permission_check(self, obj):
        # Inventory doesn't have its own `vendor` field, so translate
        # ownership through the related product for IsVendorOwnerOrStaff.
        return obj.product.vendor

    @action(detail=True, methods=["post"])
    def restock(self, request, pk=None):
        """POST /api/inventory/{id}/restock/  { "amount": 50 }"""
        inventory = self.get_object()
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inventory.restock(serializer.validated_data["amount"], user=request.user)
        return Response(InventorySerializer(inventory).data)
