"""
PDF report generation.

Every builder here takes the exact dict `DashboardAnalyticsService` returns
for the JSON dashboards (see services.py) and lays it out as a page —
nothing is re-queried or recomputed. That's deliberate: a downloaded report
should always match what the dashboard showed at the moment it was
generated, and the only way to guarantee that is to render from the same
data rather than a second query path that could drift out of sync.
"""

import io

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

CURRENCY_SYMBOL = "৳"

INK = colors.HexColor("#0f172a")
MUTED = colors.HexColor("#475569")
BORDER = colors.HexColor("#e2e8f0")
STRIPE = colors.HexColor("#f8fafc")


def _fmt_money(value):
    return f"{CURRENCY_SYMBOL}{(value or 0):,.2f}"


def _fmt_date(value):
    if not value:
        return "—"
    return value.strftime("%d %b %Y") if hasattr(value, "strftime") else str(value)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontSize=18, spaceAfter=2))
    styles.add(ParagraphStyle(name="ReportSubtitle", parent=styles["Normal"], textColor=MUTED, spaceAfter=14))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="Empty", parent=styles["Italic"], textColor=MUTED))
    return styles


def _kpi_table(pairs):
    """pairs: list of (label, formatted value) — laid out two per row."""
    rows, data = [pairs[i : i + 2] for i in range(0, len(pairs), 2)], []
    for row in rows:
        cells = []
        for label, value in row:
            cells.extend([label, value])
        while len(cells) < 4:
            cells.append("")
        data.append(cells)
    table = Table(data, colWidths=[45 * mm, 40 * mm, 45 * mm, 40 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
                ("TEXTCOLOR", (2, 0), (2, -1), MUTED),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
            ]
        )
    )
    return table


def _data_table(headers, rows):
    if not rows:
        return Paragraph("No data for this period.", _styles()["Empty"])
    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, STRIPE]),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _range_subtitle(summary):
    date_range = summary["range"]
    start = _fmt_date(date_range["start"]) if date_range["start"] else "the beginning"
    end = _fmt_date(date_range["end"]) if date_range["end"] else "today"
    generated = timezone.localtime().strftime("%d %b %Y, %I:%M %p")
    return f"{start} \u2014 {end} \u00b7 Generated {generated}"


