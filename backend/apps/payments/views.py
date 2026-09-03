from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrManager

from .models import Payment
from .permissions import IsTransactionOwnerOrStaff
from .serializers import PaymentSerializer


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Customers initiate a payment for their own transaction (status starts as
    `pending`). Marking a payment success/failed/refunded is a staff-only
    action - in a real deployment this would instead be driven by a payment
    gateway webhook, but the manual endpoints keep this testable without one.
    """

    queryset = Payment.objects.select_related("transaction", "transaction__user")
    serializer_class = PaymentSerializer
    permission_classes = [IsTransactionOwnerOrStaff]
    filterset_fields = ["status", "method"]
    ordering_fields = ["created_at", "amount"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not (user.is_admin or user.is_manager):
            qs = qs.filter(transaction__user=user)
        return qs

    def get_permissions(self):
        if self.action in ("mark_success", "mark_failed", "mark_refunded"):
            return [IsAdminOrManager()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def mark_success(self, request, pk=None):
        payment = self.get_object()
        payment.mark_success()
        payment.transaction.status = payment.transaction.Status.CONFIRMED
        payment.transaction.save(update_fields=["status", "updated_at"])
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"])
    def mark_failed(self, request, pk=None):
        payment = self.get_object()
        payment.mark_failed()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"])
    def mark_refunded(self, request, pk=None):
        payment = self.get_object()
        payment.status = payment.Status.REFUNDED
        payment.save(update_fields=["status", "updated_at"])
        payment.transaction.status = payment.transaction.Status.REFUNDED
        payment.transaction.save(update_fields=["status", "updated_at"])
        return Response(PaymentSerializer(payment).data)
