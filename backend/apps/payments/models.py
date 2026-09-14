from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.transactions.models import Transaction


class Payment(TimeStampedModel):
    """
    One payment per transaction. Gateway identifiers are stored as plain
    strings so provider responses can be audited without exposing secrets.
    """

    class Method(models.TextChoices):
        ONLINE = "ONLINE", "Online payment"
        COD = "COD", "Cash on Delivery"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    transaction = models.OneToOneField(
        Transaction, related_name="payment", on_delete=models.CASCADE
    )
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.ONLINE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    gateway = models.CharField(max_length=30, default="SSLCOMMERZ")
    session_key = models.CharField(max_length=100, blank=True, db_index=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    validation_id = models.CharField(max_length=100, blank=True)
    bank_transaction_id = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default="BDT")
    gateway_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_date"]

    def __str__(self):
        return f"Payment for {self.transaction.transaction_number} — {self.status}"

    def mark_successful(self, gateway_reference="", validation_id="", bank_transaction_id=""):
        if self.status == self.Status.SUCCESS:
            return
        self.status = self.Status.SUCCESS
        self.gateway_reference = gateway_reference or self.gateway_reference
        self.validation_id = validation_id or self.validation_id
        self.bank_transaction_id = bank_transaction_id or self.bank_transaction_id
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "gateway_reference", "validation_id", "bank_transaction_id", "paid_at", "updated_date"])

        self.transaction.status = Transaction.Status.CONFIRMED
        self.transaction.save(update_fields=["status", "updated_date"])

    def mark_failed(self):
        if self.status == self.Status.SUCCESS:
            return
        self.status = self.Status.FAILED
        self.save(update_fields=["status", "updated_date"])
