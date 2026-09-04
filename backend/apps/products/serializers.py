from rest_framework import serializers

from apps.users.models import User

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_purchasable = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    vendor_name = serializers.CharField(source="vendor.full_name", read_only=True)
    quantity_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "slug",
            "sku",
            "description",
            "brand",
            "category",
            "category_name",
            "vendor",
            "vendor_name",
            "issues",
            "expire_date",
            "mrp",
            "discount_percentage",
            "selling_price",
            "quantity_in_stock",
            "is_active",
            "is_expired",
            "is_purchasable",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "slug", "created_date", "updated_date"]
        extra_kwargs = {"vendor": {"required": False}}

    def get_quantity_in_stock(self, obj) -> int:
        inventory = getattr(obj, "inventory", None)
        return inventory.quantity_in_stock if inventory else 0

    def validate_vendor(self, value):
        if value.role != User.Role.VENDOR:
            raise serializers.ValidationError("The assigned vendor must have the VENDOR role.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None

        if user and user.is_authenticated and user.is_vendor:
            # Vendors may only ever create/update products under their own account,
            # regardless of what (if anything) was submitted in the payload.
            attrs["vendor"] = user
        elif not self.instance and "vendor" not in attrs:
            # Admin/manager creating a product on behalf of a vendor must say which one.
            raise serializers.ValidationError({"vendor": "This field is required."})

        return attrs
