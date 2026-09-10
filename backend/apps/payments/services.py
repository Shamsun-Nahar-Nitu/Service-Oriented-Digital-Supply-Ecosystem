import uuid
from decimal import Decimal

import requests
from django.conf import settings


class SSLCommerzError(Exception):
    """Raised when SSLCommerz cannot create or validate a payment."""


class SSLCommerzService:
    gateway = "SSLCOMMERZ"

    def __init__(self):
        if not settings.SSLCOMMERZ_STORE_ID or not settings.SSLCOMMERZ_STORE_PASSWORD:
            raise SSLCommerzError("SSLCOMMERZ credentials are not configured.")
        self.base_url = settings.SSLCOMMERZ_BASE_URL.rstrip("/")

    def _post(self, path, data):
        try:
            response = requests.post(f"{self.base_url}{path}", data=data, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SSLCommerzError("Unable to communicate with SSLCOMMERZ.") from exc
        if payload.get("status") not in ("SUCCESS", "VALID", "VALIDATED"):
            raise SSLCommerzError(payload.get("failedreason", "SSLCOMMERZ rejected the request."))
        return payload

    def create_session(self, payment):
        transaction_id = f"TXN-{payment.transaction.transaction_number}-{uuid.uuid4().hex[:8]}"
        payload = self._post(
            "/gwprocess/v4/api.php",
            {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "total_amount": str(payment.amount),
                "currency": settings.CURRENCY_CODE,
                "tran_id": transaction_id,
                "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
                "fail_url": settings.SSLCOMMERZ_FAIL_URL,
                "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
                "ipn_url": settings.SSLCOMMERZ_IPN_URL,
                "cus_name": payment.transaction.user.full_name or payment.transaction.user.email,
                "cus_email": payment.transaction.user.email,
                "shipping_method": "YES",
                "product_name": "E-commerce order",
                "product_category": "General",
                "product_profile": "general",
            },
        )
        payment.gateway_transaction_id = transaction_id
        payment.session_key = payload.get("sessionkey", "")
        payment.gateway_reference = transaction_id
        payment.save(update_fields=["gateway_transaction_id", "session_key", "gateway_reference", "updated_date"])
        return payload

    def validate_transaction(self, transaction_id, validation_id=""):
        if validation_id:
            path = "/validator/api/validationserverAPI.php"
            data = {"val_id": validation_id}
        else:
            path = "/validator/api/merchantTransIDvalidationAPI.php"
            data = {"tran_id": transaction_id}
        data.update(
            {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "format": "json",
            }
        )
        return self._post(path, data)

    @staticmethod
    def is_valid_payment(payload, payment):
        try:
            amount_matches = Decimal(str(payload.get("amount", "0"))) == payment.amount
        except (ArithmeticError, ValueError):
            amount_matches = False
        return (
            payload.get("status") in ("VALID", "VALIDATED")
            and payload.get("tran_id") == payment.gateway_transaction_id
            and payload.get("currency") == payment.currency
            and amount_matches
        )
