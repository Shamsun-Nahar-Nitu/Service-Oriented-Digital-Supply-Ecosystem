from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrManager

from .models import Inventory
from .serializers import InventorySerializer, RestockSerializer, StockMovementSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/inventory/

    Restricted to admin/manager — vendors and customers see stock levels
    indirectly through the `quantity_in_stock` field on the product API
    instead of managing inventory records directly.
    """

    queryset = Inventory.objects.select_related("product").all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ["product"]
    search_fields = ["product__product_name", "product__sku"]
    ordering_fields = ["quantity_in_stock", "updated_date"]

    @action(detail=True, methods=["post"])
    def restock(self, request, pk=None):
        """POST /api/v1/inventory/{id}/restock/ — add stock and record the movement."""
        inventory = self.get_object()
        serializer = RestockSerializer(data=request.data, context={"inventory": inventory})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InventorySerializer(inventory).data)

    @action(detail=True, methods=["get"])
    def movements(self, request, pk=None):
        """GET /api/v1/inventory/{id}/movements/ — audit trail for this product's stock."""
        inventory = self.get_object()
        movements = inventory.movements.all()
        return Response(StockMovementSerializer(movements, many=True).data)
