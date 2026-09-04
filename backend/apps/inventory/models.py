from django.db import models

from apps.core.models import TimeStampedModel
from apps.products.models import Product


class Inventory(TimeStampedModel):
    """One inventory record per product — the current stock level and reorder threshold."""

    product = models.OneToOneField(Product, related_name="inventory", on_delete=models.CASCADE)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(
        default=10, help_text="Quantity at/below which the product should be restocked."
    )
    warehouse_location = models.CharField(max_length=150, blank=True)
    last_restocked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory"
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.product.product_name} — {self.quantity_in_stock} in stock"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    @property
    def is_in_stock(self):
        return self.quantity_in_stock > 0


class StockMovement(TimeStampedModel):
    """
    Immutable audit trail of every stock change. Rows are created by the
    application (restocks, sales, returns, damage write-offs) rather than
    edited — `Inventory.quantity_in_stock` is the current total and this
    table explains how it got there.
    """

    class MovementType(models.TextChoices):
        RESTOCK = "RESTOCK", "Restock"
        SALE = "SALE", "Sale"
        RETURN = "RETURN", "Return"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        DAMAGE = "DAMAGE", "Damage"

    inventory = models.ForeignKey(Inventory, related_name="movements", on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.IntegerField(
        help_text="Positive for stock added, negative for stock removed."
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "stock_movements"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.movement_type} {self.quantity:+d} — {self.inventory.product.product_name}"
