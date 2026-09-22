"""
Seeds a realistic sales history against 5 vendors and 50 products, running
from September 1st through today, using the platform's real business logic
end to end — not hand-built rows.

Every simulated order goes through the exact same path a live order does:
`CheckoutService` creates the Transaction and its items (and decrements
real stock), a `Payment` is created against it, and `Payment.mark_successful()`
is called for orders that "went through" — which is what actually fires the
`apps.finance.signals` handler and books `VendorCommission` rows. Nothing
about the commission ledger is created directly; if it were, this data
would prove nothing about whether the real signal-driven system works.

The one thing that has to be done by hand afterward is backdating: every
model here inherits `TimeStampedModel`, whose `created_date`/`updated_date`
are `auto_now_add`/`auto_now` — Django overwrites any value you pass at
creation time with "now", and re-stamps `updated_date` on every `.save()`
after that too. So every order is first created normally (getting real
"now" timestamps and triggering every real side effect), and only
afterwards is it backdated with a `.update()` queryset call, which bypasses
`auto_now_add`/`auto_now` entirely. This has to happen for Transaction,
Payment (including `paid_at`, which `mark_successful()` always sets to
`timezone.now()`), VendorCommission, and StockMovement — miss one and that
table will still show everything as having happened "today", which quietly
defeats the entire point of this command on whichever dashboard reads it.

Purely additive and idempotent:
- Vendors, customers, categories and products are all `get_or_create`, so
  re-running never duplicates them.
- The whole simulated order batch is tagged via `Transaction.notes`, and
  the command refuses to simulate a second batch if that tag is already
  present — re-running the command adjusts nothing about the order history,
  it just confirms it's already there.
- Nothing here deletes or mutates data that isn't part of this command's
  own vendors/products. Any products created by an older version of this
  command (previous TZ-/FM-/SH-/HC- prefixed SKUs) are deactivated, never
  deleted — TransactionItem's FK to Product is PROTECT, so deleting old
  products that already have order history against them isn't even
  possible, and isn't attempted here.

Usage:
    python manage.py seed_transaction_history
    python manage.py seed_transaction_history --dry-run
"""

import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from django.db.models import Q
from django.utils import timezone

from apps.category.models import Category
from apps.finance.models import VendorCommission
from apps.inventory.models import Inventory, StockMovement
from apps.payments.models import Payment
from apps.products.models import Product
from apps.transactions.models import Transaction
from apps.transactions.services import CheckoutService
from apps.users.models import User

BATCH_TAG = "demo-seed-sept-batch"

CATEGORY_CODES = {
    "Electronics": "ELEC",
    "Mobile Phones": "MOB",
    "Home Appliances": "APP",
    "Groceries": "GRO",
    "Fashion": "FAS",
    "Beauty & Personal Care": "BEA",
    "Books": "BOK",
    "Sports & Fitness": "SPT",
    "Home & Kitchen": "HOM",
    "Stationery": "STA",
}

# Old SKU prefixes from an earlier version of this command — deactivated
# (never deleted) so a demo doesn't show 100+ near-duplicate products.
LEGACY_SKU_PREFIXES = ("TZ-", "FM-", "SH-", "HC-")

VENDORS = [
    {"email": "vendor@example.com", "first_name": "Val", "last_name": "Vendor",
     "password": "Vendor@12345", "code": "TZX", "store": "TechZone"},
    {"email": "freshmart.vendor@example.com", "first_name": "Farhana", "last_name": "Rahman",
     "password": "Vendor@12345", "code": "FRM", "store": "FreshMart"},
    {"email": "stylehouse.vendor@example.com", "first_name": "Sabbir", "last_name": "Hossain",
     "password": "Vendor@12345", "code": "STY", "store": "Style House"},
    {"email": "homecraft.vendor@example.com", "first_name": "Hasan", "last_name": "Mahmud",
     "password": "Vendor@12345", "code": "HMC", "store": "HomeCraft"},
    {"email": "sportshub.vendor@example.com", "first_name": "Rafiq", "last_name": "Islam",
     "password": "Vendor@12345", "code": "SPH", "store": "SportsHub"},
]

