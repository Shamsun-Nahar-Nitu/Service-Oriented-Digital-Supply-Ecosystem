from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentConfirmSerializer, PaymentSerializer


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    /api/v1/payments/

    Customers initiate a payment against their own transaction; admins and
    managers can see every payment. There is no separate gateway integrated
    here — `confirm` simulates the webhook a real provider (Stripe,
    Razorpay, etc.) would send, which is where that integration would plug in.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "method"]

    def get_queryset(self):
        queryset = Payment.objects.select_related("transaction", "transaction__user")

        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return queryset.none()

        user = self.request.user
        if user.role in (user.Role.ADMIN, user.Role.MANAGER):
            return queryset
        return queryset.filter(transaction__user=user)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """POST /api/v1/payments/{id}/confirm/ — simulate a gateway success/failure callback."""
        payment = self.get_object()
        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["success"]:
            payment.mark_successful(
                gateway_reference=serializer.validated_data.get("gateway_reference", "")
            )
        else:
            payment.mark_failed()

        return Response(PaymentSerializer(payment).data)
