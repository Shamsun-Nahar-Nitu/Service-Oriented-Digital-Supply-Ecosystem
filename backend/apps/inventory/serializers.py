from rest_framework import serializers

from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Inventory
        fields = (
            "id",
            "product",
            "product_name",
            "sku",
            "quantity_available",
            "reorder_level",
            "warehouse_location",
            "is_low_stock",
            "is_in_stock",
            "last_restocked_at",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "last_restocked_at", "created_at", "updated_at")


class RestockSerializer(serializers.Serializer):
    """Small dedicated payload for the /inventory/{id}/restock/ action."""

    amount = serializers.IntegerField(min_value=1)
