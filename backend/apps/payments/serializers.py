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
            "gateway",
            "session_key",
            "gateway_transaction_id",
            "validation_id",
            "bank_transaction_id",
            "currency",
            "gateway_reference",
            "paid_at",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "id",
            "status",
            "amount",
            "gateway_reference",
            "gateway",
            "session_key",
            "gateway_transaction_id",
            "validation_id",
            "bank_transaction_id",
            "currency",
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
        if transaction:
            attrs["amount"] = transaction.total_amount
            attrs["currency"] = "BDT"
            method = attrs.get("method", Payment.Method.ONLINE)
            if method == Payment.Method.ONLINE and not transaction.user.phone_number.strip():
                raise serializers.ValidationError(
                    {"transaction": "A phone number is required for online payment."}
                )
        return attrs
