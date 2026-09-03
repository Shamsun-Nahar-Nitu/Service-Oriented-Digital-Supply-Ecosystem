from rest_framework import serializers

from apps.categories.models import Category

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    vendor_name = serializers.CharField(
        source="vendor.get_full_name", read_only=True, default=None
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "product_name",
            "description",
            "brand",
            "issues",
            "expire_date",
            "mrp",
            "discount_percent",
            "selling_price",
            "is_expired",
            "category",
            "category_name",
            "vendor",
            "vendor_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_category(self, value: Category):
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign an inactive category.")
        return value

    def validate(self, attrs):
        # Vendors may only ever create products under their own name -
        # enforced again here (belt & braces on top of the viewset logic).
        request = self.context.get("request")
        if request and request.user.is_vendor:
            attrs["vendor"] = request.user
        return attrs
