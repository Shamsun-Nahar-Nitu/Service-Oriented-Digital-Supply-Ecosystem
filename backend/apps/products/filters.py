import django_filters as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    """Lets the frontend query things like:
    /api/v1/products/?min_price=100&max_price=500&category=3&brand=sony
    """

    min_price = filters.NumberFilter(field_name="mrp", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="mrp", lookup_expr="lte")
    brand = filters.CharFilter(field_name="brand", lookup_expr="icontains")
    is_expired = filters.BooleanFilter(method="filter_is_expired")

    class Meta:
        model = Product
        fields = ["category", "vendor", "brand", "is_active"]

    def filter_is_expired(self, queryset, name, value):
        from django.utils import timezone

        today = timezone.now().date()
        if value:
            return queryset.filter(expire_date__lt=today)
        return queryset.filter(models_q_expire_gte_or_null(today))


def models_q_expire_gte_or_null(today):
    from django.db.models import Q

    return Q(expire_date__gte=today) | Q(expire_date__isnull=True)
