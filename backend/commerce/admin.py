from django.contrib import admin

from .models import CartItem, GuestSession, WishlistItem


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = ("token", "created_at", "updated_at")
    readonly_fields = ("token", "created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("session", "variant", "quantity", "updated_at")
    list_select_related = ("session", "variant", "variant__product")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("session", "product", "created_at")
    list_select_related = ("session", "product")
