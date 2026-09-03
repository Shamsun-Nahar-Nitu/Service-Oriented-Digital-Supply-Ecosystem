import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class Payment(TimeStampedModel):
    """
    Payment record for a transaction. One-to-one: this project assumes a
    single payment attempt settles an order. Partial/split payments or
    multiple retries would need a FK instead - noted here for whoever
    extends this later.
    """

    class Method(models.TextChoices):
        CASH_ON_DELIVERY = "cod", "Cash on Delivery"
        CARD = "card", "Credit/Debit Card"
        UPI = "upi", "UPI"
        NET_BANKING = "net_banking", "Net Banking"
        WALLET = "wallet", "Wallet"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    transaction = models.OneToOneField(
        "transactions.Transaction", on_delete=models.CASCADE, related_name="payment"
    )
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        default=uuid.uuid4,
        help_text="Reference/transaction ID returned by the payment gateway.",
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for {self.transaction.transaction_number} - {self.status}"

    def mark_success(self):
        from django.utils import timezone

        self.status = self.Status.SUCCESS
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])

    def mark_failed(self):
        self.status = self.Status.FAILED
        self.save(update_fields=["status", "updated_at"])
