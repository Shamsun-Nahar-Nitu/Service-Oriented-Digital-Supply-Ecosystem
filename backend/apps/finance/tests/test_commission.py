from decimal import Decimal

from django.test import TestCase

from apps.category.models import Category
from apps.finance.models import VendorCommission
from apps.payments.models import Payment
from apps.products.models import Product
from apps.transactions.services import CheckoutService
from apps.users.models import User


class VendorCommissionTests(TestCase):
    """
    The money math that matters most in this feature: when a payment
    succeeds, does the platform book exactly 1% from the vendor and 1%
    (of the customer's fee) attributed back to that vendor — correctly,
    even when one order spans several vendors — and never more than once?
    """

    def setUp(self):
        self.customer = User.objects.create_user(
            email="buyer@example.com", password="pass12345", role=User.Role.CUSTOMER
        )
        self.vendor_a = User.objects.create_user(
            email="vendor-a@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.vendor_b = User.objects.create_user(
            email="vendor-b@example.com", password="pass12345", role=User.Role.VENDOR
        )
        self.category = Category.objects.create(name="Commission test products")

    def _make_product(self, vendor, mrp, discount, sku, stock=10):
        product = Product.objects.create(
            product_name=f"Product {sku}",
            sku=sku,
            category=self.category,
            vendor=vendor,
            mrp=Decimal(mrp),
            discount_percentage=Decimal(discount),
        )
        product.inventory.quantity_in_stock = stock
        product.inventory.save()
        return product

    def test_single_vendor_commission_amounts(self):
        """
        mrp=1000, discount=10% -> selling_price=900; qty=2 -> gross=1800.
        Customer fee (1% of order subtotal) = 18.00, all of it attributed
        to the one vendor since they're the only vendor on the order.
        Vendor commission = 1% of their own gross = 18.00.
        """
        product = self._make_product(self.vendor_a, "1000.00", "10.00", "SKU-A1")
        order = CheckoutService(self.customer, [{"product": product, "quantity": 2}]).execute()

        self.assertEqual(order.items_subtotal, Decimal("1800.00"))
        self.assertEqual(order.platform_fee, Decimal("18.00"))
        self.assertEqual(order.total_amount, Decimal("1818.00"))

        payment = Payment.objects.create(
            transaction=order, method=Payment.Method.COD, amount=order.total_amount, currency="BDT"
        )
        payment.mark_successful()

        commissions = VendorCommission.objects.filter(payment=payment)
        self.assertEqual(commissions.count(), 1)

        entry = commissions.get()
        self.assertEqual(entry.vendor, self.vendor_a)
        self.assertEqual(entry.vendor_gross_amount, Decimal("1800.00"))
        self.assertEqual(entry.vendor_commission_amount, Decimal("18.00"))
        self.assertEqual(entry.vendor_payable_amount, Decimal("1782.00"))
        self.assertEqual(entry.customer_fee_share, Decimal("18.00"))
        self.assertEqual(entry.platform_revenue_amount, Decimal("36.00"))

        # Sanity check the whole ledger balances against real money moved:
        # customer paid total_amount; vendor keeps payable; platform keeps
        # the rest, and nothing is created or destroyed.
        self.assertEqual(
            entry.vendor_payable_amount + entry.platform_revenue_amount, order.total_amount
        )

    def test_multi_vendor_order_splits_commission_proportionally(self):
        """
        Vendor A contributes 800 of a 1000 order subtotal (80%), vendor B
        contributes 200 (20%). The order-level 1% customer fee (10.00)
        should split 8.00 / 2.00 by that same 80/20 share, and each
        vendor's own 1% commission is computed on their own gross only.
        """
        product_a = self._make_product(self.vendor_a, "800.00", "0.00", "SKU-A2")
        product_b = self._make_product(self.vendor_b, "200.00", "0.00", "SKU-B1")
        order = CheckoutService(
            self.customer,
            [{"product": product_a, "quantity": 1}, {"product": product_b, "quantity": 1}],
        ).execute()

        self.assertEqual(order.items_subtotal, Decimal("1000.00"))
        self.assertEqual(order.platform_fee, Decimal("10.00"))
        self.assertEqual(order.total_amount, Decimal("1010.00"))

        payment = Payment.objects.create(
            transaction=order, method=Payment.Method.COD, amount=order.total_amount, currency="BDT"
        )
        payment.mark_successful()

        entries = {entry.vendor: entry for entry in VendorCommission.objects.filter(payment=payment)}
        self.assertEqual(len(entries), 2)

        entry_a = entries[self.vendor_a]
        self.assertEqual(entry_a.vendor_gross_amount, Decimal("800.00"))
        self.assertEqual(entry_a.vendor_commission_amount, Decimal("8.00"))
        self.assertEqual(entry_a.customer_fee_share, Decimal("8.00"))  # 80% of the 10.00 fee
        self.assertEqual(entry_a.vendor_payable_amount, Decimal("792.00"))

        entry_b = entries[self.vendor_b]
        self.assertEqual(entry_b.vendor_gross_amount, Decimal("200.00"))
        self.assertEqual(entry_b.vendor_commission_amount, Decimal("2.00"))
        self.assertEqual(entry_b.customer_fee_share, Decimal("2.00"))  # 20% of the 10.00 fee
        self.assertEqual(entry_b.vendor_payable_amount, Decimal("198.00"))

        # The two fee shares must add back up to the whole order fee — no
        # money should be lost or invented by splitting it across vendors.
        self.assertEqual(
            entry_a.customer_fee_share + entry_b.customer_fee_share, order.platform_fee
        )
        total_payable = entry_a.vendor_payable_amount + entry_b.vendor_payable_amount
        total_platform_revenue = entry_a.platform_revenue_amount + entry_b.platform_revenue_amount
        self.assertEqual(total_payable + total_platform_revenue, order.total_amount)

    def test_commission_is_not_duplicated_on_repeated_save(self):
        """mark_successful() already no-ops if status is already SUCCESS,
        but the (payment, vendor) unique constraint is a second, independent
        guard — this proves a duplicate row can't appear even if something
        else saves the payment again while it's already SUCCESS."""
        product = self._make_product(self.vendor_a, "500.00", "0.00", "SKU-A3")
        order = CheckoutService(self.customer, [{"product": product, "quantity": 1}]).execute()
        payment = Payment.objects.create(
            transaction=order, method=Payment.Method.COD, amount=order.total_amount, currency="BDT"
        )

        payment.mark_successful()
        payment.save()  # simulate an unrelated later save while already SUCCESS
        payment.save()

        self.assertEqual(VendorCommission.objects.filter(payment=payment).count(), 1)

    def test_pending_payment_books_no_commission(self):
        product = self._make_product(self.vendor_a, "500.00", "0.00", "SKU-A4")
        order = CheckoutService(self.customer, [{"product": product, "quantity": 1}]).execute()
        Payment.objects.create(
            transaction=order, method=Payment.Method.COD, amount=order.total_amount, currency="BDT"
        )

        self.assertEqual(VendorCommission.objects.count(), 0)
