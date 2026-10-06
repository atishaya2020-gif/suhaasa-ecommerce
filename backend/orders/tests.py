from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from commerce.models import CartItem, GuestSession
from notifications.models import Notification
from products.models import Category, Product, ProductVariant

from orders.admin import OrderAdminForm
from orders.models import Order, OrderStatusHistory, OrderItem
from orders.services import transition_order_status


User = get_user_model()


class OrderAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_order_creation_requires_login(self):
        response = self.client.post(
            "/api/orders/create/",
            {
                "name": "Guest Customer", "email": "guest@example.com", "phone": "9999999999",
                "address": "Test address", "city": "Chandigarh", "state": "Punjab", "pincode": "160001",
                "shipping_method": "standard",
            },
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_order_history_requires_login(self):
        response = self.client.get("/api/orders/")
        self.assertIn(response.status_code, (401, 403))


class InventoryReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="buyer", password="test-password")
        self.owner = User.objects.create_user(
            username="owner",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            sku="TEST-PRODUCT",
            name="Test Product",
            slug="test-product",
            category=self.category,
            description="Test",
            price=Decimal("500.00"),
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Standard",
            sku="TEST-V1",
            stock_quantity=1,
            is_active=True,
        )
        self.session = GuestSession.objects.create(user=self.user)
        CartItem.objects.create(session=self.session, variant=self.variant, quantity=1)
        self.client.force_authenticate(self.user)
        self.payload = {
            "name": "Buyer",
            "email": "buyer@example.com",
            "phone": "9999999999",
            "address": "Test address",
            "city": "Chandigarh",
            "state": "Punjab",
            "pincode": "160001",
            "shipping_method": "standard",
        }

    def test_checkout_reserves_stock_atomically(self):
        response = self.client.post("/api/orders/create/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)

        self.variant.refresh_from_db()
        order = Order.objects.get(order_number=response.data["order_number"])

        self.assertEqual(self.variant.stock_quantity, 0)
        self.assertTrue(order.stock_reserved)
        self.assertEqual(order.status, "pending_payment")
        self.assertEqual(order.status_history.count(), 1)
        self.assertEqual(order.status_history.first().new_status, "pending_payment")

    def test_second_order_cannot_oversell_last_unit(self):
        first = self.client.post("/api/orders/create/", self.payload, format="json")
        self.assertEqual(first.status_code, 201)

        self.session.cart_items.all().delete()
        CartItem.objects.create(session=self.session, variant=self.variant, quantity=1)

        second = self.client.post("/api/orders/create/", self.payload, format="json")
        self.assertEqual(second.status_code, 409)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 0)
        self.assertEqual(Order.objects.count(), 1)

    def test_cancel_pending_order_releases_reserved_stock_and_audits(self):
        response = self.client.post("/api/orders/create/", self.payload, format="json")
        order_number = response.data["order_number"]

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 0)

        cancelled = self.client.post(
            f"/api/orders/{order_number}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(cancelled.status_code, 200)

        self.variant.refresh_from_db()
        order = Order.objects.get(order_number=order_number)

        self.assertEqual(self.variant.stock_quantity, 1)
        self.assertFalse(order.stock_reserved)
        self.assertEqual(order.status, "cancelled")
        self.assertEqual(order.payment_status, "failed")
        self.assertEqual(order.status_history.count(), 2)
        self.assertEqual(order.status_history.last().new_status, "cancelled")
        self.assertTrue(Notification.objects.filter(recipient=self.owner, kind="order").exists())


class OrderLifecycleServiceTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        self.customer = User.objects.create_user(username="buyer", password="test-password")

        category = Category.objects.create(name="Kurtas", slug="kurtas")
        self.product = Product.objects.create(
            category=category,
            name="Lifecycle Kurta",
            slug="lifecycle-kurta",
            sku="LIFE-KRT",
            description="Test",
            price=Decimal("1000.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="M",
            sku="LIFE-KRT-M",
            stock_quantity=4,
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
            subtotal=Decimal("1000.00"),
            total=Decimal("1099.00"),
            status="placed",
            payment_status="paid",
            stock_reserved=False,
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            product_name=self.product.name,
            product_sku=self.product.sku,
            variant_name=self.variant.name,
            unit_price=self.product.price,
            quantity=2,
            line_total=Decimal("2000.00"),
        )

    def test_valid_forward_transitions_create_history_and_notification(self):
        for expected in ["processing", "shipped", "delivered"]:
            transition_order_status(
                self.order,
                expected,
                changed_by=self.owner,
                note=f"Moved to {expected}.",
            )
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, expected)

        history = list(self.order.status_history.all())
        self.assertEqual(
            [item.new_status for item in history],
            ["processing", "shipped", "delivered"],
        )
        self.assertEqual(OrderStatusHistory.objects.filter(order=self.order).count(), 3)
        self.assertEqual(
            Notification.objects.filter(recipient=self.owner, kind="order").count(),
            3,
        )

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValidationError):
            transition_order_status(
                self.order,
                "delivered",
                changed_by=self.owner,
            )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "placed")

    def test_paid_cancellation_restores_inventory_without_faking_refund(self):
        self.variant.stock_quantity = 2
        self.variant.save(update_fields=["stock_quantity"])

        transition_order_status(
            self.order,
            "cancelled",
            changed_by=self.owner,
            note="Customer cancellation approved.",
        )

        self.variant.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.variant.stock_quantity, 4)
        self.assertEqual(self.order.status, "cancelled")
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status_history.last().new_status, "cancelled")
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner,
                message__icontains="Refund action is still required",
            ).exists()
        )

    def test_terminal_orders_cannot_move_again(self):
        transition_order_status(self.order, "processing", changed_by=self.owner)
        transition_order_status(self.order, "shipped", changed_by=self.owner)
        transition_order_status(self.order, "delivered", changed_by=self.owner)

        with self.assertRaises(ValidationError):
            transition_order_status(self.order, "processing", changed_by=self.owner)


class OrderAdminFormTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="buyer",
            password="test-password",
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
            subtotal=Decimal("500.00"),
            total=Decimal("599.00"),
            status="placed",
            payment_status="paid",
        )

    def test_admin_form_only_offers_valid_next_states(self):
        form = OrderAdminForm(instance=self.order)
        self.assertEqual(
            [value for value, _ in form.fields["status"].choices],
            ["placed", "processing", "cancelled"],
        )

    def test_admin_form_rejects_invalid_jump(self):
        form = OrderAdminForm(
            data={"status": "delivered", "status_note": ""},
            instance=self.order,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)
