from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Public self-registration endpoint.

    Customers and vendors can self-register. Admin/Manager accounts are
    intentionally NOT creatable through this endpoint — those are provisioned
    by an existing admin via the /users/ management endpoint (or the Django
    admin), so privilege escalation isn't a single unauthenticated API call
    away.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    SELF_REGISTERABLE_ROLES = (User.Role.CUSTOMER, User.Role.VENDOR)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "role",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {"role": {"default": User.Role.CUSTOMER}}

    def validate_role(self, value):
        if value not in self.SELF_REGISTERABLE_ROLES:
            raise serializers.ValidationError(
                "Self-registration is only available for customer or vendor accounts."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Read/update serializer used for the authenticated user's own profile."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "address",
            "role",
            "is_active",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "created_date", "updated_date"]


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Full-control serializer used by admins to manage any user, including
    role changes and activation/deactivation.
    """

    password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "address",
            "role",
            "is_active",
            "password",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "created_date", "updated_date"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT's login serializer to embed `role` and `full_name` as
    custom claims in the access token, and to return a small user object
    alongside the tokens so the frontend doesn't need a follow-up request
    just to know who logged in.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
