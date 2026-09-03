from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class Product(TimeStampedModel):
    """
    A sellable product.

    `mrp` (maximum retail price) and `discount_percent` are stored
    separately, and `selling_price` is derived rather than duplicated, so
    changing the discount can never leave a stale selling price behind.
    """

    sku = models.CharField(
        "SKU", max_length=64, unique=True, help_text="Stock keeping unit / product code."
    )
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=150, blank=True)
    issues = models.TextField(
        blank=True,
        help_text="Known defects, recalls or quality issues reported for this product.",
    )
    expire_date = models.DateField(
        null=True, blank=True, help_text="Leave blank for products that don't expire."
    )
    mrp = models.DecimalField(
        "MRP", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )

    category = models.ForeignKey(
        "categories.Category", on_delete=models.PROTECT, related_name="products"
    )
    vendor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        limit_choices_to={"role": "vendor"},
        help_text="Vendor who owns/supplies this product, if any.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product_name"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return f"{self.product_name} ({self.sku})"

    @property
    def selling_price(self) -> Decimal:
        discount_amount = (self.mrp * self.discount_percent) / Decimal("100")
        return (self.mrp - discount_amount).quantize(Decimal("0.01"))

    @property
    def is_expired(self) -> bool:
        if not self.expire_date:
            return False
        from django.utils import timezone

        return self.expire_date < timezone.now().date()
