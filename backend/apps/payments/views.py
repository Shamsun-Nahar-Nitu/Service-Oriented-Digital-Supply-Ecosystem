from django.http import JsonResponse
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer
from .services import SSLCommerzError, SSLCommerzService


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    /api/v1/payments/

    Customers initiate a payment against their own transaction; admins and
    managers can see every payment. Gateway callbacks control payment status.
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

    def perform_create(self, serializer):
        payment = serializer.save(amount=serializer.validated_data["transaction"].total_amount)
        if payment.method == Payment.Method.COD:
            self.gateway_payload = {}
            return
        try:
            self.gateway_payload = SSLCommerzService().create_session(payment)
        except SSLCommerzError as exc:
            payment.mark_failed()
            raise serializers.ValidationError({"gateway": str(exc)}) from exc

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        payment = serializer.instance
        data = PaymentSerializer(payment).data
        if payment.method != Payment.Method.COD:
            data["gateway_url"] = self.gateway_payload.get("GatewayPageURL")
        return Response(data, status=status.HTTP_201_CREATED)


class SSLCommerzCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, callback_type):
        return self.post(request, callback_type)

    def post(self, request, callback_type):
        transaction_id = request.data.get("tran_id", "")
        try:
            payment = Payment.objects.get(gateway_transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return JsonResponse({"detail": "Payment not found."}, status=404)

        if callback_type in ("fail", "cancel"):
            payment.mark_failed()
            return JsonResponse({"status": payment.status})

        try:
            payload = SSLCommerzService().validate_transaction(
                transaction_id, request.data.get("val_id", "")
            )
        except SSLCommerzError:
            payment.mark_failed()
            return JsonResponse({"status": Payment.Status.FAILED}, status=400)

        if not SSLCommerzService.is_valid_payment(payload, payment):
            payment.mark_failed()
            return JsonResponse({"status": Payment.Status.FAILED}, status=400)

        payment.mark_successful(
            gateway_reference=payload.get("tran_id", transaction_id),
            validation_id=payload.get("val_id", request.data.get("val_id", "")),
            bank_transaction_id=payload.get("bank_tran_id", ""),
        )
        return JsonResponse({"status": Payment.Status.SUCCESS})
