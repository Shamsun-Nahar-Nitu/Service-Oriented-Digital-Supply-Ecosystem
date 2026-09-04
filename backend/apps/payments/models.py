from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.transactions.models import Transaction


class Payment(TimeStampedModel):
    """
    One payment per transaction. `method` covers the common e-commerce
    payment rails; `gateway_reference` stores whatever ID a real payment
    gateway (Stripe/Razorpay/etc.) would return, kept as a plain string so
    swapping providers doesn't require a schema change.
    """

    class Method(models.TextChoices):
        CARD = "CARD", "Credit/Debit Card"
        UPI = "UPI", "UPI"
        NET_BANKING = "NET_BANKING", "Net Banking"
        WALLET = "WALLET", "Wallet"
        COD = "COD", "Cash on Delivery"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    transaction = models.OneToOneField(
        Transaction, related_name="payment", on_delete=models.CASCADE
    )
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    gateway_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_date"]

    def __str__(self):
        return f"Payment for {self.transaction.transaction_number} — {self.status}"

    def mark_successful(self, gateway_reference=""):
        self.status = self.Status.SUCCESS
        self.gateway_reference = gateway_reference or self.gateway_reference
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "gateway_reference", "paid_at", "updated_date"])

        self.transaction.status = Transaction.Status.CONFIRMED
        self.transaction.save(update_fields=["status", "updated_date"])

    def mark_failed(self):
        self.status = self.Status.FAILED
        self.save(update_fields=["status", "updated_date"])
