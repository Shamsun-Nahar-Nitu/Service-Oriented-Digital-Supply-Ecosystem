import django_filters as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="mrp", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="mrp", lookup_expr="lte")
    in_stock = filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "vendor", "brand", "issues", "is_active"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(inventory__quantity_in_stock__gt=0)
        return queryset.filter(inventory__quantity_in_stock=0)
