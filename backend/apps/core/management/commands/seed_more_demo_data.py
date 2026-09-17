"""
Additive demo data — extends what `seed_demo_data` already created.

This command is deliberately separate from `seed_demo_data` rather than an
edit to it, for two reasons:

1. Your database already holds data you want to keep. Editing the original
   seeder would mean re-running it, and although it is written with
   get_or_create, re-running it also re-applies the `image_url` update
   branch to products you may have since edited in the admin. A separate
   command touches nothing that already exists.
2. The two have different jobs. `seed_demo_data` bootstraps an empty
   database with the minimum to log in; this one fattens the catalog for
   screenshots, demos and pagination testing.

Safety properties, in order of how much they matter here:

- No delete, no flush, no truncate. There is not a single destructive call
  in this file.
- Every write is `get_or_create` keyed on a natural key (email for users,
  SKU for products). Run it ten times and you get the same database.
- Stock levels and inventory rows are only written for products this run
  actually created. If you later adjust stock in the admin and re-run this,
  your numbers survive.
- SKUs use a vendor-prefixed namespace (TZ-, FM-, SH-, HC-) that cannot
  collide with the flat SKUs the original seeder uses (ELEC-ANK-001 etc).

Usage:
    python manage.py seed_more_demo_data
    python manage.py seed_more_demo_data --dry-run
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.category.models import Category
from apps.inventory.models import Inventory, StockMovement
from apps.products.models import Product
from apps.users.models import User

# Short codes used to build collision-proof SKUs.
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

# Four vendors, each with a coherent catalog rather than a random scatter —
# a vendor dashboard showing sixteen related products looks like a real
# storefront; sixteen unrelated ones looks like test data.
#
# The first entry reuses the account seed_demo_data already made, so this
# lands at four vendors total, not five. Its existing 19 products stay put.
VENDORS = [
    {
        "email": "vendor@example.com",
        "first_name": "Val",
        "last_name": "Vendor",
        "password": "Vendor@12345",
        "code": "TZ",
        "store": "TechZone",
    },
    {
        "email": "freshmart.vendor@example.com",
        "first_name": "Farhana",
        "last_name": "Rahman",
        "password": "Vendor@12345",
        "code": "FM",
        "store": "FreshMart",
    },
    {
        "email": "stylehouse.vendor@example.com",
        "first_name": "Sabbir",
        "last_name": "Hossain",
        "password": "Vendor@12345",
        "code": "SH",
        "store": "Style House",
    },
    {
        "email": "homecraft.vendor@example.com",
        "first_name": "Hasan",
        "last_name": "Mahmud",
        "password": "Vendor@12345",
        "code": "HC",
        "store": "HomeCraft",
    },
]

# Three managers total — the one seed_demo_data made, plus two more.
MANAGERS = [
    {
        "email": "manager@example.com",
        "first_name": "Mo",
        "last_name": "Manager",
        "password": "Manager@12345",
    },
    {
        "email": "manager.catalog@example.com",
        "first_name": "Nusrat",
        "last_name": "Jahan",
        "password": "Manager@12345",
    },
    {
        "email": "manager.ops@example.com",
        "first_name": "Tanvir",
        "last_name": "Ahmed",
        "password": "Manager@12345",
    },
]

# (product_name, brand, category, mrp, discount_pct, stock, reorder_level)
# Sixteen per vendor, sixty-four in total.
CATALOG = {
    "TZ": [
        ("JBL Go 3 Portable Speaker", "JBL", "Electronics", "4200", "10", 26, 10),
        ("Havit HV-H2002D Gaming Headset", "Havit", "Electronics", "2950", "14", 34, 12),
        ("A4Tech FK11 Wired Keyboard", "A4Tech", "Electronics", "1250", "8", 48, 15),
        ("Xiaomi Mi Power Bank 20000mAh", "Xiaomi", "Electronics", "3450", "12", 30, 10),
        ("Baseus 65W GaN Fast Charger", "Baseus", "Electronics", "3900", "15", 22, 8),
        ("Ugreen 6-in-1 USB-C Hub", "Ugreen", "Electronics", "4600", "9", 18, 8),
        ("Walton 24 inch LED Monitor", "Walton", "Electronics", "14500", "6", 9, 5),
        ("Transcend 1TB Portable SSD", "Transcend", "Electronics", "9800", "11", 12, 5),
        ("SanDisk Ultra 128GB microSD", "SanDisk", "Electronics", "1650", "7", 60, 20),
        ("Realme Buds Air 5", "Realme", "Electronics", "5400", "13", 25, 10),
        ("Samsung Galaxy A25 5G", "Samsung", "Mobile Phones", "32999", "6", 11, 5),
        ("Infinix Note 40", "Infinix", "Mobile Phones", "26500", "9", 15, 5),
        ("Vivo Y28 5G", "Vivo", "Mobile Phones", "23900", "7", 13, 5),
        ("Oppo A60", "Oppo", "Mobile Phones", "21999", "5", 16, 6),
        ("Symphony Z60", "Symphony", "Mobile Phones", "11500", "10", 20, 8),
        ("Nokia C32", "Nokia", "Mobile Phones", "13900", "8", 14, 6),
    ],
    "FM": [
        ("Pusti Atta 2kg", "Pusti", "Groceries", "145", "2", 120, 40),
        ("Rupchanda Soyabean Oil 2L", "Rupchanda", "Groceries", "375", "3", 95, 30),
        ("ACI Pure Salt 1kg", "ACI", "Groceries", "42", "0", 200, 60),
        ("Ispahani Mirzapore Tea 400g", "Ispahani", "Groceries", "320", "5", 85, 25),
        ("Nestle Nido Milk Powder 900g", "Nestle", "Groceries", "1150", "4", 40, 15),
        ("Radhuni Turmeric Powder 200g", "Radhuni", "Groceries", "95", "3", 140, 40),
        ("Kazi Farms Eggs 30 pcs", "Kazi Farms", "Groceries", "380", "2", 55, 20),
        ("Diamond Chinigura Rice 2kg", "Diamond", "Groceries", "290", "4", 70, 25),
        ("Fresh Refined Sugar 1kg", "Fresh", "Groceries", "135", "1", 110, 35),
        ("Pran Mango Juice 1L", "Pran", "Groceries", "120", "6", 90, 30),
        ("Dove Nourishing Body Wash 500ml", "Dove", "Beauty & Personal Care", "720", "10", 45, 15),
        ("Himalaya Neem Face Wash 150ml", "Himalaya", "Beauty & Personal Care", "380", "8", 62, 20),
        ("Garnier Micellar Water 400ml", "Garnier", "Beauty & Personal Care", "890", "12", 38, 12),
        ("Head & Shoulders Shampoo 650ml", "Head & Shoulders", "Beauty & Personal Care", "980", "9", 44, 15),
        ("Lifebuoy Handwash Refill 1L", "Lifebuoy", "Beauty & Personal Care", "340", "7", 75, 25),
        ("Vaseline Intensive Care Lotion 400ml", "Vaseline", "Beauty & Personal Care", "650", "11", 50, 18),
    ],
    "SH": [
        ("Aarong Half Silk Saree", "Aarong", "Fashion", "6500", "15", 12, 5),
        ("Ecstasy Slim Fit Denim Jeans", "Ecstasy", "Fashion", "2890", "20", 26, 10),
        ("Sailor Oxford Formal Shirt", "Sailor", "Fashion", "2250", "12", 30, 12),
        ("Apex Leather Formal Shoes", "Apex", "Fashion", "4200", "10", 18, 8),
        ("Bata Comfit Sandals", "Bata", "Fashion", "1450", "8", 40, 15),
        ("Le Reve Embroidered Kurti", "Le Reve", "Fashion", "2750", "18", 22, 10),
        ("Richman Cotton Polo Shirt", "Richman", "Fashion", "1350", "14", 45, 15),
        ("Yellow Woolen Shawl", "Yellow", "Fashion", "1950", "16", 20, 8),
        ("Atomic Habits Paperback", "Penguin", "Books", "720", "10", 35, 12),
        ("Sapiens Hardcover Edition", "Harper", "Books", "1350", "12", 20, 8),
        ("Feluda Samagra Volume 1", "Ananda", "Books", "950", "5", 28, 10),
        ("Rich Dad Poor Dad", "Plata", "Books", "560", "8", 42, 15),
        ("Deli Gel Pen Pack of 12", "Deli", "Stationery", "320", "10", 90, 30),
        ("Casio FX-991EX Scientific Calculator", "Casio", "Stationery", "2450", "6", 24, 10),
        ("Matador Ball Pen Box of 50", "Matador", "Stationery", "450", "12", 65, 20),
        ("Oxford A4 Spiral Notebook", "Oxford", "Stationery", "380", "9", 70, 25),
    ],
    "HC": [
        ("Walton WFC-3F5 Refrigerator", "Walton", "Home Appliances", "42500", "7", 6, 3),
        ("Singer 1.5 Ton Split AC", "Singer", "Home Appliances", "58900", "5", 4, 2),
        ("Miyako Rice Cooker 1.8L", "Miyako", "Home Appliances", "3250", "9", 22, 8),
        ("Vision Ceiling Fan 56 inch", "Vision", "Home Appliances", "3950", "6", 30, 10),
        ("Panasonic Microwave Oven 20L", "Panasonic", "Home Appliances", "14900", "8", 10, 4),
        ("Kiam Induction Cooker", "Kiam", "Home Appliances", "4600", "11", 16, 6),
        ("Sharp Air Cooler 30L", "Sharp", "Home Appliances", "12500", "10", 8, 4),
        ("RFL Plastic Storage Rack", "RFL", "Home & Kitchen", "2850", "12", 25, 10),
        ("Kiam Pressure Cooker 5L", "Kiam", "Home & Kitchen", "2650", "8", 28, 10),
        ("Lock & Lock Container Set 6 pcs", "Lock & Lock", "Home & Kitchen", "1950", "10", 34, 12),
        ("Bengal Dinner Set 32 pcs", "Bengal", "Home & Kitchen", "3400", "14", 15, 6),
        ("Tefal Nonstick Frying Pan 26cm", "Tefal", "Home & Kitchen", "2450", "9", 26, 10),
        ("Nivia Football Size 5", "Nivia", "Sports & Fitness", "1250", "10", 36, 12),
        ("Cosco Kashmir Willow Cricket Bat", "Cosco", "Sports & Fitness", "3200", "12", 14, 6),
        ("Kore Adjustable Dumbbell Set 20kg", "Kore", "Sports & Fitness", "5400", "15", 10, 4),
        ("Boldfit Skipping Rope with Counter", "Boldfit", "Sports & Fitness", "450", "8", 55, 20),
    ],
}

WAREHOUSES = {
    "TZ": "Dhaka - Tejgaon DC",
    "FM": "Dhaka - Savar DC",
    "SH": "Narayanganj DC",
    "HC": "Gazipur DC",
}


class Command(BaseCommand):
    help = (
        "Adds 3 more vendors, 2 more managers and 64 products to the existing "
        "demo data. Purely additive — nothing already in the database is "
        "modified or deleted. Safe to run more than once."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be created, then roll the transaction back.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        try:
            with transaction.atomic():
                summary = self._seed()
                self._report(summary, dry_run)
                if dry_run:
                    # Raising inside atomic() is the only reliable way to roll
                    # back; caught immediately below so the command still exits 0.
                    raise _DryRun()
        except _DryRun:
            self.stdout.write(self.style.WARNING("\nDry run — all changes rolled back."))

    # --- steps ---------------------------------------------------------

    def _seed(self):
        summary = {
            "vendors_created": 0,
            "managers_created": 0,
            "categories_created": 0,
            "products_created": 0,
            "products_skipped": 0,
        }

        # Users
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
                summary["vendors_created"] += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  vendor  {spec['email']} / {spec['password']}  ({spec['store']})"
                    )
                )
            vendors[spec["code"]] = user

        for spec in MANAGERS:
            _, created = User.objects.get_or_create(
                email=spec["email"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "role": User.Role.MANAGER,
                },
            )
            if created:
                manager = User.objects.get(email=spec["email"])
                manager.set_password(spec["password"])
                manager.save()
                summary["managers_created"] += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  manager {spec['email']} / {spec['password']}")
                )

        # Categories — already present from seed_demo_data, created here only
        # so this command also works on a database that never ran that one.
        categories = {}
        for name in CATEGORY_CODES:
            category, created = Category.objects.get_or_create(name=name)
            categories[name] = category
            if created:
                summary["categories_created"] += 1

        # Products
        now = timezone.now()
        for code, rows in CATALOG.items():
            vendor = vendors[code]
            for index, row in enumerate(rows, start=101):
                name, brand, category_name, mrp, discount, stock, reorder = row
                sku = f"{code}-{CATEGORY_CODES[category_name]}-{index:03d}"

                product, created = Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        "product_name": name,
                        "brand": brand,
                        "category": categories[category_name],
                        "mrp": Decimal(mrp),
                        "discount_percentage": Decimal(discount),
                        "vendor": vendor,
                        "description": (
                            f"{name} by {brand}. Listed by {vendor.full_name} "
                            f"under {category_name}."
                        ),
                    },
                )

                if not created:
                    # Someone may have edited this product since the last run.
                    # Leave it exactly as it is.
                    summary["products_skipped"] += 1
                    continue

                summary["products_created"] += 1

                # The post_save signal in apps/inventory already made a
                # zero-stock Inventory row; fill it in and log the movement
                # so the audit trail matches the quantity, the way a real
                # restock would.
                inventory, _ = Inventory.objects.get_or_create(product=product)
                inventory.quantity_in_stock = stock
                inventory.reorder_level = reorder
                inventory.warehouse_location = WAREHOUSES[code]
                inventory.last_restocked_at = now
                inventory.save()

                StockMovement.objects.create(
                    inventory=inventory,
                    movement_type=StockMovement.MovementType.RESTOCK,
                    quantity=stock,
                    note="Initial stock from seed_more_demo_data.",
                )

        return summary

    def _report(self, summary, dry_run):
        verb = "Would create" if dry_run else "Created"
        self.stdout.write("")
        self.stdout.write(f"{verb}:")
        self.stdout.write(f"  vendors    {summary['vendors_created']}")
        self.stdout.write(f"  managers   {summary['managers_created']}")
        self.stdout.write(f"  categories {summary['categories_created']}")
        self.stdout.write(f"  products   {summary['products_created']}")
        if summary["products_skipped"]:
            self.stdout.write(
                f"  skipped    {summary['products_skipped']} products already present"
            )

        self.stdout.write("")
        self.stdout.write("Catalog totals now in the database:")
        self.stdout.write(f"  vendors  {User.objects.filter(role=User.Role.VENDOR).count()}")
        self.stdout.write(f"  managers {User.objects.filter(role=User.Role.MANAGER).count()}")
        self.stdout.write(f"  products {Product.objects.count()}")


class _DryRun(Exception):
    """Internal sentinel used to roll back a --dry-run transaction."""