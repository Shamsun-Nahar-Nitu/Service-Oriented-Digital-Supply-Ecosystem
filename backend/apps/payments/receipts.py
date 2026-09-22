"""
Generates a downloadable receipt PDF for a single payment.

Deliberately separate from apps.finance.reports even though both use
reportlab the same way — finance's reports summarize many orders for a
vendor/admin/manager; this summarizes exactly one order for the customer
who paid for it. Different audience, different shape, no shared data to
factor out.
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
EMBER = colors.HexColor("#FF5A1F")


def _fmt_money(value):
    return f"{CURRENCY_SYMBOL}{(value or 0):,.2f}"


def _fmt_date(value):
    if not value:
        return "\u2014"
    local = timezone.localtime(value) if timezone.is_aware(value) else value
    return local.strftime("%d %b %Y, %I:%M %p")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReceiptBrand", parent=styles["Title"], fontSize=20, textColor=EMBER, spaceAfter=2))
    styles.add(ParagraphStyle(name="ReceiptMeta", parent=styles["Normal"], textColor=MUTED, fontSize=9, leading=13))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading3"], spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="Footer", parent=styles["Normal"], textColor=MUTED, fontSize=8, alignment=1))
    return styles


def _items_table(items):
    header = ["Product", "SKU", "Qty", "Unit price", "Subtotal"]
    rows = [
        [item.product.product_name, item.product.sku, str(item.quantity), _fmt_money(item.unit_price), _fmt_money(item.subtotal)]
        for item in items
    ]
    table = Table([header] + rows, colWidths=[70 * mm, 30 * mm, 15 * mm, 30 * mm, 30 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, STRIPE]),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _totals_table(transaction_obj):
    rows = [
        ["Items subtotal", _fmt_money(transaction_obj.items_subtotal)],
        ["Platform service fee", _fmt_money(transaction_obj.platform_fee)],
        ["Total paid", _fmt_money(transaction_obj.total_amount)],
    ]
    table = Table(rows, colWidths=[130 * mm, 45 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TEXTCOLOR", (0, 0), (-1, -2), MUTED),
                ("LINEABOVE", (0, -1), (-1, -1), 0.75, INK),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_receipt_pdf(payment):
    """payment: a Payment instance with .transaction and .transaction.items
    already available (call with select_related/prefetch_related from the
    view — see PaymentViewSet.receipt)."""
    transaction_obj = payment.transaction
    customer = transaction_obj.user
    styles = _styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm, leftMargin=16 * mm, rightMargin=16 * mm
    )

    story = [
        Paragraph("ShopNest", styles["ReceiptBrand"]),
        Paragraph("Payment receipt", styles["Heading2"]),
        Spacer(1, 3 * mm),
        Paragraph(
            f"Order #{str(transaction_obj.transaction_number)[:8]} &nbsp;\u00b7&nbsp; "
            f"Placed {_fmt_date(transaction_obj.created_date)}",
            styles["ReceiptMeta"],
        ),
        Paragraph(
            f"Payment method: {payment.get_method_display()} &nbsp;\u00b7&nbsp; "
            f"Paid {_fmt_date(payment.paid_at)}",
            styles["ReceiptMeta"],
        ),
    ]

    story.append(Paragraph("Billed to", styles["SectionHeading"]))
    billing_lines = [customer.full_name or customer.email, customer.email]
    if transaction_obj.shipping_address:
        billing_lines.append(transaction_obj.shipping_address.replace("\n", "<br/>"))
    story.append(Paragraph("<br/>".join(billing_lines), styles["Normal"]))

    story.append(Paragraph("Items", styles["SectionHeading"]))
    story.append(_items_table(transaction_obj.items.all()))
    story.append(Spacer(1, 4 * mm))
    story.append(_totals_table(transaction_obj))

    story.append(Spacer(1, 12 * mm))
    story.append(
        Paragraph(
            "This receipt confirms payment was received for the order above. "
            "Questions about this order? Reach us through the Contact link on the site.",
            styles["Footer"],
        )
    )

    doc.build(story)
    return buffer.getvalue()