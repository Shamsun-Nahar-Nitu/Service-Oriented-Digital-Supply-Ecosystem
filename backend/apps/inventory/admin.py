from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity_available",
        "reorder_level",
        "warehouse_location",
        "last_restocked_at",
    )
    search_fields = ("product__product_name", "product__sku")
    autocomplete_fields = ("product",)
