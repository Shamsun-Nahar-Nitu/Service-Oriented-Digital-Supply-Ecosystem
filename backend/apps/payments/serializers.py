from rest_framework import serializers

from apps.transactions.models import Transaction

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # Not required on input: defaults to the transaction's total_amount in
    # validate() below, so clients never have to (and never get to) invent
    # their own payment amount.
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

    class Meta:
        model = Payment
        fields = (
            "id",
            "transaction",
            "method",
            "status",
            "amount",
            "gateway_reference",
            "paid_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "gateway_reference",
            "paid_at",
            "created_at",
            "updated_at",
        )

    def validate_transaction(self, value: Transaction):
        request = self.context.get("request")
        if request and not (request.user.is_admin or request.user.is_manager):
            if value.user != request.user:
                raise serializers.ValidationError("You can only pay for your own transaction.")
        if hasattr(value, "payment"):
            raise serializers.ValidationError("This transaction already has a payment record.")
        return value

    def validate(self, attrs):
        # Never trust a client-supplied amount - always derive it from the
        # transaction's own total so a payment can't be under/over-recorded.
        transaction = attrs.get("transaction")
        if transaction:
            attrs["amount"] = transaction.total_amount
        return attrs
