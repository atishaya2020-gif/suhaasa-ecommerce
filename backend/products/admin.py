from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "sort_order"]
    list_editable = ["is_active", "sort_order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "price", "rating", "is_active", "is_featured", "is_new", "is_bestseller"]
    list_filter = ["category", "is_active", "is_featured", "is_new", "is_bestseller"]
    search_fields = ["name", "sku", "description", "fabric", "color"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "sku", "stock_quantity", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__name", "sku", "name"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "sort_order", "is_primary", "url"]
    list_filter = ["is_primary"]
    search_fields = ["product__name", "alt_text"]
