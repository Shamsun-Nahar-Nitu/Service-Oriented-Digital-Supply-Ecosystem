from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.products.models import Product
from apps.transactions.services import CheckoutService
from apps.users.models import User


class PaymentSecurityTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            email="vendor@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.customer = User.objects.create_user(
            email="customer@example.com", password="pass12345", role=User.Role.CUSTOMER
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
        self.assertEqual(response.data["amount"], "900.00")
        self.assertEqual(response.data["status"], "PENDING")

        confirm_response = self.client.post(
            reverse("payments:payment-detail", args=[response.data["id"]]) + "confirm/",
            {"success": True},
            format="json",
        )
        self.assertEqual(confirm_response.status_code, status.HTTP_404_NOT_FOUND)
