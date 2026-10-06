import json
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from orders.models import Order

from .models import Payment, Refund
from .refunds import create_refund_request, request_razorpay_refund, apply_refund_webhook
from .views import RazorpayWebhookAPIView
import hmac
import hashlib
from django.conf import settings

User = get_user_model()


class RazorpayRefundIntegrationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw", is_staff=True, is_superuser=True)
        self.customer = User.objects.create_user(username="buyer", password="pw")
        self.order = Order.objects.create(
            user=self.customer, email="buyer@example.com", full_name="Buyer", phone="9999999999",
            address_line1="Test", city="Chandigarh", state="Punjab", pincode="160001",
            shipping_method="standard", shipping_amount=Decimal("0"), subtotal=Decimal("4398.00"),
            total=Decimal("4398.00"), status="cancelled", payment_status="paid", stock_reserved=False,
        )
        self.payment = Payment.objects.create(
            order=self.order, gateway_order_id="order_test_refund", gateway_payment_id="pay_test_refund",
            status="captured", amount=Decimal("4398.00"), currency="INR",
        )
        self.refund = create_refund_request(order_id=self.order.id, requested_by=self.owner)

    @patch("payments.refunds.requests.post")
    def test_successful_razorpay_refund_marks_processed(self, post):
        post.return_value = Mock(
            status_code=200,
            json=lambda: {"id": "rfnd_test_123", "status": "processed", "amount": 439800, "currency": "INR", "payment_id": "pay_test_refund"},
            text="",
        )
        refund = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        self.assertEqual(refund.status, "processed")
        self.assertEqual(refund.gateway_refund_id, "rfnd_test_123")
        self.payment.refresh_from_db(); self.order.refresh_from_db()
        self.assertEqual(self.payment.status, "refunded")
        self.assertEqual(self.order.payment_status, "refunded")
        post.assert_called_once()
        self.assertIn("X-Refund-Idempotency", post.call_args.kwargs["headers"])

    @patch("payments.refunds.requests.post")
    def test_pending_gateway_response_stays_processing(self, post):
        post.return_value = Mock(
            status_code=200,
            json=lambda: {"id": "rfnd_test_pending", "status": "pending", "amount": 439800, "currency": "INR", "payment_id": "pay_test_refund"},
            text="",
        )
        refund = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        self.assertEqual(refund.status, "processing")
        self.payment.refresh_from_db(); self.order.refresh_from_db()
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.payment_status, "paid")

    @patch("payments.refunds.requests.post")
    def test_gateway_timeout_keeps_same_idempotency_key(self, post):
        import requests
        post.side_effect = requests.Timeout("timed out")
        key = self.refund.idempotency_key
        refund = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        refund.refresh_from_db()
        self.assertEqual(refund.status, "processing")
        self.assertEqual(str(refund.idempotency_key), str(key))

    @patch("payments.refunds.requests.post")
    def test_definitive_gateway_4xx_marks_failed(self, post):
        post.return_value = Mock(status_code=400, json=lambda: {"error": {"code": "BAD_REQUEST_ERROR"}}, text="bad")
        refund = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        self.assertEqual(refund.status, "failed")
        self.payment.refresh_from_db(); self.order.refresh_from_db()
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.payment_status, "paid")

    @patch("payments.refunds.requests.post")
    def test_retry_after_definitive_failure_uses_new_key(self, post):
        post.return_value = Mock(status_code=400, json=lambda: {"error": {"code": "BAD_REQUEST_ERROR"}}, text="bad")
        first = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        first_key = first.idempotency_key
        post.return_value = Mock(status_code=200, json=lambda: {"id": "rfnd_retry", "status": "processed", "amount": 439800, "currency": "INR"}, text="")
        second = request_razorpay_refund(self.refund.id, changed_by=self.owner)
        self.assertNotEqual(second.idempotency_key, first_key)
        self.assertEqual(second.status, "processed")

    def test_refund_processed_webhook_is_idempotent(self):
        self.refund.gateway_refund_id = "rfnd_webhook"
        self.refund.status = "processing"
        self.refund.save(update_fields=["gateway_refund_id", "status"])
        payload = {"id": "rfnd_webhook", "status": "processed", "amount": 439800, "payment_id": "pay_test_refund"}
        apply_refund_webhook(event="refund.processed", refund_entity=payload)
        apply_refund_webhook(event="refund.processed", refund_entity=payload)
        self.refund.refresh_from_db(); self.payment.refresh_from_db(); self.order.refresh_from_db()
        self.assertEqual(self.refund.status, "processed")
        self.assertEqual(self.payment.status, "refunded")
        self.assertEqual(self.order.payment_status, "refunded")

    def test_failed_refund_webhook_does_not_mark_order_refunded(self):
        self.refund.gateway_refund_id = "rfnd_failed"
        self.refund.status = "processing"
        self.refund.save(update_fields=["gateway_refund_id", "status"])
        apply_refund_webhook(event="refund.failed", refund_entity={"id": "rfnd_failed", "status": "failed"})
        self.refund.refresh_from_db(); self.payment.refresh_from_db(); self.order.refresh_from_db()
        self.assertEqual(self.refund.status, "failed")
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.payment_status, "paid")
