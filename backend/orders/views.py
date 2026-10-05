from decimal import Decimal
from products.models import ProductVariant
from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from commerce.views import get_guest_session, session_payload
from products.models import InventoryAdjustment
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .services import release_reserved_inventory


FREE_SHIPPING_THRESHOLD = Decimal("1499.00")
STANDARD_SHIPPING = Decimal("99.00")
EXPRESS_SHIPPING = Decimal("149.00")


def _validate_payload(request):
    required = ["name", "email", "phone", "address", "city", "state", "pincode", "shipping_method"]
    missing = [key for key in required if not str(request.data.get(key, "")).strip()]
    if missing:
        return None, {"detail": f"Missing required fields: {', '.join(missing)}."}
    method = str(request.data.get("shipping_method", "")).strip().lower()
    if method not in {"standard", "express"}:
        return None, {"detail": "shipping_method must be standard or express."}
    return method, None


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shipping_method, error = _validate_payload(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        session = get_guest_session(request)
        cart_items = list(session.cart_items.select_related("variant__product").all())
        if not cart_items:
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            locked_items = []
            subtotal = Decimal("0.00")
            for cart_item in cart_items:
                # Lock the cart row and variant row in the same transaction. The
                # variant lock is the authoritative concurrency boundary for stock.
                locked_cart_item = session.cart_items.select_related("variant__product").select_for_update().get(pk=cart_item.pk)
                variant = ProductVariant.objects.select_related("product").select_for_update().get(pk=locked_cart_item.variant_id)
                if not variant.is_active or not variant.product.is_active:
                    return Response({"detail": f"{variant.product.name} is no longer available."}, status=status.HTTP_409_CONFLICT)
                if locked_cart_item.quantity > variant.stock_quantity:
                    return Response({"detail": f"Only {variant.stock_quantity} units are available for {variant.name}."}, status=status.HTTP_409_CONFLICT)
                line_total = variant.product.price * locked_cart_item.quantity
                subtotal += line_total
                locked_items.append((locked_cart_item, variant, line_total))

            shipping_amount = EXPRESS_SHIPPING if shipping_method == "express" else (Decimal("0.00") if subtotal >= FREE_SHIPPING_THRESHOLD else STANDARD_SHIPPING)
            order = Order.objects.create(
                user=request.user,
                session=session,
                email=str(request.data["email"]).strip().lower(),
                full_name=str(request.data["name"]).strip(),
                phone=str(request.data["phone"]).strip(),
                address_line1=str(request.data["address"]).strip(),
                address_line2=str(request.data.get("address_line2", "")).strip(),
                city=str(request.data["city"]).strip(),
                state=str(request.data["state"]).strip(),
                pincode=str(request.data["pincode"]).strip(),
                shipping_method=shipping_method,
                shipping_amount=shipping_amount,
                subtotal=subtotal,
                total=subtotal + shipping_amount,
                status="pending_payment",
                payment_status="pending",
                stock_reserved=True,
            )

            for cart_item, variant, line_total in locked_items:
                primary_image = variant.product.images.filter(is_primary=True).first() or variant.product.images.first()
                image_url = ""
                if primary_image:
                    image_url = primary_image.url or (primary_image.image.url if primary_image.image else "")
                OrderItem.objects.create(
                    order=order,
                    product=variant.product,
                    variant=variant,
                    product_name=variant.product.name,
                    product_sku=variant.product.sku,
                    variant_name=variant.name,
                    image_url=image_url,
                    unit_price=variant.product.price,
                    quantity=cart_item.quantity,
                    line_total=line_total,
                )
                before = variant.stock_quantity
                variant.stock_quantity = before - cart_item.quantity
                variant.save(update_fields=["stock_quantity"])
                InventoryAdjustment.objects.create(
                    variant=variant,
                    quantity_before=before,
                    quantity_change=-cart_item.quantity,
                    quantity_after=variant.stock_quantity,
                    reason="order_adjustment",
                    note=f"Reserved stock for pending-payment order {order.order_number}",
                )

            # Keep the cart until payment is verified successfully. Stock is
            # reserved separately so a failed/cancelled payment can release it.

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelPendingOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_number):
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(
                user=request.user,
                order_number=order_number,
            ).first()
            if not order:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
            if order.status == "cancelled":
                return Response(OrderSerializer(order).data)
            if order.status != "pending_payment" or order.payment_status != "pending":
                return Response({"detail": "Only pending-payment orders can be cancelled."}, status=status.HTTP_409_CONFLICT)

            release_reserved_inventory(order)
            order.status = "cancelled"
            order.payment_status = "failed"
            order.save(update_fields=["status", "payment_status", "updated_at"])

        return Response(OrderSerializer(order).data)


class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items").select_related("payment")
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number):
        order = Order.objects.filter(user=request.user, order_number=order_number).prefetch_related("items").select_related("payment").first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)


class ReorderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_number):
        order = Order.objects.filter(user=request.user, order_number=order_number).prefetch_related("items").first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        session = get_guest_session(request)
        added = []
        skipped = []
        with transaction.atomic():
            for old_item in order.items.all():
                variant = old_item.variant
                if not variant or not variant.is_active or not variant.product.is_active:
                    skipped.append({"name": old_item.product_name, "variant": old_item.variant_name, "reason": "No longer available"})
                    continue
                existing = session.cart_items.select_for_update().filter(variant=variant).first()
                current = existing.quantity if existing else 0
                available = max(0, variant.stock_quantity - current)
                if available <= 0:
                    skipped.append({"name": old_item.product_name, "variant": variant.name, "reason": "Out of stock"})
                    continue
                quantity = min(old_item.quantity, available)
                if existing:
                    existing.quantity += quantity
                    existing.save(update_fields=["quantity", "updated_at"])
                else:
                    from commerce.models import CartItem
                    CartItem.objects.create(session=session, variant=variant, quantity=quantity)
                added.append({"name": variant.product.name, "variant": variant.name, "quantity": quantity})
        return Response({"commerce": session_payload(session), "added": added, "skipped": skipped})
