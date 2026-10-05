from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from accounts.models import CustomerProfile
from orders.models import Order

from .models import PageView


def _clean(value, max_length):
    if value is None:
        return ""
    return str(value).strip()[:max_length]


def _device(value):
    value = _clean(value, 20).lower()
    return value if value in {"mobile", "tablet", "desktop"} else "unknown"


@require_POST
def track_page_view(request):
    payload = request.body
    try:
        import json
        data = json.loads(payload or b"{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Invalid JSON."}, status=400)

    visitor_id = _clean(data.get("visitor_id"), 64)
    session_id = _clean(data.get("session_id"), 64)
    path = _clean(data.get("path"), 500)
    if not visitor_id or not session_id or not path.startswith("/"):
        return JsonResponse({"detail": "visitor_id, session_id and a valid path are required."}, status=400)

    PageView.objects.create(
        visitor_id=visitor_id,
        session_id=session_id,
        path=path,
        referrer=_clean(data.get("referrer"), 1000),
        utm_source=_clean(data.get("utm_source"), 120),
        utm_medium=_clean(data.get("utm_medium"), 120),
        utm_campaign=_clean(data.get("utm_campaign"), 180),
        device_type=_device(data.get("device_type")),
    )
    return JsonResponse({"ok": True})


@staff_member_required
@require_GET
def dashboard_data(request):
    now = timezone.now()
    period = request.GET.get("period", "30")
    try:
        days = max(1, min(int(period), 90))
    except (TypeError, ValueError):
        days = 30
    since = now - timedelta(days=days)

    traffic = PageView.objects.filter(created_at__gte=since)
    orders = Order.objects.filter(created_at__gte=since)
    paid_orders = orders.filter(payment_status="paid")

    daily = list(
        traffic.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(pageviews=Count("id"), sessions=Count("session_id", distinct=True), visitors=Count("visitor_id", distinct=True))
        .order_by("day")
    )

    top_pages = list(
        traffic.values("path")
        .annotate(pageviews=Count("id"), visitors=Count("visitor_id", distinct=True))
        .order_by("-pageviews", "path")[:10]
    )
    referrers = list(
        traffic.exclude(referrer="").values("referrer")
        .annotate(visits=Count("id"))
        .order_by("-visits", "referrer")[:10]
    )
    sources = list(
        traffic.exclude(utm_source="").values("utm_source")
        .annotate(visits=Count("id"))
        .order_by("-visits", "utm_source")[:10]
    )
    devices = list(
        traffic.values("device_type")
        .annotate(visits=Count("id"))
        .order_by("-visits")
    )

    revenue = paid_orders.aggregate(total=Sum("total"))["total"] or 0

    recent_orders = list(
        orders.values(
            "id", "order_number", "full_name", "total", "status", "payment_status", "created_at"
        )[:8]
    )
    status_breakdown = list(
        orders.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    result = {
        "period_days": days,
        "traffic": {
            "pageviews": traffic.count(),
            "sessions": traffic.values("session_id").distinct().count(),
            "visitors": traffic.values("visitor_id").distinct().count(),
            "daily": [
                {**item, "day": item["day"].isoformat()} for item in daily
            ],
            "top_pages": top_pages,
            "referrers": referrers,
            "sources": sources,
            "devices": devices,
        },
        "commerce": {
            "orders": orders.count(),
            "paid_orders": paid_orders.count(),
            "revenue": str(revenue),
            "customers": CustomerProfile.objects.filter(user__date_joined__gte=since).count(),
            "recent_orders": [
                {
                    **item,
                    "total": str(item["total"]),
                    "created_at": item["created_at"].isoformat(),
                    "admin_url": reverse("admin:orders_order_change", args=[item["id"]]),
                }
                for item in recent_orders
            ],
            "status_breakdown": status_breakdown,
        },
        "inventory": {
            "low_stock_variants": 0,
            "out_of_stock_variants": 0,
        },
    }

    from products.models import ProductVariant
    low_stock_qs = ProductVariant.objects.filter(
        is_active=True, stock_quantity__gt=0, stock_quantity__lte=F("low_stock_threshold")
    ).select_related("product").order_by("stock_quantity", "product__name")
    result["inventory"]["low_stock_variants"] = low_stock_qs.count()
    result["inventory"]["out_of_stock_variants"] = ProductVariant.objects.filter(is_active=True, stock_quantity=0).count()
    result["inventory"]["low_stock"] = [
        {
            "product": item.product.name,
            "variant": item.name,
            "sku": item.sku,
            "stock_quantity": item.stock_quantity,
        }
        for item in low_stock_qs[:8]
    ]
    return JsonResponse(result)
