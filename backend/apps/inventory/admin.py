from django.contrib import admin

from .models import Inventory, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ["movement_type", "quantity", "note", "created_date"]
    can_delete = False


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "quantity_in_stock",
        "reorder_level",
        "is_low_stock",
        "last_restocked_at",
    ]
    list_filter = ["warehouse_location"]
    search_fields = ["product__product_name", "product__sku"]
    inlines = [StockMovementInline]

    @admin.display(boolean=True, description="Low stock")
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["inventory", "movement_type", "quantity", "created_date"]
    list_filter = ["movement_type"]
