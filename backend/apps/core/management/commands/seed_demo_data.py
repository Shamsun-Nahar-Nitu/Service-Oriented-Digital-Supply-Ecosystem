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

        electronics, _ = Category.objects.get_or_create(name="Electronics")
        groceries, _ = Category.objects.get_or_create(name="Groceries")

        demo_products = [
            {
                "product_name": "Wireless Mouse",
                "sku": "WM-001",
                "brand": "Logitech",
                "category": electronics,
                "mrp": Decimal("1500.00"),
                "discount_percentage": Decimal("10.00"),
                "stock": 40,
            },
            {
                "product_name": "Mechanical Keyboard",
                "sku": "KB-002",
                "brand": "Keychron",
                "category": electronics,
                "mrp": Decimal("6500.00"),
                "discount_percentage": Decimal("5.00"),
                "stock": 15,
            },
            {
                "product_name": "Organic Coffee 500g",
                "sku": "GRO-010",
                "brand": "Local Roasters",
                "category": groceries,
                "mrp": Decimal("650.00"),
                "discount_percentage": Decimal("0.00"),
                "stock": 100,
            },
        ]

        for data in demo_products:
            stock = data.pop("stock")
            product, created = Product.objects.get_or_create(
                sku=data["sku"], defaults={**data, "vendor": vendor}
            )
            if created:
                Inventory.objects.filter(product=product).update(quantity_in_stock=stock)
                self.stdout.write(self.style.SUCCESS(f"Created product: {product.product_name}"))

        self.stdout.write(
            self.style.SUCCESS(
                "\nDemo data ready. Log in at /api/v1/auth/login/ with any account above."
            )
        )
