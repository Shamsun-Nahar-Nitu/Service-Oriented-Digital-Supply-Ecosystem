from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# Roles the public registration endpoint is allowed to create.
# Admin/manager accounts are provisioned by an existing admin (or via
# `python manage.py createsuperuser` / the Django admin), never self-served.
PUBLIC_REGISTRATION_ROLES = (User.Role.CUSTOMER, User.Role.VENDOR)


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user, used for profile / admin listing."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "business_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class RegisterSerializer(serializers.ModelSerializer):
    """Public sign-up endpoint. Restricted to customer/vendor roles."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "business_name",
        )
        read_only_fields = ("id",)

    def validate_role(self, value):
        if value not in PUBLIC_REGISTRATION_ROLES:
            raise serializers.ValidationError(
                "Self-registration is only available for customer or vendor accounts."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """
    Used by admins to create staff accounts (manager/vendor/admin) directly,
    bypassing the role restriction on the public register endpoint.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "business_name",
            "is_active",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        if user.role == User.Role.ADMIN:
            user.is_staff = True
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Adds a few useful, non-sensitive claims to the JWT payload so a frontend
    can render role-based UI without a second round trip, and returns the
    user profile alongside the tokens.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        token["full_name"] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
