import uuid

from django.core.validators import MinValueValidator
from django.db import models

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
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_date"]

    def __str__(self):
        return f"Transaction {self.transaction_number} — {self.user.email}"

    def recalculate_total(self):
        total = sum((item.subtotal for item in self.items.all()), start=0)
        self.total_amount = total
        self.save(update_fields=["total_amount", "updated_date"])


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
