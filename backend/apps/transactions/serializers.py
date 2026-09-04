from rest_framework import serializers

from apps.products.models import Product

from .models import Transaction, TransactionItem
from .services import CheckoutService


class TransactionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = TransactionItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "subtotal"]
        read_only_fields = ["id", "unit_price"]


class TransactionSerializer(serializers.ModelSerializer):
    """Read-only representation of an order, including its line items."""

    items = TransactionItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_number",
            "user",
            "user_email",
            "status",
            "total_amount",
            "shipping_address",
            "notes",
            "items",
            "created_date",
            "updated_date",
        ]
        read_only_fields = fields


class CheckoutItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    """
    Write serializer for POST /api/v1/transactions/checkout/.

    Accepts a cart-like payload:
        {
          "shipping_address": "...",
          "items": [{"product": 1, "quantity": 2}, ...]
        }
    and delegates the actual order creation to CheckoutService.
    """

    shipping_address = serializers.CharField(required=False, allow_blank=True, default="")
    items = CheckoutItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required to check out.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        service = CheckoutService(
            user=user,
            items=validated_data["items"],
            shipping_address=validated_data.get("shipping_address", ""),
        )
        return service.execute()


class TransactionStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by admin/manager to move an order through its lifecycle."""

    class Meta:
        model = Transaction
        fields = ["status"]
