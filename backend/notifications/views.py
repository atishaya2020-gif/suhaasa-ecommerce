from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Notification
from .services import sync_owner_notifications


@staff_member_required
@require_GET
def notification_list(request):
    sync_owner_notifications(request.user)
    try:
        limit = min(max(int(request.GET.get("limit", 30) or 30), 1), 50)
    except (TypeError, ValueError):
        limit = 30
    notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:limit]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({
        "unread_count": unread_count,
        "notifications": [
            {
                "id": item.id,
                "kind": item.kind,
                "title": item.title,
                "message": item.message,
                "link": item.link,
                "is_read": item.is_read,
                "created_at": item.created_at.isoformat(),
            }
            for item in notifications
        ],
    })


@staff_member_required
@require_POST
def mark_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
    return JsonResponse({"ok": True, "id": notification.id})


@staff_member_required
@require_POST
def mark_all_read(request):
    now = timezone.now()
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=now)
    return JsonResponse({"ok": True})