CUSTOMERS = [
    {"email": "customer@example.com", "first_name": "Cara", "last_name": "Customer"},
    {"email": "nabila.rahman@example.com", "first_name": "Nabila", "last_name": "Rahman"},
    {"email": "tanvir.ahmed@example.com", "first_name": "Tanvir", "last_name": "Ahmed"},
    {"email": "sadia.islam@example.com", "first_name": "Sadia", "last_name": "Islam"},
    {"email": "rakib.hasan@example.com", "first_name": "Rakib", "last_name": "Hasan"},
    {"email": "farhana.akter@example.com", "first_name": "Farhana", "last_name": "Akter"},
    {"email": "imran.khan@example.com", "first_name": "Imran", "last_name": "Khan"},
    {"email": "mim.chowdhury@example.com", "first_name": "Mim", "last_name": "Chowdhury"},
    {"email": "shakil.ahmed@example.com", "first_name": "Shakil", "last_name": "Ahmed"},
]
CUSTOMER_PASSWORD = "Customer@12345"

# (name, brand, category, mrp, discount_pct, target_display_stock)
# Ten curated products per vendor — the target_display_stock is what the
# catalog shows once seeding is done, not what it's capped at during
# simulation (see _restock_to_display_levels).
CATALOG = {
    "TZX": [
        ("JBL Go 3 Portable Speaker", "JBL", "Electronics", "4200", "10", 26),
        ("Havit HV-H2002D Gaming Headset", "Havit", "Electronics", "2950", "14", 34),
        ("Xiaomi Mi Power Bank 20000mAh", "Xiaomi", "Electronics", "3450", "12", 30),
        ("Ugreen 6-in-1 USB-C Hub", "Ugreen", "Electronics", "4600", "9", 18),
        ("Transcend 1TB Portable SSD", "Transcend", "Electronics", "9800", "11", 12),
        ("SanDisk Ultra 128GB microSD", "SanDisk", "Electronics", "1650", "7", 60),
        ("Samsung Galaxy A25 5G", "Samsung", "Mobile Phones", "32999", "6", 11),
        ("Infinix Note 40", "Infinix", "Mobile Phones", "26500", "9", 15),
        ("Realme Buds Air 5", "Realme", "Electronics", "5400", "13", 25),
        ("Symphony Z60", "Symphony", "Mobile Phones", "11500", "10", 20),
    ],
    "FRM": [
        ("Pusti Atta 2kg", "Pusti", "Groceries", "145", "2", 120),
        ("Rupchanda Soyabean Oil 2L", "Rupchanda", "Groceries", "375", "3", 95),
        ("Ispahani Mirzapore Tea 400g", "Ispahani", "Groceries", "320", "5", 85),
        ("Kazi Farms Eggs 30 pcs", "Kazi Farms", "Groceries", "380", "2", 55),
        ("Diamond Chinigura Rice 2kg", "Diamond", "Groceries", "290", "4", 70),
        ("Pran Mango Juice 1L", "Pran", "Groceries", "120", "6", 90),
        ("Dove Nourishing Body Wash 500ml", "Dove", "Beauty & Personal Care", "720", "10", 45),
        ("Himalaya Neem Face Wash 150ml", "Himalaya", "Beauty & Personal Care", "380", "8", 62),
        ("Head & Shoulders Shampoo 650ml", "Head & Shoulders", "Beauty & Personal Care", "980", "9", 44),
        ("Lifebuoy Handwash Refill 1L", "Lifebuoy", "Beauty & Personal Care", "340", "7", 75),
    ],
    "STY": [
        ("Aarong Half Silk Saree", "Aarong", "Fashion", "6500", "15", 12),
        ("Ecstasy Slim Fit Denim Jeans", "Ecstasy", "Fashion", "2890", "20", 26),
        ("Sailor Oxford Formal Shirt", "Sailor", "Fashion", "2250", "12", 30),
        ("Apex Leather Formal Shoes", "Apex", "Fashion", "4200", "10", 18),
        ("Bata Comfit Sandals", "Bata", "Fashion", "1450", "8", 40),
        ("Atomic Habits Paperback", "Penguin", "Books", "720", "10", 35),
        ("Sapiens Hardcover Edition", "Harper", "Books", "1350", "12", 20),
        ("Rich Dad Poor Dad", "Plata", "Books", "560", "8", 42),
        ("Deli Gel Pen Pack of 12", "Deli", "Stationery", "320", "10", 90),
        ("Casio FX-991EX Scientific Calculator", "Casio", "Stationery", "2450", "6", 24),
    ],
    "HMC": [
        ("Walton WFC-3F5 Refrigerator", "Walton", "Home Appliances", "42500", "7", 6),
        ("Miyako Rice Cooker 1.8L", "Miyako", "Home Appliances", "3250", "9", 22),
        ("Vision Ceiling Fan 56 inch", "Vision", "Home Appliances", "3950", "6", 30),
        ("Panasonic Microwave Oven 20L", "Panasonic", "Home Appliances", "14900", "8", 10),
        ("Kiam Induction Cooker", "Kiam", "Home Appliances", "4600", "11", 16),
        ("RFL Plastic Storage Rack", "RFL", "Home & Kitchen", "2850", "12", 25),
        ("Kiam Pressure Cooker 5L", "Kiam", "Home & Kitchen", "2650", "8", 28),
        ("Lock & Lock Container Set 6 pcs", "Lock & Lock", "Home & Kitchen", "1950", "10", 34),
        ("Bengal Dinner Set 32 pcs", "Bengal", "Home & Kitchen", "3400", "14", 15),
        ("Tefal Nonstick Frying Pan 26cm", "Tefal", "Home & Kitchen", "2450", "9", 26),
    ],
    "SPH": [
        ("Nivia Football Size 5", "Nivia", "Sports & Fitness", "1250", "10", 36),
        ("Cosco Kashmir Willow Cricket Bat", "Cosco", "Sports & Fitness", "3200", "12", 14),
        ("Kore Adjustable Dumbbell Set 20kg", "Kore", "Sports & Fitness", "5400", "15", 10),
        ("Boldfit Skipping Rope with Counter", "Boldfit", "Sports & Fitness", "450", "8", 55),
        ("Yonex Mavis 350 Shuttlecock Tube", "Yonex", "Sports & Fitness", "850", "5", 40),
        ("Adidas Predator Training Football Boots", "Adidas", "Sports & Fitness", "6200", "18", 12),
        ("Decathlon Kalenji Running Shoes", "Decathlon", "Sports & Fitness", "2800", "14", 22),
        ("Nivia Yoga Mat 8mm", "Nivia", "Sports & Fitness", "950", "9", 38),
        ("Cosco Table Tennis Racket Set", "Cosco", "Sports & Fitness", "1150", "11", 20),
        ("Boldfit Resistance Band Set", "Boldfit", "Sports & Fitness", "680", "13", 48),
    ],
}


