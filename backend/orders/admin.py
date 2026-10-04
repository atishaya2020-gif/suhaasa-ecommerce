from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "product_sku", "variant_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "email", "total", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status", "shipping_method", "created_at")
    search_fields = ("order_number", "email", "full_name", "phone")
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal", "shipping_amount", "total")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "variant_name", "quantity", "line_total")
    search_fields = ("order__order_number", "product_name", "product_sku")
