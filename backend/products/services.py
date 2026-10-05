from django.core.exceptions import ValidationError
from django.db import transaction

from .models import InventoryAdjustment, ProductVariant


def adjust_inventory(*, variant_id, quantity_change, reason, note="", adjusted_by=None):
    """Atomically change a variant's available stock and record the audit row.

    The variant row is the concurrency boundary. Every stock mutation outside
    order reservation/release should go through this helper so stock can never
    become negative and every manual/lifecycle adjustment is auditable.
    """
    if quantity_change == 0:
        raise ValidationError("quantity_change cannot be zero.")

    valid_reasons = dict(InventoryAdjustment.REASON_CHOICES)
    if reason not in valid_reasons:
        raise ValidationError("Invalid inventory adjustment reason.")

    with transaction.atomic():
        variant = ProductVariant.objects.select_for_update().select_related("product").get(pk=variant_id)
        before = variant.stock_quantity
        after = before + quantity_change
        if after < 0:
            raise ValidationError(f"Stock cannot become negative. Available stock: {before}.")

        variant.stock_quantity = after
        variant.save(update_fields=["stock_quantity"])
        adjustment = InventoryAdjustment.objects.create(
            variant=variant,
            quantity_before=before,
            quantity_change=quantity_change,
            quantity_after=after,
            reason=reason,
            note=note,
            adjusted_by=adjusted_by,
        )

    return variant, adjustment
