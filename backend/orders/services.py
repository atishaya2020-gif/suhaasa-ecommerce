from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from products.models import InventoryAdjustment, ProductVariant

from .models import Order


def release_reserved_inventory(order):
    """Release inventory reserved by a pending-payment order exactly once.

    Returns the number of order items released. The order is locked by the
    caller when this is used inside a larger transaction.
    """
    if not order.stock_reserved:
        return 0

    released = 0
    items = order.items.select_related("variant").all()
    for item in items:
        if not item.variant_id:
            continue
        try:
            variant = ProductVariant.objects.select_for_update().get(pk=item.variant_id)
        except ProductVariant.DoesNotExist as exc:
            # A reservation cannot be safely released if its inventory row
            # disappeared. Let the surrounding transaction roll back instead
            # of silently clearing stock_reserved and losing accounting data.
            raise ObjectDoesNotExist(
                f"Reserved variant {item.variant_id} for order {order.order_number} no longer exists."
            ) from exc

        before = variant.stock_quantity
        variant.stock_quantity = before + item.quantity
        variant.save(update_fields=["stock_quantity"])
        InventoryAdjustment.objects.create(
            variant=variant,
            quantity_before=before,
            quantity_change=item.quantity,
            quantity_after=variant.stock_quantity,
            reason="order_adjustment",
            note=f"Released reservation for cancelled/failed order {order.order_number}",
        )
        released += item.quantity

    order.stock_reserved = False
    order.save(update_fields=["stock_reserved", "updated_at"])
    return released
