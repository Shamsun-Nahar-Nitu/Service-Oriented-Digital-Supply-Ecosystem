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
            {
                "name": "Anker Soundcore Bluetooth Speaker",
                "sku": "ELEC-ANK-001",
                "brand": "Anker",
                "category": "Electronics",
                "mrp": "5490",
                "discount": "12",
                "stock": 18,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/25/Sonos_PLAY5_Wireless_speaker_with_remote_control_as_size_comparison.jpeg",
            },
            {
                "name": "Sony WH-CH520 Wireless Headphones",
                "sku": "ELEC-SON-002",
                "brand": "Sony",
                "category": "Electronics",
                "mrp": "6500",
                "discount": "8",
                "stock": 12,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/56/2023_S%C5%82uchawki_Sony_WI-XB400_%281%29.jpg",
            },
            {
                "name": "Logitech M331 Silent Wireless Mouse",
                "sku": "ELEC-LOG-003",
                "brand": "Logitech",
                "category": "Electronics",
                "mrp": "2200",
                "discount": "15",
                "stock": 35,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/13/Mouse_mechanism_diagram.svg",
            },
            {
                "name": "Samsung Galaxy A15 5G",
                "sku": "MOB-SAM-004",
                "brand": "Samsung",
                "category": "Mobile Phones",
                "mrp": "28999",
                "discount": "5",
                "stock": 10,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Nokia_6630.png",
            },
            {
                "name": "Xiaomi Redmi Note 13",
                "sku": "MOB-XIA-005",
                "brand": "Xiaomi",
                "category": "Mobile Phones",
                "mrp": "24999",
                "discount": "7",
                "stock": 14,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Nokia_6630.png",
            },
            {
                "name": "Philips 1.5L Electric Kettle",
                "sku": "APP-PHI-006",
                "brand": "Philips",
                "category": "Home Appliances",
                "mrp": "2850",
                "discount": "10",
                "stock": 20,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/55/2023_Czajnik_elektryczny_N%27OVEEN.jpg",
            },
            {
                "name": "Vision Blender 1.5L",
                "sku": "APP-VIS-007",
                "brand": "Vision",
                "category": "Home Appliances",
                "mrp": "4200",
                "discount": "6",
                "stock": 16,
                "image_url": "",
            },
            {
                "name": "Fresh Miniket Rice 5kg",
                "sku": "GRO-FRE-008",
                "brand": "Fresh",
                "category": "Groceries",
                "mrp": "460",
                "discount": "3",
                "stock": 80,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Green_rice_sheaves_planted_in_a_paddy_field_with_long_shadows_at_golden_hour_in_Don_Det_Laos.jpg",
            },
            {
                "name": "Teer Soybean Oil 5L",
                "sku": "GRO-TEE-009",
                "brand": "Teer",
                "category": "Groceries",
                "mrp": "890",
                "discount": "4",
                "stock": 65,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/88/Cooking_oil_tanks_at_%E5%94%90%E6%8F%9A%E3%81%92_shop.jpg",
            },
            {
                "name": "Aarong Cotton Panjabi",
                "sku": "FAS-AAR-010",
                "brand": "Aarong",
                "category": "Fashion",
                "mrp": "3200",
                "discount": "18",
                "stock": 22,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Woman%27s_shirt_from_Kutch%2C_Gujarat%2C_India%2C_IMA_55114.jpg",
            },
            {
                "name": "Yellow Canvas Handbag",
                "sku": "FAS-YEL-011",
                "brand": "Yellow",
                "category": "Fashion",
                "mrp": "1850",
                "discount": "10",
                "stock": 28,
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b6/Handbag_%28drawing%29.jpg",
            },
            {
                "name": "Nivea Sun Protect SPF 50",
                "sku": "BEA-NIV-012",
                "brand": "Nivea",
                "category": "Beauty & Personal Care",
                "mrp": "1150",
                "discount": "9",
                "stock": 30,
                "image_url": "",
            },
            {
                "name": "The Alchemist Paperback",
                "sku": "BOK-PEN-013",
                "brand": "Penguin",
                "category": "Books",
                "mrp": "520",
                "discount": "0",
                "stock": 24,
                "image_url": "",
            },
            {
                "name": "Bold: How to Be Brave",
                "sku": "BOK-RAN-014",
                "brand": "Random House",
                "category": "Books",
                "mrp": "780",
                "discount": "15",
                "stock": 18,
                "image_url": "",
            },
            {
                "name": "Decathlon Yoga Mat 6mm",
                "sku": "SPT-DEC-015",
                "brand": "Decathlon",
                "category": "Sports & Fitness",
                "mrp": "1750",
                "discount": "12",
                "stock": 25,
                "image_url": "",
            },
            {
                "name": "RFL Nonstick Cookware Set",
                "sku": "HOM-RFL-016",
                "brand": "RFL",
                "category": "Home & Kitchen",
                "mrp": "3850",
                "discount": "8",
                "stock": 14,
                "image_url": "",
            },
            {
                "name": "Butterfly Stainless Saucepan",
                "sku": "HOM-BUT-017",
                "brand": "Butterfly",
                "category": "Home & Kitchen",
                "mrp": "1650",
                "discount": "5",
                "stock": 20,
                "image_url": "",
            },
            {
                "name": "Matador A5 Hardcover Notebook",
                "sku": "STA-MAT-018",
                "brand": "Matador",
                "category": "Stationery",
                "mrp": "280",
                "discount": "20",
                "stock": 55,
                "image_url": "",
            },
            {
                "name": "Faber-Castell Colour Pencil Set",
                "sku": "STA-FAB-019",
                "brand": "Faber-Castell",
                "category": "Stationery",
                "mrp": "650",
                "discount": "10",
                "stock": 32,
                "image_url": "",
            },
        ]

        self.stdout.write("Generating varied demo products...")
        for demo_product in demo_products:
            product, created = Product.objects.get_or_create(
                sku=demo_product["sku"],
                defaults={
                    "product_name": demo_product["name"],
                    "brand": demo_product["brand"],
                    "category": categories[demo_product["category"]],
                    "mrp": Decimal(demo_product["mrp"]),
                    "discount_percentage": Decimal(demo_product["discount"]),
                    "vendor": vendor,
                    "image_url": demo_product["image_url"],
                },
            )
            if not created and product.image_url != demo_product["image_url"]:
                Product.objects.filter(pk=product.pk).update(
                    image_url=demo_product["image_url"]
                )
            if created:
                Inventory.objects.filter(product=product).update(
                    quantity_in_stock=demo_product["stock"]
                )
                self.stdout.write(self.style.SUCCESS(f"Created product: {product.product_name}"))

        self.stdout.write(
            self.style.SUCCESS(
                "\nDemo data ready. Log in at /api/v1/auth/login/ with any account above."
            )
        )
