from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction

from notifications.services import create_notification
from products.models import InventoryAdjustment, ProductVariant

from .models import Order, OrderStatusHistory


ALLOWED_STATUS_TRANSITIONS = {
    "pending_payment": {"placed", "cancelled"},
    "placed": {"processing", "cancelled"},
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def _notify_staff_of_status_change(order, history):
    User = get_user_model()
    old_label = dict(Order.STATUS_CHOICES).get(history.previous_status, "New")
    new_label = dict(Order.STATUS_CHOICES).get(history.new_status, history.new_status)

    title = f"Order {order.order_number} updated"
    if history.new_status == "cancelled":
        if order.payment_status == "paid":
            message = f"{order.order_number} was cancelled. Refund action is still required."
        else:
            message = f"{order.order_number} was cancelled."
    else:
        message = f"{order.order_number}: {old_label} → {new_label}."

    if history.note:
        message += f" {history.note}"

    for recipient in User.objects.filter(is_staff=True):
        create_notification(
            recipient=recipient,
            kind="order",
            title=title,
            message=message,
            link=f"/admin/orders/order/{order.pk}/change/",
            dedupe_key=f"order-status:{history.pk}",
        )


def _restore_cancelled_order_inventory(order):
    restored = 0

    for item in order.items.select_related("variant").all():
        if not item.variant_id:
            continue

        try:
            variant = ProductVariant.objects.select_for_update().get(pk=item.variant_id)
        except ProductVariant.DoesNotExist as exc:
            raise ObjectDoesNotExist(
                f"Order item variant {item.variant_id} for {order.order_number} no longer exists."
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
            note=f"Restored stock for cancelled order {order.order_number}",
        )
        restored += item.quantity

    return restored


def _transition_locked_order(order, new_status, *, changed_by=None, note=""):
    previous_status = order.status

    if previous_status == new_status:
        return order, None

    allowed = ALLOWED_STATUS_TRANSITIONS.get(previous_status, set())
    if new_status not in allowed:
        raise ValidationError(
            f"Invalid order status transition: {previous_status} → {new_status}."
        )

    if new_status == "cancelled":
        if previous_status == "pending_payment":
            release_reserved_inventory(order)
            if order.payment_status == "pending":
                order.payment_status = "failed"
        elif previous_status in {"placed", "processing"}:
            _restore_cancelled_order_inventory(order)

    order.status = new_status
    update_fields = ["status", "updated_at"]

    if new_status == "cancelled" and previous_status == "pending_payment":
        update_fields.append("payment_status")

    order.save(update_fields=update_fields)

    history = OrderStatusHistory.objects.create(
        order=order,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
        note=note,
    )
    _notify_staff_of_status_change(order, history)

    return order, history


def transition_order_status(order, new_status, *, changed_by=None, note=""):
    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(pk=order.pk)
        updated, _ = _transition_locked_order(
            locked_order,
            new_status,
            changed_by=changed_by,
            note=note,
        )
    return updated


def release_reserved_inventory(order):
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
