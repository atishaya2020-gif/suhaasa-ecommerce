from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "gateway_order_id", "gateway_payment_id", "status", "amount", "created_at")
    list_filter = ("status", "gateway")
    search_fields = ("order__order_number", "gateway_order_id", "gateway_payment_id")
    readonly_fields = ("created_at", "updated_at")
