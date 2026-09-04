from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.products.models import Product

from .models import Inventory


@receiver(post_save, sender=Product)
def create_inventory_for_new_product(sender, instance, created, **kwargs):
    """Every new product automatically gets a zero-stock inventory record."""
    if created:
        Inventory.objects.get_or_create(product=instance)
