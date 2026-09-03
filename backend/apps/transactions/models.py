import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class Transaction(TimeStampedModel):
    """
    An order placed by a user. Holds no line-item detail itself - that lives
    in TransactionItem - so a transaction can contain any number of products.
    `total_amount` is a snapshot, recalculated from items at creation time,
    so it stays correct even if a product's price changes later.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    transaction_number = models.CharField(
        max_length=40, unique=True, editable=False, default=uuid.uuid4
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="transactions"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction {self.transaction_number} ({self.status})"

    def recalculate_total(self, save=True):
        total = sum((item.line_total for item in self.items.all()), Decimal("0"))
        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount", "updated_at"])
        return total


class TransactionItem(TimeStampedModel):
    """One product line within a transaction, with price frozen at purchase
    time so historical orders remain accurate even if the product price
    changes afterwards."""

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="transaction_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Product's selling price at the moment of purchase.",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
