from django.db import models

from apps.core.constants import PLATFORM_CUSTOMER_FEE_RATE, PLATFORM_VENDOR_COMMISSION_RATE
from apps.core.models import TimeStampedModel
from apps.payments.models import Payment
from apps.transactions.models import Transaction
from apps.users.models import User


class VendorCommission(TimeStampedModel):
    """
    The platform's commission ledger — one row per vendor represented in a
    successfully paid transaction.

    A single transaction can hold products from several vendors at once
    (see Transaction's docstring in apps.transactions.models), so commission
    has to be booked per vendor, not per transaction: an order with items
    from two vendors produces two VendorCommission rows against the one
    Payment. Rows are created automatically — see signals.py, which listens
    for a Payment turning SUCCESS — and are never written to directly by a
    view; nothing here is user-editable.

    Every rate is stored alongside its resulting amount, not just referenced
    from apps.core.constants, so a future rate change never rewrites the
    economics of a historical order — this row is a permanent record of
    what applied at the time.

    Field meanings:
    - vendor_gross_amount: this vendor's share of the order's item
      subtotal (sum of their line items' subtotal, before any fee).
    - vendor_commission_amount: vendor_gross_amount × vendor_commission_rate
      — the platform's 1% cut, deducted from what the vendor is owed.
    - vendor_payable_amount: vendor_gross_amount − vendor_commission_amount
      — what the platform actually owes this vendor for this order.
    - customer_fee_share: this vendor's proportional slice of the order's
      Transaction.platform_fee (the 1% the customer paid), allocated by
      each vendor's share of the order subtotal. A single-vendor order
      gives that vendor the whole fee; a mixed order splits it.
    - platform_revenue_amount: vendor_commission_amount + customer_fee_share
      — total platform earnings from this vendor's portion of this order.
    """

    payment = models.ForeignKey(
        Payment, related_name="vendor_commissions", on_delete=models.CASCADE
    )
    transaction = models.ForeignKey(
        Transaction, related_name="vendor_commissions", on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        User,
        related_name="commission_entries",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.VENDOR},
    )

    vendor_gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    vendor_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=PLATFORM_VENDOR_COMMISSION_RATE
    )
    vendor_commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    vendor_payable_amount = models.DecimalField(max_digits=12, decimal_places=2)

    customer_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=PLATFORM_CUSTOMER_FEE_RATE
    )
    customer_fee_share = models.DecimalField(max_digits=12, decimal_places=2)

    platform_revenue_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "vendor_commissions"
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "vendor"], name="unique_commission_per_payment_vendor"
            )
        ]
        indexes = [
            models.Index(fields=["vendor", "created_date"]),
        ]

    def __str__(self):
        return f"Commission for {self.vendor.email} on {self.transaction.transaction_number}"