def _build(title, subtitle, blocks):
    """blocks: list of (heading_or_None, flowable) tuples, in order."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
    )
    styles = _styles()
    story = [Paragraph(title, styles["ReportTitle"]), Paragraph(subtitle, styles["ReportSubtitle"])]
    for heading, flowable in blocks:
        if heading:
            story.append(Paragraph(heading, styles["SectionHeading"]))
        story.append(flowable)
        story.append(Spacer(1, 4 * mm))
    doc.build(story)
    return buffer.getvalue()


def build_admin_report_pdf(summary):
    k = summary["kpis"]
    kpis = [
        ("Gross revenue", _fmt_money(k["gross_revenue"])),
        ("Platform revenue", _fmt_money(k["platform_revenue"])),
        ("Vendor payout", _fmt_money(k["vendor_payout"])),
        ("Average order value", _fmt_money(k["average_order_value"])),
        ("Paid orders", str(k["paid_orders"])),
        ("Orders placed", str(k["orders_placed"])),
        ("Total customers", str(k["total_customers"])),
        ("Total vendors", str(k["total_vendors"])),
        ("New customers", str(k["new_customers"])),
        ("New vendors", str(k["new_vendors"])),
    ]
    status_rows = [[row["status"].title(), str(row["count"])] for row in summary["orders_by_status"]]
    vendor_rows = [
        [
            row["vendor__email"],
            _fmt_money(row["sales"]),
            _fmt_money(row["commission"]),
            _fmt_money(row["payable"]),
            str(row["orders"]),
        ]
        for row in summary["top_vendors"]
    ]
    product_rows = [
        [row["product__product_name"], row["product__sku"], str(row["units_sold"]), _fmt_money(row["revenue"])]
        for row in summary["top_products"]
    ]

    blocks = [
        (None, _kpi_table(kpis)),
        ("Orders by status", _data_table(["Status", "Orders"], status_rows)),
        ("Top vendors", _data_table(["Vendor", "Sales", "Commission", "Payable", "Orders"], vendor_rows)),
        ("Top products", _data_table(["Product", "SKU", "Units sold", "Revenue"], product_rows)),
    ]
    return _build("Admin performance report", _range_subtitle(summary), blocks)


def build_manager_report_pdf(summary):
    k = summary["kpis"]
    kpis = [
        ("Total customers", str(k["total_customers"])),
        ("Total vendors", str(k["total_vendors"])),
        ("New customers", str(k["new_customers"])),
        ("Orders needing attention", str(k["orders_needing_attention"])),
        ("Low stock products", str(k["low_stock_products"])),
    ]
    vendor_rows = [
        [
            row["vendor__email"],
            _fmt_money(row["sales"]),
            _fmt_money(row["payable"]),
            str(row["orders"]),
            str(row["product_count"]),
        ]
        for row in summary["vendor_performance"]
    ]
    customer_rows = [
        [row["user__email"], _fmt_money(row["total_spend"]), str(row["orders"])]
        for row in summary["customer_activity"]
    ]
    low_stock_rows = [
        [
            row["product__product_name"],
            row["product__sku"],
            row["product__vendor__email"],
            str(row["quantity_in_stock"]),
            str(row["reorder_level"]),
        ]
        for row in summary["low_stock_alerts"]
    ]
    pending_rows = [
        [
            str(row["transaction_number"])[:8],
            row["status"].title(),
            _fmt_money(row["total_amount"]),
            row["user__email"],
            _fmt_date(row["created_date"]),
        ]
        for row in summary["pending_attention"]
    ]

    blocks = [
        (None, _kpi_table(kpis)),
        ("Vendor performance", _data_table(["Vendor", "Sales", "Payable", "Orders", "Products"], vendor_rows)),
        ("Top customers", _data_table(["Customer", "Total spend", "Orders"], customer_rows)),
        ("Low stock alerts", _data_table(["Product", "SKU", "Vendor", "In stock", "Reorder at"], low_stock_rows)),
        ("Orders needing attention", _data_table(["Order", "Status", "Total", "Customer", "Placed"], pending_rows)),
    ]
    return _build("Manager monitoring report", _range_subtitle(summary), blocks)


def build_vendor_report_pdf(summary, vendor):
    k = summary["kpis"]
    kpis = [
        ("Gross sales", _fmt_money(k["gross_sales"])),
        ("Commission paid", _fmt_money(k["commission_paid"])),
        ("Net payable", _fmt_money(k["net_payable"])),
        ("Paid orders", str(k["paid_orders"])),
        ("Active products", str(k["active_products"])),
        ("Total products", str(k["total_products"])),
    ]
    status_rows = [[row["status"].title(), str(row["count"])] for row in summary["orders_by_status"]]
    product_rows = [
        [row["product__product_name"], row["product__sku"], str(row["units_sold"]), _fmt_money(row["revenue"])]
        for row in summary["top_products"]
    ]
    customer_rows = [
        [
            row["transaction__user__email"],
            str(row["units"]),
            _fmt_money(row["spend"]),
            str(row["orders"]),
        ]
        for row in summary["top_customers"]
    ]

    blocks = [
        (None, _kpi_table(kpis)),
        ("Orders by status", _data_table(["Status", "Orders"], status_rows)),
        ("Top products", _data_table(["Product", "SKU", "Units sold", "Revenue"], product_rows)),
        ("Top customers", _data_table(["Customer", "Units bought", "Spend", "Orders"], customer_rows)),
    ]
    return _build(f"Vendor report \u2014 {vendor.full_name or vendor.email}", _range_subtitle(summary), blocks)