# Product image URLs used by the demo catalog. These are intentionally
# kept separate from CATALOG so the existing product/pricing/stock tuples
# and transaction-history logic remain unchanged.
PRODUCT_IMAGE_URLS = {
    # TechZone
    "TZX-ELEC-01": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-02": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-03": "https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-04": "https://images.unsplash.com/photo-1616440342232-159c99147d33?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-05": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-06": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
    "TZX-MOB-07": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80",
    "TZX-MOB-08": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80",
    "TZX-ELEC-09": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
    "TZX-MOB-10": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80",

    # FreshMart
    "FRM-GRO-01": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop&q=80",
    "FRM-GRO-02": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
    "FRM-GRO-03": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80",
    "FRM-GRO-04": "https://static-01.daraz.com.bd/p/8c1b3380cca980346322dcdced4c74e8.png",
    "FRM-GRO-05": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
    "FRM-GRO-06": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=600&auto=format&fit=crop&q=80",
    "FRM-BEA-07": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
    "FRM-BEA-08": "https://images.unsplash.com/photo-1556228722-d1193828e40b?w=600&auto=format&fit=crop&q=80",
    "FRM-BEA-09": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=600&auto=format&fit=crop&q=80",
    "FRM-BEA-10": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=600&auto=format&fit=crop&q=80",

    # Style House
    "STY-FAS-01": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
    "STY-FAS-02": "https://images.unsplash.com/photo-1542272604-780c36856d61?w=600&auto=format&fit=crop&q=80",
    "STY-FAS-03": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80",
    "STY-FAS-04": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80",
    "STY-FAS-05": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=600&auto=format&fit=crop&q=80",
    "STY-BOK-06": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
    "STY-BOK-07": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80",
    "STY-BOK-08": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80",
    "STY-STA-09": "https://images.unsplash.com/photo-1585336261026-6757f541a674?w=600&auto=format&fit=crop&q=80",
    "STY-STA-10": "https://images.unsplash.com/photo-1611125832047-1d7ad1e8e48f?w=600&auto=format&fit=crop&q=80",

    # HomeCraft
    "HMC-APP-01": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop&q=80",
    "HMC-APP-02": "https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=600&auto=format&fit=crop&q=80",
    "HMC-APP-03": "https://images.unsplash.com/photo-1618944847023-38aa001235f0?w=600&auto=format&fit=crop&q=80",
    "HMC-APP-04": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=600&auto=format&fit=crop&q=80",
    "HMC-APP-05": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80",
    "HMC-HOM-06": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&auto=format&fit=crop&q=80",
    "HMC-HOM-07": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&auto=format&fit=crop&q=80",
    "HMC-HOM-08": "https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=600&auto=format&fit=crop&q=80",
    "HMC-HOM-09": "https://images.unsplash.com/photo-1615865417236-d67f572a746f?w=600&auto=format&fit=crop&q=80",
    "HMC-HOM-10": "https://images.unsplash.com/photo-1583778176476-4a8b02a64c01?w=600&auto=format&fit=crop&q=80",

    # SportsHub
    "SPH-SPT-01": "https://images.unsplash.com/photo-1614632537190-23e4146777db?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-02": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-03": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-04": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-05": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-06": "https://images.unsplash.com/photo-1511886929837-354d827aae26?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-07": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-08": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-09": "https://images.unsplash.com/photo-1534158914592-062992fbe900?w=600&auto=format&fit=crop&q=80",
    "SPH-SPT-10": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&auto=format&fit=crop&q=80",
}

