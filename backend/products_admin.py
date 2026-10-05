from django import forms
from django.contrib import admin

from .models import Category, InventoryAdjustment, Product, ProductImage, ProductVariant


class ProductVariantAdminForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["stock_quantity"].disabled = True
            self.fields["stock_quantity"].help_text = (
                "Stock is read-only after creation. Use Inventory → adjustments "
                "so every stock change is recorded in the audit history."
            )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    form = ProductVariantAdminForm
    extra = 1
    fields = ["name", "sku", "stock_quantity", "low_stock_threshold", "is_active"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "sort_order"]
    list_editable = ["is_active", "sort_order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "price", "inventory_units", "rating", "is_active", "is_featured", "is_new", "is_bestseller"]
    list_filter = ["category", "is_active", "is_featured", "is_new", "is_bestseller"]
    search_fields = ["name", "sku", "description", "fabric", "color"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProductVariantInline, ProductImageInline]

    @admin.display(description="Inventory")
    def inventory_units(self, obj):
        return sum(variant.stock_quantity for variant in obj.variants.all() if variant.is_active)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    form = ProductVariantAdminForm
    list_display = ["product", "name", "sku", "stock_quantity", "low_stock_threshold", "stock_status_display", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__name", "product__sku", "sku", "name"]
    list_select_related = ["product"]

    @admin.display(description="Stock status")
    def stock_status_display(self, obj):
        return obj.stock_status


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ["created_at", "variant", "quantity_before", "quantity_change", "quantity_after", "reason", "adjusted_by"]
    list_filter = ["reason", "created_at"]
    search_fields = ["variant__product__name", "variant__product__sku", "variant__name", "variant__sku", "note", "adjusted_by__username"]
    readonly_fields = ["variant", "quantity_before", "quantity_change", "quantity_after", "reason", "note", "adjusted_by", "created_at"]
    list_select_related = ["variant", "variant__product", "adjusted_by"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "sort_order", "is_primary", "url"]
    list_filter = ["is_primary"]
    search_fields = ["product__name", "alt_text"]


admin.site.site_header = "SVAASA Store Admin"
admin.site.site_title = "SVAASA Admin"
admin.site.index_title = "Store overview"
admin.site.index_template = "admin/dashboard_index.html"
