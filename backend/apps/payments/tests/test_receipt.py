from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.payments.models import Payment
from apps.products.models import Product
from apps.transactions.services import CheckoutService
from apps.users.models import User


class PaymentReceiptTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="receipt-buyer@example.com", password="pass12345", role=User.Role.CUSTOMER
        )
        self.other_customer = User.objects.create_user(
            email="receipt-other@example.com", password="pass12345", role=User.Role.CUSTOMER
        )
        self.admin = User.objects.create_user(
            email="receipt-admin@example.com", password="pass12345", role=User.Role.ADMIN
        )
        vendor = User.objects.create_user(
            email="receipt-vendor@example.com", password="pass12345", role=User.Role.VENDOR
        )
        category = Category.objects.create(name="Receipt test products")
        product = Product.objects.create(
            product_name="Receipt Test Product",
            sku="RCPT-1",
            category=category,
            vendor=vendor,
            mrp=Decimal("500.00"),
            discount_percentage=Decimal("0.00"),
        )
        product.inventory.quantity_in_stock = 10
        product.inventory.save()

        self.order = CheckoutService(
            self.customer, [{"product": product, "quantity": 2}], shipping_address="123 Test Road"
        ).execute()
        self.payment = Payment.objects.create(
            transaction=self.order, method=Payment.Method.COD, amount=self.order.total_amount, currency="BDT"
        )

    def _receipt_url(self):
        return reverse("payments:payment-receipt", args=[self.payment.id])

    def test_receipt_requires_successful_payment(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(self._receipt_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_download_receipt_after_success(self):
        self.payment.mark_successful()
        self.client.force_authenticate(self.customer)

        response = self.client.get(self._receipt_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertGreater(len(response.content), 500)

    def test_other_customer_cannot_download_receipt(self):
        self.payment.mark_successful()
        self.client.force_authenticate(self.other_customer)

        response = self.client.get(self._receipt_url())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_download_any_receipt(self):
        self.payment.mark_successful()
        self.client.force_authenticate(self.admin)

        response = self.client.get(self._receipt_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_anonymous_request_is_rejected(self):
        self.payment.mark_successful()
        response = self.client.get(self._receipt_url())
        self.assertIn(
            response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )