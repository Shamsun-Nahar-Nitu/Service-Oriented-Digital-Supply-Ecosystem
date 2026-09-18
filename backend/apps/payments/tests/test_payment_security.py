from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.payments.models import Payment
from apps.payments.services import SSLCommerzService
from apps.products.models import Product
from apps.transactions.services import CheckoutService
from apps.users.models import User


class PaymentSecurityTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            email="vendor@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="pass12345",
            first_name="Customer",
            role=User.Role.CUSTOMER,
            address="Customer saved address",
            phone_number="01700000000",
        )
        category = Category.objects.create(name="Payment products")
        product = Product.objects.create(
            product_name="Payment product",
            sku="PAY-1",
            category=category,
            vendor=self.vendor,
            mrp=Decimal("1000.00"),
            discount_percentage=Decimal("10.00"),
        )
        product.inventory.quantity_in_stock = 2
        product.inventory.save()
        self.order = CheckoutService(
            self.customer, [{"product": product, "quantity": 1}]
        ).execute()

    def create_order(self, user=None):
        user = user or self.customer
        product = Product.objects.create(
            product_name="Another payment product",
            sku=f"PAY-{Product.objects.count() + 1}",
            category=self.order.items.first().product.category,
            vendor=self.vendor,
            mrp=Decimal("500.00"),
            discount_percentage=Decimal("0.00"),
        )
        product.inventory.quantity_in_stock = 2
        product.inventory.save()
        return CheckoutService(user, [{"product": product, "quantity": 1}]).execute()

    @staticmethod
    def gateway_response(payload):
        response = Mock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        return response

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_online_payment_uses_bdt_backend_amount(self, post):
        post.return_value = self.gateway_response(
            {"status": "SUCCESS", "GatewayPageURL": "https://sandbox.example/pay"}
        )
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("payments:payment-list"),
            {"transaction": self.order.id, "method": "ONLINE", "amount": "1.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], "909.00")
        self.assertEqual(response.data["currency"], "BDT")
        self.assertEqual(response.data["method"], "ONLINE")
        self.assertEqual(post.call_args.kwargs["data"]["total_amount"], "909.00")
        self.assertEqual(post.call_args.kwargs["data"]["currency"], "BDT")
        payload = post.call_args.kwargs["data"]
        self.assertEqual(payload["store_id"], "test-store")
        self.assertEqual(payload["store_passwd"], "test-password")
        self.assertEqual(payload["tran_id"][:4], "TXN-")
        self.assertLessEqual(len(payload["tran_id"]), 30)
        self.assertEqual(payload["success_url"], "http://localhost/success")
        self.assertEqual(payload["fail_url"], "http://localhost/fail")
        self.assertEqual(payload["cancel_url"], "http://localhost/cancel")
        self.assertEqual(payload["ipn_url"], "http://localhost/ipn")
        self.assertEqual(payload["cus_name"], self.customer.full_name)
        self.assertEqual(payload["cus_email"], self.customer.email)
        self.assertEqual(payload["cus_add1"], "Customer saved address")
        self.assertEqual(payload["cus_city"], "N/A")
        self.assertEqual(payload["cus_state"], "N/A")
        self.assertEqual(payload["cus_postcode"], "N/A")
        self.assertEqual(payload["cus_country"], "Bangladesh")
        self.assertEqual(payload["cus_phone"], "01700000000")
        self.assertEqual(payload["shipping_method"], "NO")
        self.assertEqual(payload["num_of_item"], 1)
        self.assertEqual(payload["product_name"], "Payment product")
        self.assertEqual(payload["product_category"], "Payment products")
        self.assertEqual(payload["product_profile"], "physical-goods")

    def test_online_payment_requires_customer_phone(self):
        self.customer.phone_number = ""
        self.customer.save(update_fields=["phone_number"])
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("payments:payment-list"),
            {"transaction": self.order.id, "method": "ONLINE"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone number is required", str(response.data).lower())

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_online_payload_prefers_transaction_shipping_address(self, post):
        post.return_value = self.gateway_response(
            {"status": "SUCCESS", "GatewayPageURL": "https://sandbox.example/pay"}
        )
        self.order.shipping_address = "Checkout delivery address"
        self.order.save(update_fields=["shipping_address"])
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.ONLINE,
            amount=self.order.total_amount,
            currency="BDT",
        )

        SSLCommerzService().create_session(payment)

        self.assertEqual(
            post.call_args.kwargs["data"]["cus_add1"], "Checkout delivery address"
        )

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_online_payload_uses_safe_address_fallback_when_addresses_are_blank(self, post):
        post.return_value = self.gateway_response(
            {"status": "SUCCESS", "GatewayPageURL": "https://sandbox.example/pay"}
        )
        self.order.shipping_address = ""
        self.customer.address = ""
        self.order.save(update_fields=["shipping_address"])
        self.customer.save(update_fields=["address"])
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.ONLINE,
            amount=self.order.total_amount,
            currency="BDT",
        )

        SSLCommerzService().create_session(payment)

        self.assertEqual(post.call_args.kwargs["data"]["cus_add1"], "N/A")

    @patch("apps.payments.views.SSLCommerzService.create_session")
    def test_cod_creation_does_not_call_gateway(self, create_session):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("payments:payment-list"),
            {"transaction": self.order.id, "method": "COD"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")
        create_session.assert_not_called()

    def test_customer_cannot_create_payment_for_another_customer(self):
        other_customer = User.objects.create_user(
            email="other@example.com", password="pass12345", role=User.Role.CUSTOMER
        )
        other_order = self.create_order(other_customer)
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("payments:payment-list"),
            {"transaction": other_order.id, "method": "COD"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_validation_rejects_amount_and_currency_mismatch(self, post):
        for suffix, payload in (
            ("amount", {"amount": "899.99", "currency": "BDT"}),
            ("currency", {"amount": "900.00", "currency": "USD"}),
        ):
            with self.subTest(suffix=suffix):
                payment = Payment.objects.create(
                    transaction=self.create_order(),
                    method=Payment.Method.ONLINE,
                    amount=Decimal("900.00"),
                    currency="BDT",
                    gateway_transaction_id=f"gateway-{suffix}",
                )
                post.return_value = self.gateway_response(
                    {
                        "status": "VALID",
                        "tran_id": payment.gateway_transaction_id,
                        "val_id": f"validation-{suffix}",
                        **payload,
                    }
                )
                response = self.client.post(
                    reverse("payments:callback", args=["ipn"]),
                    {
                        "tran_id": payment.gateway_transaction_id,
                        "val_id": f"validation-{suffix}",
                    },
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                payment.refresh_from_db()
                self.assertEqual(payment.status, Payment.Status.FAILED)

    def test_customer_cannot_collect_cod(self):
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.COD,
            amount=self.order.total_amount,
            currency="BDT",
        )
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("payments:payment-mark-cod-collected", args=[payment.id]), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_and_admin_can_collect_cod(self):
        manager = User.objects.create_user(
            email="manager@example.com", password="pass12345", role=User.Role.MANAGER
        )
        admin = User.objects.create_user(
            email="admin@example.com", password="pass12345", role=User.Role.ADMIN
        )
        manager_payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.COD,
            amount=self.order.total_amount,
            currency="BDT",
        )
        self.client.force_authenticate(manager)
        manager_response = self.client.post(
            reverse("payments:payment-mark-cod-collected", args=[manager_payment.id]),
            format="json",
        )
        self.assertEqual(manager_response.status_code, status.HTTP_200_OK)
        self.assertEqual(manager_response.data["status"], "SUCCESS")

        admin_order = self.create_order()
        admin_payment = Payment.objects.create(
            transaction=admin_order,
            method=Payment.Method.COD,
            amount=admin_order.total_amount,
            currency="BDT",
        )
        self.client.force_authenticate(admin)
        admin_response = self.client.post(
            reverse("payments:payment-mark-cod-collected", args=[admin_payment.id]),
            format="json",
        )
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data["status"], "SUCCESS")

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_success_callback_requires_validated_amount_and_currency(self, post):
        post.return_value = self.gateway_response(
            {
                "status": "VALID",
                "tran_id": "wrong-id",
                "val_id": "validation-1",
                "amount": "900.00",
                "currency": "BDT",
            }
        )
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.ONLINE,
            amount=self.order.total_amount,
            currency="BDT",
            gateway_transaction_id="gateway-1",
        )

        response = self.client.post(
            reverse("payments:callback", args=["success"]),
            {"tran_id": payment.gateway_transaction_id, "val_id": "validation-1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.FAILED)
        self.assertEqual(payment.transaction.status, "PENDING")

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store", SSLCOMMERZ_STORE_PASSWORD="test-password"
    )
    @patch("apps.payments.services.requests.post")
    def test_successful_validation_and_duplicate_ipn_are_idempotent(self, post):
        post.return_value = self.gateway_response(
            {
                "status": "VALID",
                "tran_id": "gateway-1",
                "val_id": "validation-1",
                "bank_tran_id": "bank-1",
                "amount": "909.00",
                "currency": "BDT",
            }
        )
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.ONLINE,
            amount=self.order.total_amount,
            currency="BDT",
            gateway_transaction_id="gateway-1",
        )
        callback = reverse("payments:callback", args=["ipn"])

        first_response = self.client.post(
            callback, {"tran_id": "gateway-1", "val_id": "validation-1"}, format="json"
        )
        second_response = self.client.post(
            callback, {"tran_id": "gateway-1", "val_id": "validation-1"}, format="json"
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.call_count, 1)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(payment.transaction.status, "CONFIRMED")

    @override_settings(
        SSLCOMMERZ_STORE_ID="test-store",
        SSLCOMMERZ_STORE_PASSWORD="test-password",
        SSLCOMMERZ_SUCCESS_URL="http://localhost/success",
        SSLCOMMERZ_FAIL_URL="http://localhost/fail",
        SSLCOMMERZ_CANCEL_URL="http://localhost/cancel",
        SSLCOMMERZ_IPN_URL="http://localhost/ipn",
    )
    @patch("apps.payments.services.requests.post")
    def test_failed_online_payment_can_retry_without_new_payment_row(self, post):
        post.return_value = self.gateway_response(
            {"status": "SUCCESS", "GatewayPageURL": "https://sandbox.example/retry"}
        )
        payment = Payment.objects.create(
            transaction=self.order,
            method=Payment.Method.ONLINE,
            status=Payment.Status.FAILED,
            amount=self.order.total_amount,
            currency="BDT",
        )
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("payments:payment-retry", args=[payment.id]), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(Payment.objects.filter(transaction=self.order).count(), 1)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(response.data["gateway_url"], "https://sandbox.example/retry")

    def test_anonymous_payment_creation_is_rejected(self):
        response = self.client.post(
            reverse("payments:payment-list"), {"transaction": self.order.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_amount_comes_from_order_and_confirm_is_removed(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("payments:payment-list"),
            {"transaction": self.order.id, "method": "COD", "amount": "1.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], "909.00")
        self.assertEqual(response.data["status"], "PENDING")

        confirm_response = self.client.post(
            reverse("payments:payment-detail", args=[response.data["id"]]) + "confirm/",
            {"success": True},
            format="json",
        )
        self.assertEqual(confirm_response.status_code, status.HTTP_404_NOT_FOUND)