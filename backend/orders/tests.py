from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from commerce.models import CartItem, GuestSession
from products.models import Category, Product, ProductVariant
from orders.models import Order


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
            }, format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_order_history_requires_login(self):
        response = self.client.get("/api/orders/")
        self.assertIn(response.status_code, (401, 403))


class InventoryReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="buyer", password="test-password")
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            sku="TEST-PRODUCT", name="Test Product", slug="test-product", category=self.category,
            description="Test", price=Decimal("500.00"), is_active=True,
        )
        self.variant = ProductVariant.objects.create(product=self.product, name="Standard", sku="TEST-V1", stock_quantity=1, is_active=True)
        self.session = GuestSession.objects.create(user=self.user)
        CartItem.objects.create(session=self.session, variant=self.variant, quantity=1)
        self.client.force_authenticate(self.user)
        self.payload = {
            "name": "Buyer", "email": "buyer@example.com", "phone": "9999999999",
            "address": "Test address", "city": "Chandigarh", "state": "Punjab", "pincode": "160001",
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

    def test_cancel_pending_order_releases_reserved_stock(self):
        response = self.client.post("/api/orders/create/", self.payload, format="json")
        order_number = response.data["order_number"]
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 0)
        cancelled = self.client.post(f"/api/orders/{order_number}/cancel/", {}, format="json")
        self.assertEqual(cancelled.status_code, 200)
        self.variant.refresh_from_db()
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(self.variant.stock_quantity, 1)
        self.assertFalse(order.stock_reserved)
        self.assertEqual(order.status, "cancelled")
