from rest_framework import serializers
from .models import Category, InventoryAdjustment, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image_url", "sort_order"]


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "src", "url", "alt_text", "sort_order", "is_primary"]

    def get_src(self, obj):
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.url


class ProductVariantSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id", "name", "sku", "stock_quantity", "low_stock_threshold",
            "in_stock", "stock_status", "is_low_stock", "is_out_of_stock", "is_active",
        ]

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0 and obj.is_active


class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="variant.product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    adjusted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = [
            "id", "product", "variant_name", "sku", "quantity_before",
            "quantity_change", "quantity_after", "reason", "note",
            "adjusted_by", "adjusted_by_name", "created_at",
        ]
        read_only_fields = [
            "quantity_before", "quantity_after", "adjusted_by",
            "adjusted_by_name", "created_at",
        ]

    def get_adjusted_by_name(self, obj):
        if not obj.adjusted_by:
            return None
        return obj.adjusted_by.get_full_name() or obj.adjusted_by.username


class InventoryVariantSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id", "product", "product_sku", "name", "sku", "stock_quantity",
            "low_stock_threshold", "stock_status", "is_low_stock",
            "is_out_of_stock", "is_active",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    primary_image = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "slug", "category", "price", "compare_at_price",
            "fabric", "color", "rating", "review_count", "tag", "primary_image",
            "is_featured", "is_new", "is_bestseller", "description", "dimensions",
            "care", "highlights", "stock", "sizes",
        ]

    def get_stock(self, obj):
        return sum(variant.stock_quantity for variant in obj.variants.all() if variant.is_active)

    def get_sizes(self, obj):
        return [variant.name for variant in obj.variants.all() if variant.is_active]

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not image:
            return ""
        return ProductImageSerializer(image, context=self.context).data["src"]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "slug", "category", "description", "fabric", "color",
            "care", "dimensions", "highlights", "price", "compare_at_price", "rating",
            "review_count", "tag", "is_featured", "is_new", "is_bestseller", "variants", "images",
        ]
