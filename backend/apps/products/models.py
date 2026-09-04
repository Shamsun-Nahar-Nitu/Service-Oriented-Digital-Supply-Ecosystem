from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.category.models import Category
from apps.core.models import TimeStampedModel
from apps.users.models import User


class Product(TimeStampedModel):
    """
    Catalog product.

    `issues` tracks the current quality/fulfilment status of the product
    (damaged stock, a manufacturer recall, etc.) so it can be surfaced to
    admins/managers and hidden from customers independently of `is_active`.
    """

    class IssueStatus(models.TextChoices):
        NONE = "NONE", "No Issues"
        DAMAGED = "DAMAGED", "Damaged"
        RECALLED = "RECALLED", "Recalled"
        QUALITY_HOLD = "QUALITY_HOLD", "Quality Hold"

    product_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock keeping unit.")
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True, db_index=True)

    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    vendor = models.ForeignKey(
        User,
        related_name="products",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.VENDOR},
        help_text="The vendor account that lists and owns this product.",
    )

    issues = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.NONE)
    expire_date = models.DateField(
        null=True, blank=True, help_text="Leave blank for non-perishable goods."
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Maximum retail price.",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this product is listed for sale."
    )

    class Meta:
        db_table = "products"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["product_name"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return f"{self.product_name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.product_name}-{self.sku}")[:220]
        super().save(*args, **kwargs)

    @property
    def selling_price(self):
        """Final price after applying the discount percentage to the MRP."""
        discount_amount = (self.mrp * self.discount_percentage) / 100
        return round(self.mrp - discount_amount, 2)

    @property
    def is_expired(self):
        return bool(self.expire_date and self.expire_date < timezone.now().date())

    @property
    def is_purchasable(self):
        return self.is_active and self.issues == self.IssueStatus.NONE and not self.is_expired
