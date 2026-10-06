from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from orders.models import Order

from .models import Payment, Refund
from .refunds import create_refund_request, transition_refund


User = get_user_model()


class RefundGroundworkTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="test-password",
            is_staff=True, is_superuser=True,
        )
        self.customer = User.objects.create_user(
            username="buyer", password="test-password",
        )
        self.order = Order.objects.create(
            user=self.customer,
            email="buyer@example.com",
            full_name="Buyer",
            phone="9999999999",
            address_line1="Test",
            city="Chandigarh",
            state="Punjab",
            pincode="160001",
            shipping_method="standard",
            shipping_amount=Decimal("99.00"),
            subtotal=Decimal("3999.00"),
            total=Decimal("4098.00"),
            status="cancelled",
            payment_status="paid",
            stock_reserved=False,
        )
        self.payment = Payment.objects.create(
            order=self.order,
            gateway_order_id="order_refund_test",
            gateway_payment_id="pay_refund_test",
            status="captured",
            amount=Decimal("4098.00"),
            currency="INR",
        )

    def test_create_refund_request_for_paid_cancelled_order(self):
        refund = create_refund_request(
            order_id=self.order.id,
            requested_by=self.owner,
            note="Customer cancellation — refund required.",
        )
        self.assertEqual(refund.status, "pending")
        self.assertEqual(refund.amount, Decimal("4098.00"))
        self.assertEqual(refund.requested_by, self.owner)

    def test_refund_request_is_idempotent_while_pending(self):
        first = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        second = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(self.order.refunds.count(), 1)

    def test_refund_requires_paid_captured_payment(self):
        self.payment.status = "failed"
        self.payment.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            create_refund_request(order_id=self.order.id, requested_by=self.owner)

    def test_refund_requires_cancelled_order_for_current_groundwork(self):
        self.order.status = "processing"
        self.order.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            create_refund_request(order_id=self.order.id, requested_by=self.owner)

    def test_processing_then_processed_marks_payment_and_order_refunded(self):
        refund = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        transition_refund(refund.id, "processing", changed_by=self.owner)
        transition_refund(
            refund.id, "processed", changed_by=self.owner,
            gateway_refund_id="rfnd_test_123",
        )

        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        refund.refresh_from_db()

        self.assertEqual(refund.status, "processed")
        self.assertEqual(refund.gateway_refund_id, "rfnd_test_123")
        self.assertEqual(self.payment.status, "refunded")
        self.assertEqual(self.order.payment_status, "refunded")

    def test_processed_requires_gateway_refund_id(self):
        refund = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        transition_refund(refund.id, "processing", changed_by=self.owner)
        with self.assertRaises(ValidationError):
            transition_refund(refund.id, "processed", changed_by=self.owner)

    def test_processed_refund_is_terminal(self):
        refund = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        transition_refund(refund.id, "processing", changed_by=self.owner)
        transition_refund(
            refund.id, "processed", changed_by=self.owner,
            gateway_refund_id="rfnd_terminal",
        )
        with self.assertRaises(ValidationError):
            transition_refund(refund.id, "processing", changed_by=self.owner)

    def test_failed_refund_does_not_change_paid_state(self):
        refund = create_refund_request(order_id=self.order.id, requested_by=self.owner)
        transition_refund(refund.id, "processing", changed_by=self.owner)
        transition_refund(refund.id, "failed", changed_by=self.owner)

        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        refund.refresh_from_db()

        self.assertEqual(refund.status, "failed")
        self.assertEqual(self.payment.status, "captured")
        self.assertEqual(self.order.payment_status, "paid")
