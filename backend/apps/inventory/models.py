from django.db import models

from apps.common.models import TimeStampedModel


class Inventory(TimeStampedModel):
    """
    Stock record for a product. One-to-one with Product: this project models
    a single-warehouse-per-product setup. If multi-warehouse support is ever
    needed, add a `Warehouse` model and turn this into a FK instead of O2O.
    """

    product = models.OneToOneField(
        "products.Product", on_delete=models.CASCADE, related_name="inventory"
    )
    quantity_available = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(
        default=10, help_text="Trigger a restock alert when stock falls to/below this."
    )
    warehouse_location = models.CharField(max_length=255, blank=True)
    last_restocked_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        verbose_name_plural = "Inventory"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.product.product_name}: {self.quantity_available} in stock"

    @property
    def is_low_stock(self) -> bool:
        return self.quantity_available <= self.reorder_level

    @property
    def is_in_stock(self) -> bool:
        return self.quantity_available > 0

    def deduct(self, amount: int):
        """Used by the transactions app when an order is placed."""
        if amount > self.quantity_available:
            raise ValueError("Not enough stock available.")
        self.quantity_available -= amount
        self.save(update_fields=["quantity_available", "updated_at"])

    def restock(self, amount: int, user=None):
        from django.utils import timezone

        self.quantity_available += amount
        self.last_restocked_at = timezone.now()
        if user:
            self.updated_by = user
        self.save(
            update_fields=[
                "quantity_available",
                "last_restocked_at",
                "updated_by",
                "updated_at",
            ]
        )
