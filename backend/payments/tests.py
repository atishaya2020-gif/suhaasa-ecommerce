import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from commerce.models import CartItem, GuestSession
from orders.models import Order, OrderItem
from products.models import Category, Product, ProductVariant

from .models import Payment


User = get_user_model()


class PaymentAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_payment_creation_requires_login(self):
        response = self.client.post("/api/payments/create/", {"order_number": "SH-TEST"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_payment_verification_requires_login(self):
        response = self.client.post("/api/payments/verify/", {"order_number": "SH-TEST"}, format="json")
        self.assertIn(response.status_code, (401, 403))


class PaymentStateTransitionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="payment-buyer", password="test-password")
        self.category = Category.objects.create(name="Payment Test", slug="payment-test")
        self.product = Product.objects.create(
            sku="PAYMENT-PRODUCT",
            name="Payment Test Product",
            slug="payment-test-product",
            category=self.category,
            description="Payment state-machine test product",
            price=Decimal("500.00"),
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Standard",
            sku="PAYMENT-V1",
            stock_quantity=0,
            is_active=True,
        )
        self.session = GuestSession.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user,
            session=self.session,
            email="buyer@example.com",
            full_name="Buyer",
            phone="9999999999",
            address_line1="Test address",
            city="Chandigarh",
            state="Punjab",
            pincode="160001",
            shipping_method="standard",
            shipping_amount=Decimal("99.00"),
            subtotal=Decimal("500.00"),
            total=Decimal("599.00"),
            status="pending_payment",
            payment_status="pending",
            stock_reserved=True,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            product_name=self.product.name,
            product_sku=self.product.sku,
            variant_name=self.variant.name,
            unit_price=self.product.price,
            quantity=1,
            line_total=self.product.price,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            gateway_order_id="order_test_123",
            amount=self.order.total,
            currency="INR",
            status="created",
        )

    def _post_webhook(self, event, payment_id="pay_test_123", order_id="order_test_123"):
        payload = {
            "event": event,
            "payload": {
                "payment": {
                    "entity": {
                        "id": payment_id,
                        "order_id": order_id,
                    }
                }
            },
        }
        body = json.dumps(payload).encode()
        signature = hmac.new(
            b"test-webhook-secret",
            body,
            hashlib.sha256,
        ).hexdigest()
        with override_settings(RAZORPAY_WEBHOOK_SECRET="test-webhook-secret"):
            return self.client.post(
                "/api/payments/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_RAZORPAY_SIGNATURE=signature,
            )

    def test_capture_after_reservation_release_does_not_fulfil(self):
        self.order.stock_reserved = False
        self.order.status = "cancelled"
        self.order.payment_status = "failed"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])

        response = self._post_webhook("payment.captured")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["status"], "reconciliation_required")
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.payment_status, "failed")
        self.assertEqual(self.order.status, "cancelled")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.variant.refresh_from_db(), None)
        self.assertEqual(self.variant.stock_quantity, 0)

    def test_late_failure_after_paid_order_does_not_corrupt_order(self):
        self.order.stock_reserved = False
        self.order.status = "placed"
        self.order.payment_status = "paid"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])
        self.payment.status = "captured"
        self.payment.gateway_payment_id = "pay_test_123"
        self.payment.save(update_fields=["status", "gateway_payment_id"])

        response = self._post_webhook("payment.failed")

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.variant.stock_quantity, 0)

    def test_duplicate_failed_webhook_releases_stock_only_once(self):
        response = self._post_webhook("payment.failed")
        self.assertEqual(response.status_code, 200)
        self.variant.refresh_from_db()
        first_stock = self.variant.stock_quantity
        self.order.refresh_from_db()
        self.assertEqual(first_stock, 1)
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.order.status, "cancelled")

        response = self._post_webhook("payment.failed")
        self.assertEqual(response.status_code, 200)
        self.variant.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, first_stock)
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.order.status, "cancelled")

    def test_duplicate_capture_webhook_is_idempotent(self):
        response = self._post_webhook("payment.captured")
        self.assertEqual(response.status_code, 200)
        self.variant.refresh_from_db()
        first_stock = self.variant.stock_quantity
        self.order.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")

        response = self._post_webhook("payment.captured")
        self.assertEqual(response.status_code, 200)
        self.variant.refresh_from_db()
        self.order.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.variant.stock_quantity, first_stock)
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")

    def test_failed_webhook_after_cancel_does_not_resurrect_order(self):
        self.order.stock_reserved = False
        self.order.status = "cancelled"
        self.order.payment_status = "failed"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])

        response = self._post_webhook("payment.failed")

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.assertEqual(self.order.payment_status, "failed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 0)

    def test_invalid_webhook_signature_rejected(self):
        payload = json.dumps({"event": "payment.captured", "payload": {}}).encode()
        with override_settings(RAZORPAY_WEBHOOK_SECRET="test-webhook-secret"):
            response = self.client.post(
                "/api/payments/webhook/",
                data=payload,
                content_type="application/json",
                HTTP_X_RAZORPAY_SIGNATURE="invalid",
            )
        self.assertEqual(response.status_code, 400)

    def test_missing_webhook_signature_rejected(self):
        payload = json.dumps({"event": "payment.captured", "payload": {}}).encode()
        with override_settings(RAZORPAY_WEBHOOK_SECRET="test-webhook-secret"):
            response = self.client.post(
                "/api/payments/webhook/",
                data=payload,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)


class PaymentEndpointStateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="verify-buyer", password="test-password")
        self.category = Category.objects.create(name="Verify Test", slug="verify-test")
        self.product = Product.objects.create(
            sku="VERIFY-PRODUCT",
            name="Verify Test Product",
            slug="verify-test-product",
            category=self.category,
            description="Verification test product",
            price=Decimal("500.00"),
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Standard",
            sku="VERIFY-V1",
            stock_quantity=0,
            is_active=True,
        )
        self.session = GuestSession.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user,
            session=self.session,
            email="verify@example.com",
            full_name="Verify Buyer",
            phone="9999999999",
            address_line1="Test address",
            city="Chandigarh",
            state="Punjab",
            pincode="160001",
            shipping_method="standard",
            shipping_amount=Decimal("99.00"),
            subtotal=Decimal("500.00"),
            total=Decimal("599.00"),
            status="pending_payment",
            payment_status="pending",
            stock_reserved=True,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            gateway_order_id="order_verify_123",
            amount=self.order.total,
            currency="INR",
            status="created",
        )
        self.client.force_authenticate(self.user)

    def _gateway(self):
        gateway = MagicMock()
        gateway.utility.verify_payment_signature.return_value = None
        gateway.payment.fetch.return_value = {
            "order_id": self.payment.gateway_order_id,
            "status": "captured",
        }
        return gateway

    @patch("payments.views.client")
    def test_verify_after_reservation_release_is_rejected(self, client_mock):
        self.order.stock_reserved = False
        self.order.status = "cancelled"
        self.order.payment_status = "failed"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])

        client_mock.return_value = self._gateway()
        response = self.client.post(
            "/api/payments/verify/",
            {
                "order_number": self.order.order_number,
                "razorpay_payment_id": "pay_verify_123",
                "razorpay_order_id": self.payment.gateway_order_id,
                "razorpay_signature": "valid",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, "failed")
        self.assertEqual(self.order.status, "cancelled")
        self.assertFalse(self.order.stock_reserved)

    @patch("payments.views.client")
    def test_verify_already_paid_order_is_idempotent(self, client_mock):
        self.order.stock_reserved = False
        self.order.status = "placed"
        self.order.payment_status = "paid"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])
        self.payment.status = "captured"
        self.payment.gateway_payment_id = "pay_verify_123"
        self.payment.save(update_fields=["status", "gateway_payment_id"])

        client_mock.return_value = self._gateway()
        response = self.client.post(
            "/api/payments/verify/",
            {
                "order_number": self.order.order_number,
                "razorpay_payment_id": "pay_verify_123",
                "razorpay_order_id": self.payment.gateway_order_id,
                "razorpay_signature": "valid",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")

    @patch("payments.views.client")
    def test_create_gateway_order_rejects_released_reservation(self, client_mock):
        self.order.stock_reserved = False
        self.order.status = "cancelled"
        self.order.payment_status = "failed"
        self.order.save(update_fields=["stock_reserved", "status", "payment_status"])

        gateway = self._gateway()
        client_mock.return_value = gateway
        response = self.client.post(
            "/api/payments/create/",
            {"order_number": self.order.order_number},
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        gateway.order.create.assert_not_called()
