from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    transaction_number = serializers.CharField(
        source="transaction.transaction_number", read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "transaction",
            "transaction_number",
            "method",
            "status",
            "amount",
            "gateway_reference",
            "paid_at",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "id",
            "status",
            "gateway_reference",
            "paid_at",
            "created_date",
            "updated_date",
        ]
        extra_kwargs = {"amount": {"required": False}}

    def validate_transaction(self, value):
        request = self.context["request"]
        user = request.user
        if user.role not in (user.Role.ADMIN, user.Role.MANAGER) and value.user_id != user.id:
            raise serializers.ValidationError("You can only pay for your own orders.")
        if hasattr(value, "payment"):
            raise serializers.ValidationError("A payment already exists for this transaction.")
        return value

    def validate(self, attrs):
        transaction = attrs.get("transaction")
        if transaction and attrs.get("amount") is None:
            attrs["amount"] = transaction.total_amount
        return attrs


class PaymentConfirmSerializer(serializers.Serializer):
    """Simulates a payment gateway callback confirming (or failing) a payment."""

    success = serializers.BooleanField(default=True)
    gateway_reference = serializers.CharField(required=False, allow_blank=True, default="")
