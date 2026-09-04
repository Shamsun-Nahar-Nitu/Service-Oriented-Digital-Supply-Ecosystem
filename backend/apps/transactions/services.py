from django.db import transaction as db_transaction
from rest_framework.exceptions import ValidationError

from apps.inventory.models import StockMovement

from .models import Transaction, TransactionItem


class CheckoutService:
    """
    Encapsulates the checkout workflow so the view/serializer stay thin:

    1. Validates that every requested product has enough stock.
    2. Creates the Transaction and its TransactionItem rows, snapshotting
       the current selling price.
    3. Decrements inventory and records a StockMovement per line item.

    Everything runs inside a single atomic block, so a stock shortfall on
    item 3 of 5 rolls back the whole order instead of leaving a half-created
    transaction behind.
    """

    def __init__(self, user, items, shipping_address=""):
        """
        `items` is a list of {"product": Product instance, "quantity": int}.
        """
        self.user = user
        self.items = items
        self.shipping_address = shipping_address

    @db_transaction.atomic
    def execute(self) -> Transaction:
        transaction_obj = Transaction.objects.create(
            user=self.user, shipping_address=self.shipping_address
        )

        for entry in self.items:
            product = entry["product"]
            quantity = entry["quantity"]

            if not product.is_purchasable:
                raise ValidationError(
                    f"'{product.product_name}' is not currently available for purchase."
                )

            inventory = product.inventory
            if inventory.quantity_in_stock < quantity:
                raise ValidationError(
                    f"Only {inventory.quantity_in_stock} unit(s) of "
                    f"'{product.product_name}' are available."
                )

            TransactionItem.objects.create(
                transaction=transaction_obj,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
            )

            inventory.quantity_in_stock -= quantity
            inventory.save(update_fields=["quantity_in_stock", "updated_date"])

            StockMovement.objects.create(
                inventory=inventory,
                movement_type=StockMovement.MovementType.SALE,
                quantity=-quantity,
                note=f"Sold via transaction {transaction_obj.transaction_number}",
            )

        transaction_obj.recalculate_total()
        return transaction_obj
