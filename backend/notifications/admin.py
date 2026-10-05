from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "title", "recipient", "kind", "is_read")
    list_filter = ("kind", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__username", "recipient__email")
    readonly_fields = ("recipient", "kind", "title", "message", "link", "dedupe_key", "is_read", "created_at", "read_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
