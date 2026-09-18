"""
All dashboard aggregation logic in one place.

`DashboardAnalyticsService` builds three summaries — admin, manager, vendor
— from the same underlying tables (Transaction, Payment, VendorCommission,
Product, Inventory, User). Keeping them in one service, rather than writing
the queries directly in views.py, means apps/finance/reports.py (the PDF
builder) can call the exact same methods the JSON dashboards use, so the
numbers in a downloaded report can never drift from what the dashboard
showed when the person generated it.

Money in, money out:
- "Revenue" is always read from Payment (status=SUCCESS), never from
  Transaction.total_amount directly, because a transaction can exist
  without ever being paid (PENDING, CANCELLED). Payment.paid_at — not
  Transaction.created_date — is the date a sale actually counts, so a
  customer who orders on the 30th and pays on the 1st shows up in the new
  month's revenue, matching standard revenue-recognition practice.
- "Orders placed" (as opposed to "orders paid") is read from Transaction
  directly and uses Transaction.created_date, since an order that never
  got paid still happened and is often exactly what a manager wants to see
  (abandoned/failed checkouts).
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Prefetch, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from apps.inventory.models import Inventory
from apps.payments.models import Payment
from apps.products.models import Product
from apps.transactions.models import Transaction, TransactionItem
from apps.users.models import User

from .models import VendorCommission

MONEY_FIELD = DecimalField(max_digits=12, decimal_places=2)


def _line_total_expr():
    """unit_price * quantity, with an explicit output_field so SQLite
    doesn't have to guess the result type of multiplying two DecimalFields."""
    return ExpressionWrapper(F("unit_price") * F("quantity"), output_field=MONEY_FIELD)


def _parse_iso_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def resolve_date_range(query_params):
    """
    Turns `?period=`, or explicit `?start=&end=`, into a (start, end) pair
    of `date` objects. Either end of the pair can come back None, meaning
    "no lower/upper bound" (used by period=all).
    """
    today = timezone.localdate()

    explicit_start = _parse_iso_date(query_params.get("start"))
    explicit_end = _parse_iso_date(query_params.get("end"))
    if explicit_start or explicit_end:
        return (explicit_start or (today - timedelta(days=29))), (explicit_end or today)

    period = query_params.get("period", "30d")
    if period == "today":
        return today, today
    if period == "7d":
        return today - timedelta(days=6), today
    if period == "90d":
        return today - timedelta(days=89), today
    if period == "12m":
        return today - timedelta(days=364), today
    if period == "this_month":
        return today.replace(day=1), today
    if period == "last_month":
        first_of_this_month = today.replace(day=1)
        last_day_prev_month = first_of_this_month - timedelta(days=1)
        return last_day_prev_month.replace(day=1), last_day_prev_month
    if period == "all":
        return None, None
    return today - timedelta(days=29), today  # default: "30d"


def resolve_granularity(query_params, start, end):
    requested = query_params.get("granularity")
    if requested in ("day", "month"):
        return requested
    if start is None or end is None:
        return "month"
    return "day" if (end - start).days <= 62 else "month"


