from django.utils import timezone
from rest_framework import serializers

from .models import Inventory, StockMovement


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "product",
            "product_name",
            "sku",
            "quantity_in_stock",
            "reorder_level",
            "warehouse_location",
            "is_low_stock",
            "last_restocked_at",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "product", "created_date", "updated_date"]


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "inventory", "movement_type", "quantity", "note", "created_date"]
        read_only_fields = ["id", "created_date"]


class RestockSerializer(serializers.Serializer):
    """Used by the `restock` action on InventoryViewSet."""

    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def save(self, **kwargs):
        inventory = self.context["inventory"]
        quantity = self.validated_data["quantity"]
        note = self.validated_data.get("note", "")

        inventory.quantity_in_stock += quantity
        inventory.last_restocked_at = timezone.now()
        inventory.save(update_fields=["quantity_in_stock", "last_restocked_at", "updated_date"])

        return StockMovement.objects.create(
            inventory=inventory,
            movement_type=StockMovement.MovementType.RESTOCK,
            quantity=quantity,
            note=note,
        )
