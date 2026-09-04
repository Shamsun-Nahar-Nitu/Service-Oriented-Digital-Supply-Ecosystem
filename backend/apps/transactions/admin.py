from django.contrib import admin

from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ["product", "quantity", "unit_price"]
    can_delete = False


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_number", "user", "status", "total_amount", "created_date"]
    list_filter = ["status"]
    search_fields = ["transaction_number", "user__email"]
    readonly_fields = ["transaction_number", "total_amount", "created_date", "updated_date"]
    inlines = [TransactionItemInline]
