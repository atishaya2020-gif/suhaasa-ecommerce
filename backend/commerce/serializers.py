from rest_framework import serializers

from products.models import ProductVariant
from products.serializers import ProductListSerializer

from .models import CartItem, WishlistItem


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    variant_id = serializers.IntegerField(source="variant.id", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    unit_price = serializers.DecimalField(source="variant.product.price", max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.SerializerMethodField()
    stock_quantity = serializers.IntegerField(source="variant.stock_quantity", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "variant_id", "variant_name", "quantity",
            "unit_price", "line_total", "stock_quantity",
        ]

    def get_product(self, obj):
        return ProductListSerializer(obj.variant.product, context=self.context).data

    def get_line_total(self, obj):
        return obj.variant.product.price * obj.quantity


class WishlistItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "created_at"]

    def get_product(self, obj):
        return ProductListSerializer(obj.product, context=self.context).data
