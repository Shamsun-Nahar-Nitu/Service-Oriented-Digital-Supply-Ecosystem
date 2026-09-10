from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.products.models import Product
from apps.users.models import User


class CatalogAccessTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            email="vendor@example.com",
            password="pass12345",
            role=User.Role.VENDOR,
        )
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="pass12345",
            role=User.Role.CUSTOMER,
        )
        self.category = Category.objects.create(name="Catalog")
        self.product = Product.objects.create(
            product_name="Public product",
            sku="PUBLIC-1",
            category=self.category,
            vendor=self.vendor,
            mrp=Decimal("1000.00"),
        )
        self.hidden = Product.objects.create(
            product_name="Hidden product",
            sku="HIDDEN-1",
            category=self.category,
            vendor=self.vendor,
            mrp=Decimal("2000.00"),
            is_active=False,
        )

    def test_anonymous_users_can_browse_public_catalog(self):
        list_response = self.client.get(reverse("products:product-list"))
        detail_response = self.client.get(
            reverse("products:product-detail", args=[self.product.id])
        )
        category_response = self.client.get(reverse("category:category-list"))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(category_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)

    def test_customer_cannot_create_product(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("products:product-list"),
            {
                "product_name": "Not allowed",
                "sku": "NO-1",
                "category": self.category.id,
                "vendor": self.vendor.id,
                "mrp": "100.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_vendor_cannot_update_another_vendors_product(self):
        other_vendor = User.objects.create_user(
            email="other-vendor@example.com",
            password="pass12345",
            role=User.Role.VENDOR,
        )
        self.product.vendor = other_vendor
        self.product.save(update_fields=["vendor"])
        self.client.force_authenticate(self.vendor)

        response = self.client.patch(
            reverse("products:product-detail", args=[self.product.id]),
            {"product_name": "Tampered"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
