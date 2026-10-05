from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Category, Product, ProductVariant


class InventoryAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser(
            username="inventory-admin",
            email="inventory@example.com",
            password="test-password-123",
        )
        self.customer = user_model.objects.create_user(
            username="inventory-customer",
            password="test-password-123",
        )
        category = Category.objects.create(name="Test", slug="test")
        product = Product.objects.create(
            sku="TEST-001",
            name="Test Product",
            slug="test-product",
            category=category,
            description="Inventory test product",
            price="100.00",
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            name="Standard",
            sku="TEST-001-STD",
            stock_quantity=3,
            low_stock_threshold=5,
        )

    def test_inventory_endpoints_require_admin(self):
        for path in [
            "/api/products/inventory/dashboard/",
            "/api/products/inventory/variants/",
            "/api/products/inventory/history/",
        ]:
            response = self.client.get(path)
            self.assertIn(response.status_code, [401, 403])

        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/products/inventory/dashboard/")
        self.assertEqual(response.status_code, 403)

    def test_dashboard_reports_low_stock(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/products/inventory/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_variants"], 1)
        self.assertEqual(response.data["low_stock_variants"], 1)
        self.assertEqual(response.data["out_of_stock_variants"], 0)
        self.assertEqual(response.data["total_units"], 3)

    def test_stock_adjustment_records_history(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/products/inventory/adjustments/",
            {
                "variant_id": self.variant.id,
                "quantity_change": 10,
                "reason": "restock",
                "note": "Test restock",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 13)
        self.assertEqual(response.data["adjustment"]["quantity_before"], 3)
        self.assertEqual(response.data["adjustment"]["quantity_after"], 13)

    def test_stock_cannot_become_negative(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/products/inventory/adjustments/",
            {
                "variant_id": self.variant.id,
                "quantity_change": -4,
                "reason": "correction",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 409)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)

class InventoryLifecycleTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser(
            username="lifecycle-admin",
            email="lifecycle@example.com",
            password="test-password-123",
        )
        category = Category.objects.create(name="Lifecycle", slug="lifecycle")
        product = Product.objects.create(
            sku="LIFE-001",
            name="Lifecycle Product",
            slug="lifecycle-product",
            category=category,
            description="Inventory lifecycle test",
            price="250.00",
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            name="Standard",
            sku="LIFE-001-STD",
            stock_quantity=5,
            low_stock_threshold=2,
        )
        self.client.force_authenticate(user=self.admin)

    def test_restock_and_damaged_adjustments_preserve_audit_chain(self):
        restock = self.client.post(
            "/api/products/inventory/adjustments/",
            {"variant_id": self.variant.id, "quantity_change": 7, "reason": "restock", "note": "Supplier delivery"},
            format="json",
        )
        self.assertEqual(restock.status_code, 201)
        self.assertEqual(restock.data["adjustment"]["quantity_before"], 5)
        self.assertEqual(restock.data["adjustment"]["quantity_after"], 12)

        damaged = self.client.post(
            "/api/products/inventory/adjustments/",
            {"variant_id": self.variant.id, "quantity_change": -2, "reason": "damaged", "note": "Two damaged units"},
            format="json",
        )
        self.assertEqual(damaged.status_code, 201)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)
        self.assertEqual(damaged.data["adjustment"]["quantity_before"], 12)
        self.assertEqual(damaged.data["adjustment"]["quantity_after"], 10)

    def test_zero_change_is_rejected(self):
        response = self.client.post(
            "/api/products/inventory/adjustments/",
            {"variant_id": self.variant.id, "quantity_change": 0, "reason": "correction"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_unknown_variant_is_404(self):
        response = self.client.post(
            "/api/products/inventory/adjustments/",
            {"variant_id": 999999, "quantity_change": 1, "reason": "restock"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_variant_form_locks_existing_stock_but_allows_new_stock(self):
        from .admin import ProductVariantAdminForm

        existing_form = ProductVariantAdminForm(instance=self.variant)
        self.assertTrue(existing_form.fields["stock_quantity"].disabled)

        new_form = ProductVariantAdminForm()
        self.assertFalse(new_form.fields["stock_quantity"].disabled)
