from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Product category. Supports a single level of nesting via `parent` so the
    catalog can express things like Electronics -> Mobile Phones.
    """

    name = models.CharField(max_length=150, unique=True)
    code = models.SlugField(
        max_length=60, unique=True, blank=True, help_text="Short unique code, e.g. 'ELEC'."
    )
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="subcategories", on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)[:60]
        super().save(*args, **kwargs)
