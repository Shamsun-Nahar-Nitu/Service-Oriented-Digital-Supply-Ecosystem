from django.contrib import admin

from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ("unit_price",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_number", "user", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("transaction_number", "user__email")
    readonly_fields = ("transaction_number", "total_amount")
    inlines = [TransactionItemInline]
