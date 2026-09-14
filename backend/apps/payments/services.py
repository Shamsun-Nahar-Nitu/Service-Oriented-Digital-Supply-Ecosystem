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
        transaction = payment.transaction
        user = transaction.user
        if not user.phone_number.strip():
            raise SSLCommerzError(
                "A phone number is required before starting an online payment."
            )
        if payment.currency != "BDT":
            raise SSLCommerzError("SSLCOMMERZ payments must use BDT currency.")
        required_urls = {
            "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
            "fail_url": settings.SSLCOMMERZ_FAIL_URL,
            "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
            "ipn_url": settings.SSLCOMMERZ_IPN_URL,
        }
        missing_urls = [name for name, value in required_urls.items() if not value]
        if missing_urls:
            raise SSLCommerzError(
                f"SSLCOMMERZ callback URLs are not configured: {', '.join(missing_urls)}."
            )

        transaction_id = f"TXN-{uuid.uuid4().hex[:26]}"
        customer_address = transaction.shipping_address.strip() or user.address.strip() or "N/A"
        product_names = ", ".join(
            item.product.product_name for item in transaction.items.select_related("product")
        )
        product_categories = ", ".join(
            item.product.category.name
            for item in transaction.items.select_related("product__category")
        )
        payload = self._post(
            "/gwprocess/v4/api.php",
            {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "total_amount": str(payment.amount),
                "currency": payment.currency,
                "tran_id": transaction_id,
                "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
                "fail_url": settings.SSLCOMMERZ_FAIL_URL,
                "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
                "ipn_url": settings.SSLCOMMERZ_IPN_URL,
                "cus_name": user.full_name or user.email,
                "cus_email": user.email,
                "cus_add1": customer_address,
                "cus_city": "N/A",
                "cus_state": "N/A",
                "cus_postcode": "N/A",
                "cus_country": "Bangladesh",
                "cus_phone": user.phone_number,
                "shipping_method": "NO",
                "num_of_item": transaction.items.count(),
                "product_name": product_names[:255],
                "product_category": product_categories[:100],
                "product_profile": "physical-goods",
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
            amount = Decimal(str(payload.get("amount", "0")))
        except (ArithmeticError, ValueError):
            return False
        amount_matches = amount == payment.amount == payment.transaction.total_amount
        return (
            payload.get("status") in ("VALID", "VALIDATED")
            and payload.get("tran_id") == payment.gateway_transaction_id
            and payload.get("currency", "").upper() == "BDT"
            and payment.currency == "BDT"
            and amount_matches
        )