class DashboardAnalyticsService:
    def __init__(self, start=None, end=None, granularity="day"):
        self.start = start
        self.end = end
        self.granularity = granularity

    # --- shared, date-filtered querysets --------------------------------

    def _successful_payments(self):
        qs = Payment.objects.filter(status=Payment.Status.SUCCESS)
        if self.start:
            qs = qs.filter(paid_at__date__gte=self.start)
        if self.end:
            qs = qs.filter(paid_at__date__lte=self.end)
        return qs

    def _placed_transactions(self):
        qs = Transaction.objects.all()
        if self.start:
            qs = qs.filter(created_date__date__gte=self.start)
        if self.end:
            qs = qs.filter(created_date__date__lte=self.end)
        return qs

    def _paid_transactions(self):
        qs = Transaction.objects.filter(payment__status=Payment.Status.SUCCESS)
        if self.start:
            qs = qs.filter(payment__paid_at__date__gte=self.start)
        if self.end:
            qs = qs.filter(payment__paid_at__date__lte=self.end)
        return qs

    def _commissions(self):
        qs = VendorCommission.objects.all()
        if self.start:
            qs = qs.filter(created_date__date__gte=self.start)
        if self.end:
            qs = qs.filter(created_date__date__lte=self.end)
        return qs

    def _sold_items(self, extra_filter=None):
        qs = TransactionItem.objects.filter(transaction__payment__status=Payment.Status.SUCCESS)
        if self.start:
            qs = qs.filter(transaction__payment__paid_at__date__gte=self.start)
        if self.end:
            qs = qs.filter(transaction__payment__paid_at__date__lte=self.end)
        if extra_filter:
            qs = qs.filter(extra_filter)
        return qs

    def _new_users(self, role):
        qs = User.objects.filter(role=role)
        if self.start:
            qs = qs.filter(created_date__date__gte=self.start)
        if self.end:
            qs = qs.filter(created_date__date__lte=self.end)
        return qs

    def _trunc(self):
        return TruncMonth if self.granularity == "month" else TruncDate

    # --- admin -----------------------------------------------------------

    def admin_summary(self, top_n=10):
        payments = self._successful_payments()
        commissions = self._commissions()
        placed = self._placed_transactions()

        revenue_totals = payments.aggregate(gross_revenue=Sum("amount"), paid_orders=Count("id"))
        gross_revenue = revenue_totals["gross_revenue"] or Decimal("0")
        paid_orders = revenue_totals["paid_orders"] or 0

        commission_totals = commissions.aggregate(
            platform_revenue=Sum("platform_revenue_amount"),
            vendor_payout=Sum("vendor_payable_amount"),
        )
        platform_revenue = commission_totals["platform_revenue"] or Decimal("0")
        vendor_payout = commission_totals["vendor_payout"] or Decimal("0")

        revenue_series = list(
            payments.annotate(bucket=self._trunc()("paid_at"))
            .values("bucket")
            .order_by("bucket")
            .annotate(revenue=Sum("amount"), orders=Count("id"))
        )

        orders_by_status = list(
            placed.values("status").order_by("status").annotate(count=Count("id"))
        )

        top_vendors = list(
            commissions.values("vendor_id", "vendor__first_name", "vendor__last_name", "vendor__email")
            .annotate(
                sales=Sum("vendor_gross_amount"),
                commission=Sum("vendor_commission_amount"),
                payable=Sum("vendor_payable_amount"),
                orders=Count("transaction_id", distinct=True),
            )
            .order_by("-sales")[:top_n]
        )

        sold_items = self._sold_items()
        top_products = list(
            sold_items.values("product_id", "product__product_name", "product__sku")
            .annotate(units_sold=Sum("quantity"), revenue=Sum(_line_total_expr()))
            .order_by("-revenue")[:top_n]
        )
        top_categories = list(
            sold_items.values("product__category_id", "product__category__name")
            .annotate(units_sold=Sum("quantity"), revenue=Sum(_line_total_expr()))
            .order_by("-revenue")[:top_n]
        )

        return {
            "range": {"start": self.start, "end": self.end, "granularity": self.granularity},
            "kpis": {
                "gross_revenue": gross_revenue,
                "platform_revenue": platform_revenue,
                "vendor_payout": vendor_payout,
                "paid_orders": paid_orders,
                "orders_placed": placed.count(),
                "average_order_value": (gross_revenue / paid_orders) if paid_orders else Decimal("0"),
                "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
                "total_vendors": User.objects.filter(role=User.Role.VENDOR).count(),
                "new_customers": self._new_users(User.Role.CUSTOMER).count(),
                "new_vendors": self._new_users(User.Role.VENDOR).count(),
            },
            "revenue_series": revenue_series,
            "orders_by_status": orders_by_status,
            "top_vendors": top_vendors,
            "top_products": top_products,
            "top_categories": top_categories,
        }

    # --- manager -----------------------------------------------------------

    def manager_summary(self, top_n=20):
        commissions = self._commissions()

        vendor_performance = list(
            commissions.values("vendor_id", "vendor__first_name", "vendor__last_name", "vendor__email")
            .annotate(
                sales=Sum("vendor_gross_amount"),
                commission=Sum("vendor_commission_amount"),
                payable=Sum("vendor_payable_amount"),
                orders=Count("transaction_id", distinct=True),
            )
            .order_by("-sales")[:top_n]
        )
        product_counts = {
            row["vendor_id"]: row
            for row in Product.objects.values("vendor_id").annotate(
                product_count=Count("id"),
                active_product_count=Count("id", filter=Q(is_active=True)),
            )
        }
        for row in vendor_performance:
            counts = product_counts.get(row["vendor_id"], {})
            row["product_count"] = counts.get("product_count", 0)
            row["active_product_count"] = counts.get("active_product_count", 0)

        customer_activity = list(
            self._paid_transactions()
            .values("user_id", "user__first_name", "user__last_name", "user__email")
            .annotate(total_spend=Sum("total_amount"), orders=Count("id"))
            .order_by("-total_spend")[:top_n]
        )

        orders_by_status = list(
            self._placed_transactions()
            .values("status")
            .order_by("status")
            .annotate(count=Count("id"))
        )

        low_stock = list(
            Inventory.objects.select_related("product", "product__vendor")
            .filter(quantity_in_stock__lte=F("reorder_level"))
            .order_by("quantity_in_stock")
            .values(
                "product__product_name",
                "product__sku",
                "product__vendor__email",
                "quantity_in_stock",
                "reorder_level",
            )[:top_n]
        )

        stale_cutoff = timezone.now() - timedelta(days=3)
        pending_attention = list(
            Transaction.objects.filter(
                status__in=[Transaction.Status.PENDING, Transaction.Status.CONFIRMED],
                created_date__lt=stale_cutoff,
            )
            .select_related("user")
            .order_by("created_date")
            .values(
                "id", "transaction_number", "status", "total_amount", "created_date", "user__email"
            )[:top_n]
        )

        return {
            "range": {"start": self.start, "end": self.end, "granularity": self.granularity},
            "kpis": {
                "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
                "total_vendors": User.objects.filter(role=User.Role.VENDOR).count(),
                "new_customers": self._new_users(User.Role.CUSTOMER).count(),
                "orders_needing_attention": len(pending_attention),
                "low_stock_products": Inventory.objects.filter(
                    quantity_in_stock__lte=F("reorder_level")
                ).count(),
            },
            "vendor_performance": vendor_performance,
            "customer_activity": customer_activity,
            "orders_by_status": orders_by_status,
            "low_stock_alerts": low_stock,
            "pending_attention": pending_attention,
        }

    # --- vendor (self-scoped) --------------------------------------------

    def vendor_summary(self, vendor, top_n=10):
        commissions = self._commissions().filter(vendor=vendor)

        totals = commissions.aggregate(
            gross_sales=Sum("vendor_gross_amount"),
            commission_paid=Sum("vendor_commission_amount"),
            net_payable=Sum("vendor_payable_amount"),
            orders=Count("transaction_id", distinct=True),
        )

        sales_series = list(
            commissions.annotate(bucket=self._trunc()("created_date"))
            .values("bucket")
            .order_by("bucket")
            .annotate(sales=Sum("vendor_gross_amount"), payable=Sum("vendor_payable_amount"))
        )

        sold_items = self._sold_items(Q(product__vendor=vendor))
        top_products = list(
            sold_items.values("product_id", "product__product_name", "product__sku")
            .annotate(units_sold=Sum("quantity"), revenue=Sum(_line_total_expr()))
            .order_by("-revenue")[:top_n]
        )
        top_customers = list(
            sold_items.values(
                "transaction__user_id", "transaction__user__first_name",
                "transaction__user__last_name", "transaction__user__email",
            )
            .annotate(
                units=Sum("quantity"),
                spend=Sum(_line_total_expr()),
                orders=Count("transaction_id", distinct=True),
            )
            .order_by("-spend")[:top_n]
        )

        # Orders containing at least one of this vendor's products, within
        # the selected window (by order placement date, not payment date —
        # a vendor cares about orders coming in, paid or not).
        vendor_order_ids = (
            self._placed_transactions()
            .filter(items__product__vendor=vendor)
            .values_list("id", flat=True)
            .distinct()
        )
        orders_by_status = list(
            Transaction.objects.filter(id__in=vendor_order_ids)
            .values("status")
            .order_by("status")
            .annotate(count=Count("id"))
        )

        recent_orders_qs = (
            Transaction.objects.filter(id__in=vendor_order_ids)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=TransactionItem.objects.filter(product__vendor=vendor).select_related("product"),
                    to_attr="vendor_items",
                )
            )
            .order_by("-created_date")[:15]
        )
        recent_orders = [
            {
                "id": txn.id,
                "transaction_number": str(txn.transaction_number),
                "status": txn.status,
                "created_date": txn.created_date,
                "customer_email": txn.user.email,
                "customer_name": txn.user.full_name,
                "items": [
                    {
                        "product": item.product.product_name,
                        "quantity": item.quantity,
                        "subtotal": item.subtotal,
                    }
                    for item in txn.vendor_items
                ],
            }
            for txn in recent_orders_qs
        ]

        return {
            "range": {"start": self.start, "end": self.end, "granularity": self.granularity},
            "kpis": {
                "gross_sales": totals["gross_sales"] or Decimal("0"),
                "commission_paid": totals["commission_paid"] or Decimal("0"),
                "net_payable": totals["net_payable"] or Decimal("0"),
                "paid_orders": totals["orders"] or 0,
                "active_products": Product.objects.filter(vendor=vendor, is_active=True).count(),
                "total_products": Product.objects.filter(vendor=vendor).count(),
            },
            "sales_series": sales_series,
            "top_products": top_products,
            "top_customers": top_customers,
            "orders_by_status": orders_by_status,
            "recent_orders": recent_orders,
        }
