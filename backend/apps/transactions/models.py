import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.constants import PLATFORM_CUSTOMER_FEE_RATE
from apps.core.models import TimeStampedModel
from apps.products.models import Product
from apps.users.models import User


class Transaction(TimeStampedModel):
    """An order placed by a customer. Line items live in TransactionItem."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"
        REFUNDED = "REFUNDED", "Refunded"

    transaction_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    items_subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Sum of line-item subtotals, before the platform fee.",
    )
    platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=(
            "Platform service fee charged to the customer on top of "
            "items_subtotal (see apps.core.constants.PLATFORM_CUSTOMER_FEE_RATE)."
        ),
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Amount actually charged to the customer: items_subtotal + platform_fee.",
    )
    shipping_address = models.TextField(blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_date"]

    def __str__(self):
        return f"Transaction {self.transaction_number} — {self.user.email}"

    def recalculate_total(self):
        """
        Recomputes items_subtotal, platform_fee and total_amount from the
        current line items.

        total_amount — not items_subtotal — is what Payment.amount is set
        from (see apps.payments.views) and what SSLCommerz is asked to
        collect, so the platform's customer-side fee is real money that
        changes hands at checkout, not just a reporting label.
        """
        subtotal = sum((item.subtotal for item in self.items.all()), start=Decimal("0"))
        fee = (subtotal * PLATFORM_CUSTOMER_FEE_RATE).quantize(Decimal("0.01"))
        self.items_subtotal = subtotal
        self.platform_fee = fee
        self.total_amount = subtotal + fee
        self.save(
            update_fields=["items_subtotal", "platform_fee", "total_amount", "updated_date"]
        )


class TransactionItem(TimeStampedModel):
    """A single product line within a transaction, priced at time of purchase."""

    transaction = models.ForeignKey(Transaction, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="transaction_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Snapshot of the product's selling price at the time of purchase.",
    )

    class Meta:
        db_table = "transaction_items"
        unique_together = ("transaction", "product")
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    @property
    def subtotal(self):
        return round(self.unit_price * self.quantity, 2)