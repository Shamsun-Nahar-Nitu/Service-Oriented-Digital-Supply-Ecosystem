"""
Platform-wide constants that more than one app needs to agree on.

The commission rates live here rather than in `apps.transactions` or
`apps.finance` specifically, because both apps need the same numbers and
neither should have to import the other just to get them — `apps.transactions`
uses PLATFORM_CUSTOMER_FEE_RATE when it computes what a customer owes at
checkout, and `apps.finance` uses both rates when it books a vendor's
commission after payment. `apps.core` already sits underneath every other
app (see models.py, permissions.py), so it's the natural home for a value
every app can see without creating a cycle.
"""

from decimal import Decimal

# Business rule: the platform earns 1% from the customer and 1% from the
# vendor on every paid order.
#
# - PLATFORM_CUSTOMER_FEE_RATE is added on top of the item subtotal at
#   checkout (Transaction.recalculate_total) — it is real money the customer
#   pays in addition to the products themselves, the same way a booking fee
#   or service charge works elsewhere.
# - PLATFORM_VENDOR_COMMISSION_RATE is deducted from what the platform owes
#   the vendor for the sale (apps.finance.models.VendorCommission) — the
#   vendor never sees this money; it is subtracted before payout.
#
# Both are 1% today, kept as two separate names (not one shared constant)
# because they are conceptually different fees that could diverge in the
# future — e.g. a promotional period that waives the buyer fee but keeps
# the seller commission.
PLATFORM_CUSTOMER_FEE_RATE = Decimal("0.01")
PLATFORM_VENDOR_COMMISSION_RATE = Decimal("0.01")