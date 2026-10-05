import hmac
import hashlib
import json
from decimal import Decimal

import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.services import release_reserved_inventory
from .models import Payment


def client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def owned_order(request, order_number):
    if not request.user.is_authenticated:
        return None
    return Order.objects.filter(order_number=order_number, user=request.user).first()


class CreateRazorpayOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_number = str(request.data.get("order_number", "")).strip()
        if not order_number:
            return Response({"detail": "Order number is required."}, status=status.HTTP_400_BAD_REQUEST)

        gateway = client()
        if not gateway:
            return Response(
                {"detail": "Razorpay is not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to backend/.env."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Keep the order locked through creation of the local Payment record so a
        # concurrent cancellation cannot release the reservation between the
        # eligibility check and payment-order creation.
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .filter(order_number=order_number, user=request.user)
                .first()
            )
            if not order:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
            if order.payment_status == "paid":
                return Response({"detail": "Order is already paid."}, status=status.HTTP_409_CONFLICT)
            if order.status != "pending_payment" or not order.stock_reserved:
                return Response(
                    {"detail": "Order is no longer available for payment."},
                    status=status.HTTP_409_CONFLICT,
                )

            amount_paise = int((Decimal(order.total) * 100).quantize(Decimal("1")))
            try:
                remote = gateway.order.create({
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": order.order_number,
                    "notes": {"suhaasa_order_number": order.order_number},
                })
            except Exception as exc:
                return Response(
                    {"detail": f"Unable to create payment order: {exc}"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            payment, _ = Payment.objects.update_or_create(
                order=order,
                defaults={
                    "gateway_order_id": remote["id"],
                    "amount": order.total,
                    "currency": "INR",
                    "status": "created",
                    "raw_response": dict(remote),
                },
            )

        return Response({
            "key_id": settings.RAZORPAY_KEY_ID,
            "gateway_order_id": payment.gateway_order_id,
            "amount": amount_paise,
            "currency": "INR",
            "order_number": order.order_number,
            "name": order.full_name,
            "email": order.email,
            "phone": order.phone,
        })


class VerifyRazorpayPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_number = str(request.data.get("order_number", "")).strip()
        payment_id = str(request.data.get("razorpay_payment_id", "")).strip()
        gateway_order_id = str(request.data.get("razorpay_order_id", "")).strip()
        signature = str(request.data.get("razorpay_signature", "")).strip()

        order = owned_order(request, order_number)
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        payment = Payment.objects.filter(order=order, gateway_order_id=gateway_order_id).first()
        if not payment or not payment_id or not signature:
            return Response(
                {"detail": "Payment verification data is incomplete."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        gateway = client()
        if not gateway:
            return Response({"detail": "Razorpay is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            gateway.utility.verify_payment_signature({
                "razorpay_order_id": payment.gateway_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })
            remote_payment = gateway.payment.fetch(payment_id)
            if (
                remote_payment.get("order_id") != payment.gateway_order_id
                or remote_payment.get("status") != "captured"
            ):
                return Response(
                    {"detail": "Payment has not been captured."},
                    status=status.HTTP_409_CONFLICT,
                )
        except Exception:
            return Response({"detail": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            payment = Payment.objects.select_for_update().get(pk=payment.pk)

            # A retry after successful verification is a safe no-op. Do not
            # mutate inventory or recreate the order transition.
            if order.payment_status == "paid" and payment.status == "captured":
                from orders.serializers import OrderSerializer
                return Response(OrderSerializer(order).data)

            # The reservation is the inventory authorization for this payment.
            # Once it has been released, this payment cannot safely fulfil the
            # order even if Razorpay reports a captured payment.
            if not order.stock_reserved:
                return Response(
                    {
                        "detail": "Payment was captured, but the order's inventory reservation has already been released. Contact support.",
                        "status": "reconciliation_required",
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            payment.gateway_payment_id = payment_id
            payment.status = "captured"
            payment.raw_response = {
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": gateway_order_id,
            }
            payment.save(update_fields=["gateway_payment_id", "status", "raw_response", "updated_at"])

            order.payment_status = "paid"
            order.status = "placed"
            # Stock was already decremented at reservation time. Consuming the
            # reservation here must NOT decrement it again.
            order.stock_reserved = False
            order.save(update_fields=["payment_status", "status", "stock_reserved", "updated_at"])

            if order.session_id:
                order.session.cart_items.all().delete()

        from orders.serializers import OrderSerializer
        return Response(OrderSerializer(order).data)


class RazorpayWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        secret = settings.RAZORPAY_WEBHOOK_SECRET
        signature = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
        if not secret or not signature:
            return Response(
                {"detail": "Webhook signature configuration missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return Response({"detail": "Invalid webhook signature."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return Response({"detail": "Invalid webhook payload."}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get("event", "")
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        gateway_payment_id = entity.get("id", "")
        gateway_order_id = entity.get("order_id", "")
        payment = (
            Payment.objects.filter(gateway_order_id=gateway_order_id)
            .select_related("order")
            .first()
        )
        if not payment:
            return Response({"status": "ignored"})

        reconciliation_required = False

        with transaction.atomic():
            payment = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
            order = Order.objects.select_for_update().get(pk=payment.order_id)

            if gateway_payment_id:
                payment.gateway_payment_id = gateway_payment_id

            if event in {"payment.captured", "order.paid"}:
                # Already completed successfully: duplicate webhook is a no-op.
                if order.payment_status == "paid" and payment.status == "captured":
                    payment.raw_response = payload
                    payment.save(update_fields=["gateway_payment_id", "raw_response", "updated_at"])
                elif not order.stock_reserved:
                    # Payment may genuinely be captured, but the reservation was
                    # already released. Never silently fulfil an order without
                    # inventory. Record the gateway state for reconciliation.
                    payment.status = "captured"
                    payment.raw_response = payload
                    payment.save(update_fields=["gateway_payment_id", "status", "raw_response", "updated_at"])
                    reconciliation_required = True
                else:
                    payment.status = "captured"
                    payment.raw_response = payload
                    order.payment_status = "paid"
                    order.status = "placed"
                    # Reservation already consumed the stock. This only changes
                    # the reservation state; it does not touch stock_quantity.
                    order.stock_reserved = False
                    order.save(update_fields=["payment_status", "status", "stock_reserved", "updated_at"])
                    payment.save(update_fields=["gateway_payment_id", "status", "raw_response", "updated_at"])
                    if order.session_id:
                        order.session.cart_items.all().delete()

            elif event == "payment.failed":
                # A late failure must never downgrade a successfully paid order.
                if order.payment_status == "paid":
                    payment.raw_response = payload
                    payment.save(update_fields=["gateway_payment_id", "raw_response", "updated_at"])
                elif order.status == "cancelled":
                    # Cancellation is terminal. Do not resurrect it to
                    # pending_payment on a later gateway failure event.
                    payment.status = "failed"
                    payment.raw_response = payload
                    payment.save(update_fields=["gateway_payment_id", "status", "raw_response", "updated_at"])
                else:
                    payment.status = "failed"
                    release_reserved_inventory(order)
                    order.payment_status = "failed"
                    order.status = "cancelled"
                    order.save(update_fields=["payment_status", "status", "updated_at"])
                    payment.raw_response = payload
                    payment.save(update_fields=["gateway_payment_id", "status", "raw_response", "updated_at"])
            else:
                # Preserve the raw event for diagnostics without changing the
                # payment/order state for events this endpoint does not handle.
                payment.raw_response = payload
                payment.save(update_fields=["gateway_payment_id", "raw_response", "updated_at"])

        if reconciliation_required:
            return Response(
                {"status": "reconciliation_required"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response({"status": "ok"})

