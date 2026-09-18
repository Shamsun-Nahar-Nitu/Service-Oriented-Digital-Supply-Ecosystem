"""
Backfills items_subtotal and platform_fee for transactions that were
created before those fields existed.

Historical orders never had a platform fee applied — the fee is a new
business rule going forward, not something we're retroactively charging
past customers. So for every existing row: items_subtotal is set equal to
the total_amount it already had (that total *was* the pure item subtotal
under the old rules), platform_fee is set to 0, and total_amount itself is
left completely untouched. Nothing about what a past customer paid, or
what a past order shows, changes.

Reversible: the reverse migration just zeroes both new fields back out,
which is what they defaulted to before this ran.
"""

from django.db import migrations, models


def backfill_forward(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    Transaction.objects.filter(items_subtotal=0, platform_fee=0).update(
        items_subtotal=models.F("total_amount")
    )


def backfill_backward(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    Transaction.objects.all().update(items_subtotal=0, platform_fee=0)


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0003_add_platform_fee_fields"),
    ]

    operations = [
        migrations.RunPython(backfill_forward, backfill_backward),
    ]
