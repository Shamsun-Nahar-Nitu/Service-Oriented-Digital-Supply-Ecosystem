"""
Books the platform's commission the instant a payment turns SUCCESS.

This runs as a signal — the same pattern apps.inventory uses to create an
Inventory row when a Product is created — rather than as a line inside
Payment.mark_successful(), so apps.payments stays ignorant of commission
entirely. Payments knows how to take money; finance knows what the
platform's cut of that money is. Neither has to import the other's models
beyond what it already does (finance already depends on payments' Payment
model to point a ForeignKey at it).
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.constants import PLATFORM_CUSTOMER_FEE_RATE, PLATFORM_VENDOR_COMMISSION_RATE
from apps.payments.models import Payment

from .models import VendorCommission

TWO_PLACES = Decimal("0.01")


def _money(value):
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


@receiver(post_save, sender=Payment)
def create_vendor_commissions_on_success(sender, instance, **kwargs):
    """
    Fires on every Payment save, but only acts once a payment is SUCCESS.

    Safe to fire more than once: Payment.mark_successful() already no-ops
    on a payment that is already SUCCESS (so in practice this only ever
    runs once per payment), and get_or_create plus the (payment, vendor)
    unique constraint on VendorCommission make it impossible to create a
    duplicate row even if something else ever sets the status directly.
    """
    if instance.status != Payment.Status.SUCCESS:
        return

    transaction_obj = instance.transaction
    items = transaction_obj.items.select_related("product__vendor")

    vendor_gross: dict = {}
    for item in items:
        vendor = item.product.vendor
        vendor_gross[vendor] = vendor_gross.get(vendor, Decimal("0")) + item.subtotal

    if not vendor_gross:
        return  # Nothing to book — a transaction with no items shouldn't happen, but don't crash if it does.

    # items_subtotal is the pre-fee sum of everyone's items; falling back to
    # the sum we just computed keeps this correct even for a transaction
    # created before the items_subtotal field existed (see the backfill
    # migration in apps/transactions).
    order_subtotal = transaction_obj.items_subtotal or sum(vendor_gross.values(), start=Decimal("0"))
    order_fee = transaction_obj.platform_fee

    for vendor, gross in vendor_gross.items():
        commission_amount = _money(gross * PLATFORM_VENDOR_COMMISSION_RATE)
        payable_amount = gross - commission_amount

        if order_subtotal > 0:
            fee_share = _money(order_fee * (gross / order_subtotal))
        else:
            fee_share = Decimal("0.00")

        VendorCommission.objects.get_or_create(
            payment=instance,
            vendor=vendor,
            defaults={
                "transaction": transaction_obj,
                "vendor_gross_amount": gross,
                "vendor_commission_rate": PLATFORM_VENDOR_COMMISSION_RATE,
                "vendor_commission_amount": commission_amount,
                "vendor_payable_amount": payable_amount,
                "customer_fee_rate": PLATFORM_CUSTOMER_FEE_RATE,
                "customer_fee_share": fee_share,
                "platform_revenue_amount": commission_amount + fee_share,
            },
        )
