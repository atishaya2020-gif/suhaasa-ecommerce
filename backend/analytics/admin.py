from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("created_at", "path", "device_type", "utm_source", "utm_medium")
    list_filter = ("device_type", "utm_source", "created_at")
    search_fields = ("path", "referrer", "utm_source", "utm_medium", "utm_campaign")
    readonly_fields = (
        "visitor_id", "session_id", "path", "referrer", "utm_source",
        "utm_medium", "utm_campaign", "device_type", "created_at",
    )
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
