import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from commerce.models import GuestSession
from orders.models import Order, OrderItem
from orders.services import release_reserved_inventory
from products.models import Category, Product, ProductVariant

from .models import Payment


User = get_user_model()


class PaymentCaptureRegressionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="capture-regression", password="test-password")
        category = Category.objects.create(name="Capture Test", slug="capture-test")
        product = Product.objects.create(
            sku="CAPTURE-PRODUCT",
            name="Capture Test Product",
            slug="capture-test-product",
            category=category,
            description="Capture regression test",
            price=Decimal("500.00"),
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            name="Standard",
            sku="CAPTURE-V1",
            stock_quantity=0,
            is_active=True,
        )
        self.session = GuestSession.objects.create(user=self.user)
        self.order = Order.objects.create(
            user=self.user,
            session=self.session,
            email="capture@example.com",
            full_name="Capture Buyer",
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
            product=product,
            variant=self.variant,
            product_name=product.name,
            product_sku=product.sku,
            variant_name=self.variant.name,
            unit_price=product.price,
            quantity=1,
            line_total=product.price,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            gateway_order_id="order_capture_regression",
            amount=self.order.total,
            currency="INR",
            status="created",
        )

    def _webhook(self):
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_capture_regression",
                        "order_id": self.payment.gateway_order_id,
                    }
                }
            },
        }
        body = json.dumps(payload).encode()
        signature = hmac.new(b"test-webhook-secret", body, hashlib.sha256).hexdigest()
        with override_settings(RAZORPAY_WEBHOOK_SECRET="test-webhook-secret"):
            return self.client.post(
                "/api/payments/webhook/",
                data=body,
                content_type="application/json",
                HTTP_X_RAZORPAY_SIGNATURE=signature,
            )

    def test_capture_webhook_marks_order_paid_and_is_idempotent(self):
        response = self._webhook()
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.variant.refresh_from_db()
        first_stock = self.variant.stock_quantity

        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.status_history.count(), 1)

        response = self._webhook()
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.variant.refresh_from_db()

        self.assertEqual(self.variant.stock_quantity, first_stock)
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "placed")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.status_history.count(), 1)

    @patch("payments.views.client")
    def test_payment_verification_marks_order_paid_and_placed(self, client_mock):
        gateway = MagicMock()
        gateway.utility.verify_payment_signature.return_value = None
        gateway.payment.fetch.return_value = {
            "order_id": self.payment.gateway_order_id,
            "status": "captured",
        }
        client_mock.return_value = gateway
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/payments/verify/",
            {
                "order_number": self.order.order_number,
                "razorpay_payment_id": "pay_verify_regression",
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
        self.assertEqual(self.order.status_history.count(), 1)
    def test_late_capture_after_reservation_release_requires_reconciliation(self):
        release_reserved_inventory(self.order)
        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        released_stock = self.variant.stock_quantity

        response = self._webhook()

        self.assertEqual(response.status_code, 409)
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.variant.refresh_from_db()

        self.assertEqual(response.data["status"], "reconciliation_required")
        self.assertEqual(self.order.status, "pending_payment")
        self.assertEqual(self.order.payment_status, "pending")
        self.assertFalse(self.order.stock_reserved)
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.variant.stock_quantity, released_stock)
        self.assertEqual(self.order.status_history.count(), 0)

