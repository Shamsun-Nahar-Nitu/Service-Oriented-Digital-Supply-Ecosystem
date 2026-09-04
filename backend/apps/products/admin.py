from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "product_name",
        "sku",
        "brand",
        "category",
        "vendor",
        "mrp",
        "discount_percentage",
        "issues",
        "is_active",
        "created_date",
    ]
    list_filter = ["issues", "is_active", "category", "brand"]
    search_fields = ["product_name", "sku", "brand"]
    autocomplete_fields = ["category", "vendor"]
    prepopulated_fields = {"slug": ("product_name",)}
    readonly_fields = ["created_date", "updated_date"]
