from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    subcategory_count = serializers.IntegerField(source="subcategories.count", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "code",
            "description",
            "parent",
            "parent_name",
            "subcategory_count",
            "is_active",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "created_date", "updated_date"]
