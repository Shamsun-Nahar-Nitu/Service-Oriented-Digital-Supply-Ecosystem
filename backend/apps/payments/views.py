from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction as db_transaction
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
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

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        payment = self.get_object()
        if payment.transaction.user_id != request.user.id:
            raise PermissionDenied("Only the customer who placed the order can retry payment.")
        if payment.method != Payment.Method.ONLINE:
            return Response(
                {"detail": "Only failed online payments can be retried."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment.status != Payment.Status.FAILED:
            return Response(
                {"detail": "Only failed payments can be retried."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = Payment.Status.PENDING
        payment.amount = payment.transaction.total_amount
        payment.currency = "BDT"
        payment.gateway_transaction_id = ""
        payment.session_key = ""
        payment.save(
            update_fields=[
                "status",
                "amount",
                "currency",
                "gateway_transaction_id",
                "session_key",
                "updated_date",
            ]
        )
        try:
            gateway_payload = SSLCommerzService().create_session(payment)
        except SSLCommerzError as exc:
            payment.mark_failed()
            raise serializers.ValidationError({"gateway": str(exc)}) from exc

        data = PaymentSerializer(payment).data
        data["gateway_url"] = gateway_payload.get("GatewayPageURL")
        return Response(data)

    @action(detail=True, methods=["post"])
    def mark_cod_collected(self, request, pk=None):
        user = request.user
        if user.role not in (user.Role.ADMIN, user.Role.MANAGER):
            raise PermissionDenied("Only admin or manager users can collect COD payments.")
        payment = self.get_object()
        if payment.method != Payment.Method.COD:
            return Response(
                {"detail": "Only COD payments can be collected this way."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment.status != Payment.Status.PENDING:
            return Response(
                {"detail": "Only pending COD payments can be collected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment.mark_successful()
        return Response(PaymentSerializer(payment).data)


class SSLCommerzCallbackView(APIView):
    """
    Handles all four SSLCOMMERZ callback URLs.

    `ipn` is server-to-server — SSLCOMMERZ's backend calls it directly, no
    human ever sees the response, so it keeps returning plain JSON exactly
    as before.

    `success` / `fail` / `cancel` are different: SSLCOMMERZ redirects the
    *customer's browser* to these URLs after they leave the gateway. This
    view still does the same validation work for them, but the response
    they end in is an HTTP redirect to the frontend's existing
    PaymentResultPage (/payment/success, /payment/fail, /payment/cancel)
    rather than raw JSON — a customer should see a normal page here, not an
    API response.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    BROWSER_CALLBACK_PATHS = {
        "success": "/payment/success",
        "fail": "/payment/fail",
        "cancel": "/payment/cancel",
    }

    def get(self, request, callback_type):
        return self.post(request, callback_type)

    def post(self, request, callback_type):
        if callback_type not in ("success", "fail", "cancel", "ipn"):
            return JsonResponse({"detail": "Unsupported callback."}, status=404)

        is_browser_callback = callback_type != "ipn"
        transaction_id = request.data.get("tran_id", "")

        with db_transaction.atomic():
            try:
                payment = Payment.objects.select_for_update().get(
                    gateway_transaction_id=transaction_id
                )
            except Payment.DoesNotExist:
                if is_browser_callback:
                    return self._redirect_to_frontend("fail")
                return JsonResponse({"detail": "Payment not found."}, status=404)

            if payment.status == Payment.Status.SUCCESS:
                return self._respond(is_browser_callback, "success", payment)

            if callback_type in ("fail", "cancel"):
                payment.mark_failed()
                return self._respond(is_browser_callback, callback_type, payment)

            try:
                payload = SSLCommerzService().validate_transaction(
                    transaction_id, request.data.get("val_id", "")
                )
            except SSLCommerzError:
                payment.mark_failed()
                return self._respond(is_browser_callback, "fail", payment)

            if not SSLCommerzService.is_valid_payment(payload, payment):
                payment.mark_failed()
                return self._respond(is_browser_callback, "fail", payment)

            payment.mark_successful(
                gateway_reference=payload.get("tran_id", transaction_id),
                validation_id=payload.get("val_id", request.data.get("val_id", "")),
                bank_transaction_id=payload.get("bank_tran_id", ""),
            )
            return self._respond(is_browser_callback, "success", payment)

    def _respond(self, is_browser_callback, outcome, payment):
        """outcome is one of 'success' / 'fail' / 'cancel' — used both as
        the JSON status key (for ipn) and to pick which frontend page to
        redirect to (for a human's browser)."""
        if is_browser_callback:
            return self._redirect_to_frontend(outcome, payment)
        json_status = Payment.Status.SUCCESS if outcome == "success" else Payment.Status.FAILED
        http_status = 200 if outcome == "success" else 400
        return JsonResponse({"status": json_status}, status=http_status)

    def _redirect_to_frontend(self, outcome, payment=None):
        path = self.BROWSER_CALLBACK_PATHS[outcome]
        query = {"payment_id": payment.id} if payment is not None else {}
        url = f"{settings.FRONTEND_BASE_URL}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return HttpResponseRedirect(url)