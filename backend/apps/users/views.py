from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminRole
from .serializers import (
    AdminCreateUserSerializer,
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Public sign-up. Anyone can create a customer or vendor account."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class EmailTokenObtainPairView(TokenObtainPairView):
    """Login. Exchanges email + password for an access/refresh token pair."""

    serializer_class = EmailTokenObtainPairSerializer


class MeView(APIView):
    """Get or update the currently authenticated user's own profile."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def patch(self, request):
        # Users may edit their own basic details but not their own role.
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("role", None)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses=None)
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."})


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only user directory: list/create/update/deactivate any account
    (managers, vendors, customers, other admins).
    """

    queryset = User.objects.all()
    permission_classes = [IsAdminRole]
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name", "business_name"]
    ordering_fields = ["created_at", "email"]

    def get_serializer_class(self):
        if self.action == "create":
            return AdminCreateUserSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        # Soft-deactivate instead of hard-deleting a user, so historical
        # transactions/payments keep a valid foreign key to them.
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
