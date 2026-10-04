from rest_framework import serializers

from payments.models import Payment

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id", "product_name", "product_sku", "variant_name", "image_url",
            "unit_price", "quantity", "line_total",
        ]


class PaymentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["gateway", "gateway_payment_id", "status", "amount", "currency", "created_at", "updated_at"]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = serializers.SerializerMethodField()

    def get_payment(self, obj):
        payment = getattr(obj, "payment", None)
        return PaymentSummarySerializer(payment).data if payment else None

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "email", "full_name", "phone", "address_line1", "address_line2",
            "city", "state", "pincode", "shipping_method", "shipping_amount",
            "subtotal", "total", "status", "payment_status", "created_at", "updated_at", "items", "payment",
        ]
        read_only_fields = fields
