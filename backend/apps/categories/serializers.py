from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    subcategory_count = serializers.IntegerField(
        source="subcategories.count", read_only=True
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "code",
            "description",
            "parent",
            "is_active",
            "created_by",
            "subcategory_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "code", "created_by", "created_at", "updated_at")
