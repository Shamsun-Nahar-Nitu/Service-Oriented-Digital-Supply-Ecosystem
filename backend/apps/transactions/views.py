from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrManager, IsOwnerOrStaff

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Orders. Customers create orders and only ever see their own; admins and
    managers see and can manage all orders. There is no hard delete - use
    the `cancel` action instead so the audit trail is preserved.
    """

    queryset = Transaction.objects.select_related("user").prefetch_related(
        "items", "items__product"
    )
    serializer_class = TransactionSerializer
    permission_classes = [IsOwnerOrStaff]
    filterset_fields = ["status", "user"]
    search_fields = ["transaction_number", "user__email"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not (user.is_admin or user.is_manager):
            qs = qs.filter(user=user)
        return qs

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return [IsAdminOrManager()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """POST /api/v1/transactions/{id}/cancel/ - restores stock."""
        txn = self.get_object()
        if txn.status in (Transaction.Status.CANCELLED, Transaction.Status.DELIVERED):
            return Response(
                {"detail": f"Cannot cancel a transaction that is already {txn.status}."},
                status=400,
            )
        for item in txn.items.select_related("product__inventory"):
            item.product.inventory.restock(item.quantity, user=request.user)
        txn.status = Transaction.Status.CANCELLED
        txn.save(update_fields=["status", "updated_at"])
        return Response(TransactionSerializer(txn).data)
