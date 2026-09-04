from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-managed `created_date` and
    `updated_date` fields.

    Every domain model in this project (User, Product, Category, Inventory,
    Transaction, Payment, ...) inherits from this instead of redeclaring the
    same two fields, so auditing behaviour stays consistent everywhere.
    """

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_date"]
