from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "sku",
        "brand",
        "category",
        "vendor",
        "mrp",
        "discount_percent",
        "is_active",
    )
    list_filter = ("is_active", "category", "brand")
    search_fields = ("product_name", "sku", "brand")
    autocomplete_fields = ("category", "vendor")
