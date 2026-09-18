from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.products.models import Product
from apps.transactions.models import Transaction
from apps.transactions.services import CheckoutService
from apps.users.models import User


class CheckoutServiceTests(APITestCase):
    """Unit tests for the CheckoutService business logic, bypassing the HTTP layer."""

    def setUp(self):
        self.vendor = User.objects.create_user(
            email="vendor@example.com",
            password="pass12345",
            first_name="Val",
            role=User.Role.VENDOR,
        )
        self.customer = User.objects.create_user(
            email="buyer@example.com",
            password="pass12345",
            first_name="Bea",
            role=User.Role.CUSTOMER,
        )
        self.category = Category.objects.create(name="Books")
        self.product = Product.objects.create(
            product_name="Django for APIs",
            sku="BOOK-1",
            category=self.category,
            vendor=self.vendor,
            mrp=Decimal("1000.00"),
            discount_percentage=Decimal("20.00"),
        )
        self.product.inventory.quantity_in_stock = 10
        self.product.inventory.save()

    def test_successful_checkout_decrements_stock_and_computes_total(self):
        service = CheckoutService(
            user=self.customer,
            items=[{"product": self.product, "quantity": 3}],
            shipping_address="1 Test Street",
        )
        transaction_obj = service.execute()

        self.product.inventory.refresh_from_db()
        self.assertEqual(self.product.inventory.quantity_in_stock, 7)
        # selling_price = 1000 - 20% = 800; 3 units = 2400 item subtotal,
        # plus the 1% platform fee the customer pays on top (24.00) = 2424 total.
        self.assertEqual(transaction_obj.items_subtotal, Decimal("2400.00"))
        self.assertEqual(transaction_obj.platform_fee, Decimal("24.00"))
        self.assertEqual(transaction_obj.total_amount, Decimal("2424.00"))
        self.assertEqual(transaction_obj.items.count(), 1)

    def test_checkout_fails_when_stock_insufficient(self):
        service = CheckoutService(
            user=self.customer, items=[{"product": self.product, "quantity": 999}]
        )

        with self.assertRaises(ValidationError):
            service.execute()

        # Stock must be untouched after the rollback.
        self.product.inventory.refresh_from_db()
        self.assertEqual(self.product.inventory.quantity_in_stock, 10)


class TransactionAPITests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            email="vendor2@example.com",
            password="pass12345",
            first_name="Val",
            role=User.Role.VENDOR,
        )
        self.customer = User.objects.create_user(
            email="buyer2@example.com",
            password="pass12345",
            first_name="Bea",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="other@example.com",
            password="pass12345",
            first_name="Otto",
            role=User.Role.CUSTOMER,
        )
        self.category = Category.objects.create(name="Gadgets")
        self.product = Product.objects.create(
            product_name="USB Cable",
            sku="CBL-1",
            category=self.category,
            vendor=self.vendor,
            mrp=Decimal("500.00"),
        )
        self.product.inventory.quantity_in_stock = 5
        self.product.inventory.save()

    def test_checkout_endpoint_creates_order(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("transactions:transaction-checkout"),
            {"items": [{"product": self.product.id, "quantity": 1}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_customer_cannot_see_others_orders(self):
        self.client.force_authenticate(self.customer)
        self.client.post(
            reverse("transactions:transaction-checkout"),
            {"items": [{"product": self.product.id, "quantity": 1}]},
            format="json",
        )

        self.client.force_authenticate(self.other_customer)
        response = self.client.get(reverse("transactions:transaction-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_only_pending_orders_can_be_cancelled(self):
        self.client.force_authenticate(self.customer)
        checkout_response = self.client.post(
            reverse("transactions:transaction-checkout"),
            {"items": [{"product": self.product.id, "quantity": 1}]},
            format="json",
        )
        transaction_id = checkout_response.data["id"]

        cancel_response = self.client.post(
            reverse("transactions:transaction-cancel", args=[transaction_id])
        )
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_response.data["status"], Transaction.Status.CANCELLED)

        second_cancel = self.client.post(
            reverse("transactions:transaction-cancel", args=[transaction_id])
        )
        self.assertEqual(second_cancel.status_code, status.HTTP_400_BAD_REQUEST)