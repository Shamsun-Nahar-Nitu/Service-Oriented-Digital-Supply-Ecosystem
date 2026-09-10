from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.category.models import Category
from apps.inventory.models import Inventory
from apps.products.models import Product
from apps.users.models import User


class Command(BaseCommand):
    help = "Seeds the database with demo users, categories, and products for local development."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "first_name": "Ada",
                "last_name": "Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Admin@12345")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin: admin@example.com / Admin@12345"))

        manager, created = User.objects.get_or_create(
            email="manager@example.com",
            defaults={"first_name": "Mo", "last_name": "Manager", "role": User.Role.MANAGER},
        )
        if created:
            manager.set_password("Manager@12345")
            manager.save()
            self.stdout.write(
                self.style.SUCCESS("Created manager: manager@example.com / Manager@12345")
            )

        vendor, created = User.objects.get_or_create(
            email="vendor@example.com",
            defaults={"first_name": "Val", "last_name": "Vendor", "role": User.Role.VENDOR},
        )
        if created:
            vendor.set_password("Vendor@12345")
            vendor.save()
            self.stdout.write(
                self.style.SUCCESS("Created vendor: vendor@example.com / Vendor@12345")
            )

        customer, created = User.objects.get_or_create(
            email="customer@example.com",
            defaults={"first_name": "Cara", "last_name": "Customer", "role": User.Role.CUSTOMER},
        )
        if created:
            customer.set_password("Customer@12345")
            customer.save()
            self.stdout.write(
                self.style.SUCCESS("Created customer: customer@example.com / Customer@12345")
            )

        category_names = [
            "Electronics",
            "Mobile Phones",
            "Home Appliances",
            "Groceries",
            "Fashion",
            "Beauty & Personal Care",
            "Books",
            "Sports & Fitness",
            "Home & Kitchen",
            "Stationery",
        ]
        categories = {
            name: Category.objects.get_or_create(name=name)[0] for name in category_names
        }

        demo_products = [
            ("Anker Soundcore Bluetooth Speaker", "ELEC-ANK-001", "Anker", "Electronics", "5490", "12", 18),
            ("Sony WH-CH520 Wireless Headphones", "ELEC-SON-002", "Sony", "Electronics", "6500", "8", 12),
            ("Logitech M331 Silent Wireless Mouse", "ELEC-LOG-003", "Logitech", "Electronics", "2200", "15", 35),
            ("Samsung Galaxy A15 5G", "MOB-SAM-004", "Samsung", "Mobile Phones", "28999", "5", 10),
            ("Xiaomi Redmi Note 13", "MOB-XIA-005", "Xiaomi", "Mobile Phones", "24999", "7", 14),
            ("Philips 1.5L Electric Kettle", "APP-PHI-006", "Philips", "Home Appliances", "2850", "10", 20),
            ("Vision Blender 1.5L", "APP-VIS-007", "Vision", "Home Appliances", "4200", "6", 16),
            ("Fresh Miniket Rice 5kg", "GRO-FRE-008", "Fresh", "Groceries", "460", "3", 80),
            ("Teer Soybean Oil 5L", "GRO-TEE-009", "Teer", "Groceries", "890", "4", 65),
            ("Aarong Cotton Panjabi", "FAS-AAR-010", "Aarong", "Fashion", "3200", "18", 22),
            ("Yellow Canvas Handbag", "FAS-YEL-011", "Yellow", "Fashion", "1850", "10", 28),
            ("Nivea Sun Protect SPF 50", "BEA-NIV-012", "Nivea", "Beauty & Personal Care", "1150", "9", 30),
            ("The Alchemist Paperback", "BOK-PEN-013", "Penguin", "Books", "520", "0", 24),
            ("Bold: How to Be Brave", "BOK-RAN-014", "Random House", "Books", "780", "15", 18),
            ("Decathlon Yoga Mat 6mm", "SPT-DEC-015", "Decathlon", "Sports & Fitness", "1750", "12", 25),
            ("RFL Nonstick Cookware Set", "HOM-RFL-016", "RFL", "Home & Kitchen", "3850", "8", 14),
            ("Butterfly Stainless Saucepan", "HOM-BUT-017", "Butterfly", "Home & Kitchen", "1650", "5", 20),
            ("Matador A5 Hardcover Notebook", "STA-MAT-018", "Matador", "Stationery", "280", "20", 55),
            ("Faber-Castell Colour Pencil Set", "STA-FAB-019", "Faber-Castell", "Stationery", "650", "10", 32),
        ]

        self.stdout.write("Generating varied demo products...")
        for name, sku, brand, category, mrp, discount, stock in demo_products:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "product_name": name,
                    "brand": brand,
                    "category": categories[category],
                    "mrp": Decimal(mrp),
                    "discount_percentage": Decimal(discount),
                    "vendor": vendor,
                },
            )
            if created:
                Inventory.objects.filter(product=product).update(quantity_in_stock=stock)
                self.stdout.write(self.style.SUCCESS(f"Created product: {product.product_name}"))

        self.stdout.write(
            self.style.SUCCESS(
                "\nDemo data ready. Log in at /api/v1/auth/login/ with any account above."
            )
        )
