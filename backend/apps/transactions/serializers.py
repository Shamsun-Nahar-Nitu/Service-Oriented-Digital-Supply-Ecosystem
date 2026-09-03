from django.db import transaction as db_transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.products.models import Product

from .models import Transaction, TransactionItem


class TransactionItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = TransactionItem
        fields = ("id", "product", "product_name", "sku", "quantity", "unit_price", "line_total")
        read_only_fields = fields


class TransactionItemWriteSerializer(serializers.Serializer):
    """Input shape for creating an order: just product + quantity.
    Price is derived server-side from the product's current selling price -
    never trust a client-supplied price."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1)


class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemReadSerializer(many=True, read_only=True)
    order_items = TransactionItemWriteSerializer(many=True, write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "transaction_number",
            "user",
            "user_email",
            "status",
            "total_amount",
            "shipping_address",
            "notes",
            "items",
            "order_items",
            "payment",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "transaction_number",
            "total_amount",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_payment(self, obj):
        # Avoid a circular import at module load time.
        from apps.payments.serializers import PaymentSerializer

        if hasattr(obj, "payment"):
            return PaymentSerializer(obj.payment).data
        return None

    def validate_order_items(self, value):
        if not value:
            raise serializers.ValidationError("A transaction needs at least one item.")
        for entry in value:
            product = entry["product"]
            quantity = entry["quantity"]
            inventory = getattr(product, "inventory", None)
            available = inventory.quantity_available if inventory else 0
            if available < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for '{product.product_name}' "
                    f"(requested {quantity}, available {available})."
                )
        return value

    @db_transaction.atomic
    def create(self, validated_data):
        order_items = validated_data.pop("order_items")
        user = self.context["request"].user
        txn = Transaction.objects.create(user=user, **validated_data)

        for entry in order_items:
            product = entry["product"]
            quantity = entry["quantity"]
            TransactionItem.objects.create(
                transaction=txn,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
            )
            # Deduct stock immediately on order placement.
            product.inventory.deduct(quantity)

        txn.recalculate_total()
        return txn
