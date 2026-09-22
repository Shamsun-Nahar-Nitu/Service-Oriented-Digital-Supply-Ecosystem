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
                "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Sony WH-CH520 Wireless Headphones",
                "sku": "ELEC-SON-002",
                "brand": "Sony",
                "category": "Electronics",
                "mrp": "6500",
                "discount": "8",
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Logitech M331 Silent Wireless Mouse",
                "sku": "ELEC-LOG-003",
                "brand": "Logitech",
                "category": "Electronics",
                "mrp": "2200",
                "discount": "15",
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Samsung Galaxy A15 5G",
                "sku": "MOB-SAM-004",
                "brand": "Samsung",
                "category": "Mobile Phones",
                "mrp": "28999",
                "discount": "5",
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Xiaomi Redmi Note 13",
                "sku": "MOB-XIA-005",
                "brand": "Xiaomi",
                "category": "Mobile Phones",
                "mrp": "24999",
                "discount": "7",
                "stock": 14,
                "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Philips 1.5L Electric Kettle",
                "sku": "APP-PHI-006",
                "brand": "Philips",
                "category": "Home Appliances",
                "mrp": "2850",
                "discount": "10",
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f6?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Vision Blender 1.5L",
                "sku": "APP-VIS-007",
                "brand": "Vision",
                "category": "Home Appliances",
                "mrp": "4200",
                "discount": "6",
                "stock": 16,
                "image_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Fresh Miniket Rice 5kg",
                "sku": "GRO-FRE-008",
                "brand": "Fresh",
                "category": "Groceries",
                "mrp": "460",
                "discount": "3",
                "stock": 80,
                "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Teer Soybean Oil 5L",
                "sku": "GRO-TEE-009",
                "brand": "Teer",
                "category": "Groceries",
                "mrp": "890",
                "discount": "4",
                "stock": 65,
                "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Aarong Cotton Panjabi",
                "sku": "FAS-AAR-010",
                "brand": "Aarong",
                "category": "Fashion",
                "mrp": "3200",
                "discount": "18",
                "stock": 22,
                "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Yellow Canvas Handbag",
                "sku": "FAS-YEL-011",
                "brand": "Yellow",
                "category": "Fashion",
                "mrp": "1850",
                "discount": "10",
                "stock": 28,
                "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Nivea Sun Protect SPF 50",
                "sku": "BEA-NIV-012",
                "brand": "Nivea",
                "category": "Beauty & Personal Care",
                "mrp": "1150",
                "discount": "9",
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "The Alchemist Paperback",
                "sku": "BOK-PEN-013",
                "brand": "Penguin",
                "category": "Books",
                "mrp": "520",
                "discount": "0",
                "stock": 24,
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Bold: How to Be Brave",
                "sku": "BOK-RAN-014",
                "brand": "Random House",
                "category": "Books",
                "mrp": "780",
                "discount": "15",
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Decathlon Yoga Mat 6mm",
                "sku": "SPT-DEC-015",
                "brand": "Decathlon",
                "category": "Sports & Fitness",
                "mrp": "1750",
                "discount": "12",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "RFL Nonstick Cookware Set",
                "sku": "HOM-RFL-016",
                "brand": "RFL",
                "category": "Home & Kitchen",
                "mrp": "3850",
                "discount": "8",
                "stock": 14,
                "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Butterfly Stainless Saucepan",
                "sku": "HOM-BUT-017",
                "brand": "Butterfly",
                "category": "Home & Kitchen",
                "mrp": "1650",
                "discount": "5",
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1583778176476-4a8b02a64c01?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Matador A5 Hardcover Notebook",
                "sku": "STA-MAT-018",
                "brand": "Matador",
                "category": "Stationery",
                "mrp": "280",
                "discount": "20",
                "stock": 55,
                "image_url": "https://images.unsplash.com/photo-1585336261026-6757f541a674?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Faber-Castell Colour Pencil Set",
                "sku": "STA-FAB-019",
                "brand": "Faber-Castell",
                "category": "Stationery",
                "mrp": "650",
                "discount": "10",
                "stock": 32,
                "image_url": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&auto=format&fit=crop&q=80",
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