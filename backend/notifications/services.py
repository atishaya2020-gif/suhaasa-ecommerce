from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from orders.models import Order
from products.models import ProductVariant

from .models import Notification


def create_notification(*, recipient, kind, title, message, link="", dedupe_key):
    notification, _ = Notification.objects.get_or_create(
        recipient=recipient,
        dedupe_key=dedupe_key,
        defaults={
            "kind": kind,
            "title": title,
            "message": message,
            "link": link,
        },
    )
    return notification


def sync_owner_notifications(user):
    """Create durable owner alerts from current store state.

    This is intentionally state-based rather than tied to a single checkout
    code path, so existing orders/inventory immediately become visible and
    future admin visits pick up new events without email infrastructure.
    """
    if not user or not user.is_staff:
        return

    now = timezone.now()
    recent_since = now - timedelta(days=2)

    with transaction.atomic():
        recent_orders = Order.objects.filter(created_at__gte=recent_since).order_by("-created_at")[:12]
        for order in recent_orders:
            customer = order.full_name or order.email
            status_label = str(order.get_status_display())
            create_notification(
                recipient=user,
                kind="order",
                title="New order received",
                message=f"{order.order_number} from {customer} · {status_label} · ₹{order.total:,.0f}",
                link=f"/admin/orders/order/{order.pk}/change/",
                dedupe_key=f"order-created:{order.pk}",
            )

        paid_orders = Order.objects.filter(
            created_at__gte=recent_since,
            payment_status="paid",
        ).order_by("-created_at")[:12]
        for order in paid_orders:
            create_notification(
                recipient=user,
                kind="payment",
                title="Payment received",
                message=f"{order.order_number} has been paid · ₹{order.total:,.0f}.",
                link=f"/admin/payments/payment/{order.payment.pk}/change/" if hasattr(order, "payment") else f"/admin/orders/order/{order.pk}/change/",
                dedupe_key=f"payment-paid:{order.pk}",
            )

        for variant in ProductVariant.objects.select_related("product").filter(
            is_active=True,
            stock_quantity__gt=0,
            stock_quantity__lte=F("low_stock_threshold"),
        ):
            create_notification(
                recipient=user,
                kind="low_stock",
                title="Low stock",
                message=f"{variant.product.name} · {variant.name} has only {variant.stock_quantity} left.",
                link=f"/admin/products/productvariant/{variant.pk}/change/",
                dedupe_key=f"low-stock:{variant.pk}",
            )

        for variant in ProductVariant.objects.select_related("product").filter(
            is_active=True,
            stock_quantity=0,
        ):
            create_notification(
                recipient=user,
                kind="out_of_stock",
                title="Out of stock",
                message=f"{variant.product.name} · {variant.name} is out of stock.",
                link=f"/admin/products/productvariant/{variant.pk}/change/",
                dedupe_key=f"out-of-stock:{variant.pk}",
            )

