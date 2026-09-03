"""
Shared abstract base models.

Every domain model in this project (Category, Product, Inventory,
Transaction, Payment, ...) inherits `TimeStampedModel` instead of redefining
created_at/updated_at by hand. One place to change the behaviour, no
copy-paste drift between apps.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """Adds self-updating `created_at` / `updated_at` fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    """
    Optional mixin for models where we'd rather deactivate/hide a row than
    lose it forever (e.g. a product that was sold in the past shouldn't
    vanish from historical transactions just because it's discontinued).
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
