from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Order, OrderItem, OrderStatusHistory
from .services import ALLOWED_STATUS_TRANSITIONS, transition_order_status


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "product_sku", "variant_name", "unit_price", "quantity", "line_total")


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    can_delete = False
    fields = ("previous_status", "new_status", "changed_by", "note", "created_at")
    readonly_fields = fields
    ordering = ("created_at", "id")


class OrderAdminForm(forms.ModelForm):
    status_note = forms.CharField(
        required=False,
        label="Status note",
        help_text="Optional note recorded in the order status history.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.instance.status if self.instance.pk else None

        if self.instance.pk:
            allowed = ALLOWED_STATUS_TRANSITIONS.get(self.instance.status, set())
            choices = [(self.instance.status, dict(Order.STATUS_CHOICES)[self.instance.status])]
            choices += [
                (value, label)
                for value, label in Order.STATUS_CHOICES
                if value in allowed
            ]
            self.fields["status"].choices = choices

    def clean_status(self):
        new_status = self.cleaned_data["status"]
        if self.instance.pk and new_status != self._original_status:
            allowed = ALLOWED_STATUS_TRANSITIONS.get(self._original_status, set())
            if new_status not in allowed:
                raise ValidationError(
                    f"Invalid status transition: {self._original_status} → {new_status}."
                )
        return new_status


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ("order_number", "full_name", "email", "total", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status", "shipping_method", "created_at")
    search_fields = ("order_number", "email", "full_name", "phone")
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal", "shipping_amount", "total")
    inlines = [OrderStatusHistoryInline, OrderItemInline]

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if not change or not obj.pk or form.cleaned_data.get("status") == form._original_status:
            super().save_model(request, obj, form, change)
            return

        new_status = form.cleaned_data["status"]
        note = form.cleaned_data.get("status_note", "").strip()

        obj.status = form._original_status
        super().save_model(request, obj, form, change)

        transition_order_status(
            obj,
            new_status,
            changed_by=request.user,
            note=note,
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "variant_name", "quantity", "line_total")
    search_fields = ("order__order_number", "product_name", "product_sku")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "order", "previous_status", "new_status", "changed_by")
    list_filter = ("previous_status", "new_status", "created_at")
    search_fields = ("order__order_number", "order__email", "note", "changed_by__username")
    readonly_fields = ("order", "previous_status", "new_status", "changed_by", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
