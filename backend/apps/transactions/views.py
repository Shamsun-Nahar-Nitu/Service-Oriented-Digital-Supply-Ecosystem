from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrManager

from .models import Transaction
from .serializers import (
    CheckoutSerializer,
    TransactionSerializer,
    TransactionStatusUpdateSerializer,
)


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    /api/v1/transactions/

    - Customers: see and create only their own orders (via `checkout`).
    - Vendors: see (read-only) any order that contains one of their products.
    - Admin/Manager: see every order and can update its status.
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status"]
    ordering_fields = ["created_date", "total_amount"]

    def get_queryset(self):
        queryset = Transaction.objects.prefetch_related("items__product").select_related("user")

        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return queryset.none()

        user = self.request.user
        if user.role in (user.Role.ADMIN, user.Role.MANAGER):
            return queryset
        if user.is_vendor:
            return queryset.filter(items__product__vendor=user).distinct()
        return queryset.filter(user=user)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """POST /api/v1/transactions/checkout/ — place an order from a cart payload."""
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        transaction_obj = serializer.save()
        return Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminOrManager])
    def update_status(self, request, pk=None):
        """PATCH /api/v1/transactions/{id}/update_status/ — admin/manager order lifecycle control."""
        transaction_obj = self.get_object()
        serializer = TransactionStatusUpdateSerializer(
            transaction_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TransactionSerializer(transaction_obj).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """POST /api/v1/transactions/{id}/cancel/ — a customer may cancel their own pending order."""
        transaction_obj = self.get_object()
        user = request.user
        if not (
            user.role in (user.Role.ADMIN, user.Role.MANAGER) or transaction_obj.user_id == user.id
        ):
            raise PermissionDenied("You can only cancel your own orders.")
        if transaction_obj.status != Transaction.Status.PENDING:
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        transaction_obj.status = Transaction.Status.CANCELLED
        transaction_obj.save(update_fields=["status", "updated_date"])
        return Response(TransactionSerializer(transaction_obj).data)
