from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.category.models import Category
from apps.payments.models import Payment
from apps.products.models import Product
from apps.transactions.services import CheckoutService
from apps.users.models import User


class DashboardPermissionTests(APITestCase):
    """Each dashboard is restricted to the roles that should see it —
    this is money and vendor/customer data, so the boundary matters as
    much as the numbers."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="pass12345", role=User.Role.ADMIN
        )
        self.manager = User.objects.create_user(
            email="manager@example.com", password="pass12345", role=User.Role.MANAGER
        )
        self.vendor = User.objects.create_user(
            email="vendor@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.customer = User.objects.create_user(
            email="customer@example.com", password="pass12345", role=User.Role.CUSTOMER
        )

    def test_admin_dashboard_is_admin_only(self):
        url = reverse("finance:dashboard-admin")

        self.client.force_authenticate(self.manager)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.vendor)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_manager_dashboard_allows_admin_and_manager_only(self):
        url = reverse("finance:dashboard-manager")

        self.client.force_authenticate(self.customer)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.manager)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_vendor_dashboard_is_vendor_only(self):
        url = reverse("finance:dashboard-vendor")

        self.client.force_authenticate(self.customer)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.vendor)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_anonymous_requests_are_rejected(self):
        for name in ("finance:dashboard-admin", "finance:dashboard-manager", "finance:dashboard-vendor"):
            response = self.client.get(reverse(name))
            self.assertIn(
                response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
            )


class DashboardNumbersTests(APITestCase):
    """One real paid order, checked end-to-end through the JSON dashboard
    response — not just the service function in isolation."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin2@example.com", password="pass12345", role=User.Role.ADMIN
        )
        self.vendor = User.objects.create_user(
            email="vendor2@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.customer = User.objects.create_user(
            email="customer2@example.com", password="pass12345", role=User.Role.CUSTOMER
        )
        category = Category.objects.create(name="Dashboard test products")
        product = Product.objects.create(
            product_name="Dashboard product",
            sku="DASH-1",
            category=category,
            vendor=self.vendor,
            mrp=Decimal("1000.00"),
            discount_percentage=Decimal("0.00"),
        )
        product.inventory.quantity_in_stock = 5
        product.inventory.save()

        order = CheckoutService(self.customer, [{"product": product, "quantity": 1}]).execute()
        payment = Payment.objects.create(
            transaction=order, method=Payment.Method.COD, amount=order.total_amount, currency="BDT"
        )
        payment.mark_successful()

    def test_admin_dashboard_reflects_the_paid_order(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("finance:dashboard-admin"), {"period": "all"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kpis = response.data["kpis"]
        self.assertEqual(Decimal(kpis["gross_revenue"]), Decimal("1010.00"))
        self.assertEqual(Decimal(kpis["platform_revenue"]), Decimal("20.00"))
        self.assertEqual(kpis["paid_orders"], 1)

    def test_vendor_dashboard_reflects_own_sale(self):
        self.client.force_authenticate(self.vendor)
        response = self.client.get(reverse("finance:dashboard-vendor"), {"period": "all"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kpis = response.data["kpis"]
        self.assertEqual(Decimal(kpis["gross_sales"]), Decimal("1000.00"))
        self.assertEqual(Decimal(kpis["net_payable"]), Decimal("990.00"))

    def test_admin_pdf_report_downloads(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse("finance:report-admin"), {"period": "all"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertGreater(len(response.content), 500)
