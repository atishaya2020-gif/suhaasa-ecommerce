from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Payment, Refund
from .refunds import create_refund_request, request_razorpay_refund, sync_razorpay_refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "gateway_order_id", "gateway_payment_id", "status", "amount", "created_at")
    list_filter = ("status", "gateway")
    search_fields = ("order__order_number", "gateway_order_id", "gateway_payment_id")
    readonly_fields = ("created_at", "updated_at")


class RefundAdminForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk:
            order = cleaned.get("order")
            if order:
                if order.status != "cancelled" or order.payment_status != "paid":
                    raise ValidationError(
                        "Refund requests currently require a cancelled order with payment status Paid."
                    )
                if order.refunds.filter(status__in={"pending", "processing", "processed"}).exists():
                    raise ValidationError("This order already has an active or completed refund.")
        return cleaned


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    form = RefundAdminForm
    list_display = (
        "created_at", "order", "amount", "reason", "status",
        "gateway_refund_id", "requested_by", "processed_by",
    )
    list_filter = ("status", "reason", "created_at")
    search_fields = ("order__order_number", "order__email", "gateway_refund_id", "note")
    readonly_fields = (
        "amount", "currency", "status", "gateway_refund_id", "idempotency_key",
        "created_at", "updated_at", "processed_at", "requested_by", "processed_by",
        "raw_response",
    )
    autocomplete_fields = ("order",)
    actions = ("process_selected_refunds", "sync_selected_refunds")

    @admin.action(description="Process selected refunds via Razorpay")
    def process_selected_refunds(self, request, queryset):
        processed = 0
        for refund in queryset:
            try:
                updated = request_razorpay_refund(refund.pk, changed_by=request.user)
                processed += 1
                self.message_user(
                    request,
                    f"{updated.order.order_number}: refund is {updated.get_status_display().lower()}.",
                    messages.SUCCESS,
                )
            except (ValidationError, Exception) as exc:
                self.message_user(request, f"Refund #{refund.pk} failed to process: {exc}", messages.ERROR)
        if not processed:
            self.message_user(request, "No refund was processed.", messages.WARNING)

    @admin.action(description="Sync selected refunds from Razorpay")
    def sync_selected_refunds(self, request, queryset):
        for refund in queryset:
            try:
                updated = sync_razorpay_refund(refund.pk, changed_by=request.user)
                self.message_user(
                    request,
                    f"{updated.order.order_number}: Razorpay reports {updated.get_status_display().lower()}.",
                    messages.SUCCESS,
                )
            except (ValidationError, Exception) as exc:
                self.message_user(request, f"Refund #{refund.pk} sync failed: {exc}", messages.ERROR)

    def save_model(self, request, obj, form, change):
        if not change:
            refund = create_refund_request(
                order_id=obj.order_id,
                requested_by=request.user,
                reason=obj.reason,
                note=obj.note,
            )
            obj.pk = refund.pk
            return
        super().save_model(request, obj, form, change)
