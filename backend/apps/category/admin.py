from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "parent", "is_active", "created_date"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "code"]
    prepopulated_fields = {"code": ("name",)}