WAREHOUSES = {
    "TZX": "Dhaka - Tejgaon DC", "FRM": "Dhaka - Savar DC",
    "STY": "Narayanganj DC", "HMC": "Gazipur DC", "SPH": "Dhaka - Uttara DC",
}

# Generous ceiling so CheckoutService never rejects a simulated order for
# lack of stock — real, sellable-looking numbers are set at the end,
# after simulation has consumed whatever it consumes.
SIMULATION_STOCK_CEILING = 100_000

# Outcome mix for a simulated order, and the payment method mix within the
# "successful" bucket. Numbers don't need to be exact — they just need to
# produce a catalog of orders in every status a real store would have.
OUTCOME_WEIGHTS = {"SUCCESS": 0.75, "PENDING": 0.15, "CANCELLED": 0.10}
ONLINE_VS_COD_WEIGHTS = {"ONLINE": 0.55, "COD": 0.45}
MULTI_VENDOR_ORDER_CHANCE = 0.25


class Command(BaseCommand):
    help = (
        "Seeds 5 vendors / 50 products and a realistic, backdated order "
        "history from September 1st through today, driven through the real "
        "checkout/payment/commission code paths. Safe to run more than once."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would happen, then roll the whole thing back.",
        )
        parser.add_argument(
            "--orders", type=int, default=None,
            help="Override the number of simulated orders (default: scales with the date range).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        random.seed(20260901)  # reproducible runs — same story every time
        try:
            with db_transaction.atomic():
                summary = self._seed(order_count_override=options["orders"])
                self._report(summary, dry_run)
                if dry_run:
                    raise _DryRun()
        except _DryRun:
            self.stdout.write(self.style.WARNING("\nDry run — all changes rolled back."))

    # --- orchestration --------------------------------------------------

    def _seed(self, order_count_override):
        vendors = self._seed_vendors()
        customers = self._seed_customers()
        categories = self._seed_categories()
        products_by_vendor, created_products = self._seed_products(vendors, categories)
        self._deactivate_legacy_products()

        already_seeded = Transaction.objects.filter(notes=BATCH_TAG).exists()
        orders_created = 0
        date_span = None

        if already_seeded:
            self.stdout.write(
                self.style.WARNING(
                    "Order history already seeded (found transactions tagged "
                    f"'{BATCH_TAG}') — skipping simulation. Products and "
                    "accounts above are still confirmed present."
                )
            )
        else:
            start_date, end_date = self._resolve_date_range()
            date_span = (start_date, end_date)
            order_count = order_count_override or self._default_order_count(start_date, end_date)
            orders_created = self._simulate_orders(
                vendors, customers, products_by_vendor, start_date, end_date, order_count
            )
            self._restock_to_display_levels(products_by_vendor)

        return {
            "vendors": vendors,
            "customers_created": len(customers),
            "products_created": created_products,
            "orders_created": orders_created,
            "date_span": date_span,
            "already_seeded": already_seeded,
        }

    # --- accounts + catalog ----------------------------------------------

    def _seed_vendors(self):
        vendors = {}
        for spec in VENDORS:
            user, created = User.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "role": User.Role.VENDOR,
                },
            )
            if created:
                user.set_password(spec["password"])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  vendor  {spec['email']} / {spec['password']} ({spec['store']})")
                )
            vendors[spec["code"]] = user
        return vendors

    def _seed_customers(self):
        created = []
        for spec in CUSTOMERS:
            user, was_created = User.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "role": User.Role.CUSTOMER,
                },
            )
            if was_created:
                user.set_password(CUSTOMER_PASSWORD)
                user.save()
                created.append(user)
        if created:
            self.stdout.write(self.style.SUCCESS(f"  {len(created)} demo customer account(s) created"))
        return list(User.objects.filter(email__in=[c["email"] for c in CUSTOMERS]))

    def _seed_categories(self):
        return {name: Category.objects.get_or_create(name=name)[0] for name in CATEGORY_CODES}

    def _seed_products(self, vendors, categories):
        products_by_vendor = {code: [] for code in CATALOG}
        created_count = 0
        for code, rows in CATALOG.items():
            vendor = vendors[code]
            for index, (name, brand, category_name, mrp, discount, _display_stock) in enumerate(
                rows, start=1
            ):
                sku = f"{code}-{CATEGORY_CODES[category_name]}-{index:02d}"
                product, created = Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        "product_name": name,
                        "brand": brand,
                        "category": categories[category_name],
                        "mrp": Decimal(mrp),
                        "discount_percentage": Decimal(discount),
                        "vendor": vendor,
                        "is_active": True,
                        "description": f"{name} by {brand}, sold by {vendor.full_name}.",
                        "image_url": PRODUCT_IMAGE_URLS.get(sku, ""),
                    },
                )
                image_url = PRODUCT_IMAGE_URLS.get(sku, "")
                if product.image_url != image_url:
                    Product.objects.filter(pk=product.pk).update(image_url=image_url)
                    product.image_url = image_url

                if created:
                    created_count += 1
                elif not product.is_active:
                    # A previous run may have deactivated it (e.g. legacy
                    # cleanup); this command's own 50 should always be live.
                    Product.objects.filter(pk=product.pk).update(is_active=True)

                # Mutate through product.inventory (not a bulk .update())
                # deliberately — product objects collected here get held
                # onto and reused later by _simulate_orders via
                # CheckoutService, and a bulk queryset .update() never
                # invalidates Django's cached .inventory on an
                # already-loaded instance (confirmed: the post_save signal
                # that creates this row caches it onto the product
                # instance immediately). A bulk update would silently
                # leave every one of these Product objects pointing at a
                # stale, zero-stock Inventory for the rest of this run.
                inventory = product.inventory
                inventory.quantity_in_stock = SIMULATION_STOCK_CEILING
                inventory.reorder_level = max(5, round(_display_stock * 0.3))
                inventory.warehouse_location = WAREHOUSES[code]
                inventory.save(
                    update_fields=["quantity_in_stock", "reorder_level", "warehouse_location", "updated_date"]
                )
                products_by_vendor[code].append(product)

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"  {created_count} product(s) created"))
        return products_by_vendor, created_count

    def _deactivate_legacy_products(self):
        legacy_filter = Q()
        for prefix in LEGACY_SKU_PREFIXES:
            legacy_filter |= Q(sku__startswith=prefix)
        legacy = Product.objects.filter(legacy_filter, is_active=True)
        count = legacy.count()
        if count:
            legacy.update(is_active=False)
            self.stdout.write(
                self.style.WARNING(
                    f"  Deactivated {count} product(s) from an earlier seed run "
                    "(kept for order-history integrity, hidden from the storefront)."
                )
            )

    # --- order simulation --------------------------------------------------

    def _resolve_date_range(self):
        today = timezone.localdate()
        start = date(today.year, 9, 1)
        if start > today:
            start = date(today.year - 1, 9, 1)
        return start, today

    def _default_order_count(self, start_date, end_date):
        days = (end_date - start_date).days + 1
        return min(400, max(80, days * 8))

    def _simulate_orders(self, vendors, customers, products_by_vendor, start_date, end_date, order_count):
        all_products = [p for products in products_by_vendor.values() for p in products]
        created = 0

        for _ in range(order_count):
            order_dt = self._random_datetime(start_date, end_date)
            customer = random.choice(customers)
            items = self._pick_items(products_by_vendor, all_products)

            try:
                txn = CheckoutService(
                    customer, items, shipping_address=self._random_address()
                ).execute()
            except Exception:  # noqa: BLE001 — a rare stock/validation clash just skips this draw
                continue

            Transaction.objects.filter(pk=txn.pk).update(notes=BATCH_TAG)

            outcome = self._weighted_choice(OUTCOME_WEIGHTS)
            payment = None

            if outcome == "SUCCESS":
                method = self._weighted_choice(ONLINE_VS_COD_WEIGHTS)
                payment = Payment.objects.create(
                    transaction=txn, method=method, amount=txn.total_amount, currency="BDT",
                    gateway_transaction_id=f"seed-{txn.transaction_number.hex[:12]}",
                )
                payment.mark_successful(
                    gateway_reference=payment.gateway_transaction_id, validation_id="seed"
                )
                paid_dt = order_dt + timedelta(minutes=random.randint(1, 45))
                Payment.objects.filter(pk=payment.pk).update(
                    created_date=order_dt, updated_date=paid_dt, paid_at=paid_dt
                )
                VendorCommission.objects.filter(payment=payment).update(
                    created_date=paid_dt, updated_date=paid_dt
                )
            elif outcome == "CANCELLED":
                Transaction.objects.filter(pk=txn.pk).update(status=Transaction.Status.CANCELLED)
                if random.random() < 0.4:
                    method = self._weighted_choice(ONLINE_VS_COD_WEIGHTS)
                    payment = Payment.objects.create(
                        transaction=txn, method=method, amount=txn.total_amount, currency="BDT",
                    )
                    payment.mark_failed()
                    Payment.objects.filter(pk=payment.pk).update(
                        created_date=order_dt, updated_date=order_dt
                    )
            else:  # PENDING — order placed, payment not (yet) completed
                if random.random() < 0.5:
                    method = self._weighted_choice(ONLINE_VS_COD_WEIGHTS)
                    payment = Payment.objects.create(
                        transaction=txn, method=method, amount=txn.total_amount, currency="BDT",
                    )
                    Payment.objects.filter(pk=payment.pk).update(
                        created_date=order_dt, updated_date=order_dt
                    )

            Transaction.objects.filter(pk=txn.pk).update(
                created_date=order_dt, updated_date=order_dt
            )
            StockMovement.objects.filter(
                note__contains=str(txn.transaction_number)
            ).update(created_date=order_dt, updated_date=order_dt)

            created += 1

        return created

    def _pick_items(self, products_by_vendor, all_products):
        if random.random() < MULTI_VENDOR_ORDER_CHANCE and len(products_by_vendor) > 1:
            codes = random.sample(list(products_by_vendor.keys()), 2)
            pool = [random.choice(products_by_vendor[codes[0]]), random.choice(products_by_vendor[codes[1]])]
        else:
            line_count = random.choices([1, 2, 3, 4], weights=[45, 30, 15, 10])[0]
            pool = random.sample(all_products, k=min(line_count, len(all_products)))

        return [{"product": product, "quantity": random.randint(1, 3)} for product in pool]

    def _random_datetime(self, start_date, end_date):
        span_days = (end_date - start_date).days
        offset = random.randint(0, max(span_days, 0))
        day = start_date + timedelta(days=offset)
        hour = random.choices(range(24), weights=self._hourly_traffic_weights())[0]
        minute = random.randint(0, 59)
        naive = datetime.combine(day, time(hour=hour, minute=minute))
        return timezone.make_aware(naive) if timezone.is_naive(naive) else naive

    @staticmethod
    def _hourly_traffic_weights():
        # Heavier in the evening (BD shopping habit: post-work browsing),
        # thin overnight — just enough shape to not look perfectly uniform.
        return [1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 7, 6, 6, 7, 8, 9, 10, 10, 9, 7, 4, 2]

    @staticmethod
    def _weighted_choice(weights: dict):
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]

    @staticmethod
    def _random_address():
        areas = ["Dhanmondi", "Mirpur", "Gulshan", "Uttara", "Banani", "Mohammadpur", "Bashundhara"]
        return f"House {random.randint(1, 60)}, Road {random.randint(1, 27)}, {random.choice(areas)}, Dhaka"

    def _restock_to_display_levels(self, products_by_vendor):
        now = timezone.now()
        for code, rows in CATALOG.items():
            for product, (*_umused, display_stock) in zip(products_by_vendor[code], rows):
                inventory = product.inventory
                inventory.quantity_in_stock = display_stock
                inventory.last_restocked_at = now
                inventory.save(update_fields=["quantity_in_stock", "last_restocked_at", "updated_date"])
                StockMovement.objects.create(
                    inventory=inventory,
                    movement_type=StockMovement.MovementType.RESTOCK,
                    quantity=display_stock,
                    note="Restocked after seed_transaction_history simulation.",
                )

    # --- reporting -----------------------------------------------------

    def _report(self, summary, dry_run):
        verb = "Would result in" if dry_run else "Result"
        self.stdout.write("")
        self.stdout.write(f"{verb}:")
        self.stdout.write(f"  vendors            {User.objects.filter(role=User.Role.VENDOR).count()}")
        self.stdout.write(f"  customers          {User.objects.filter(role=User.Role.CUSTOMER).count()}")
        self.stdout.write(f"  products (active)  {Product.objects.filter(is_active=True).count()}")
        if summary["already_seeded"]:
            self.stdout.write("  orders             already seeded in a previous run — unchanged")
        else:
            start, end = summary["date_span"]
            self.stdout.write(f"  orders simulated   {summary['orders_created']}  ({start} \u2192 {end})")
        self.stdout.write(f"  paid orders        {Payment.objects.filter(status=Payment.Status.SUCCESS).count()}")
        self.stdout.write(f"  commission entries {VendorCommission.objects.count()}")
        total_platform_revenue = sum(
            (c.platform_revenue_amount for c in VendorCommission.objects.all()), Decimal("0")
        )
        self.stdout.write(f"  platform revenue   \u09f3{total_platform_revenue:,.2f}")


class _DryRun(Exception):
    """Internal sentinel used to roll back a --dry-run transaction."""