from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, ProductVariant

from .models import Notification


class NotificationAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="owner", password="test-password", is_staff=True, is_superuser=True)
        self.client.login(username="owner", password="test-password")
        category = Category.objects.create(name="Kurtas", slug="kurtas")
        product = Product.objects.create(
            category=category,
            name="Test Kurta",
            slug="test-kurta",
            sku="TEST-KRT",
            description="Test",
            price="1000.00",
        )
        self.variant = ProductVariant.objects.create(product=product, name="M", sku="TEST-KRT-M", stock_quantity=2, low_stock_threshold=5)

    def test_notification_list_syncs_low_stock(self):
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["unread_count"], 1)
        self.assertEqual(payload["notifications"][0]["kind"], "low_stock")

    def test_mark_read(self):
        notification = Notification.objects.create(
            recipient=self.user,
            kind="system",
            title="Test",
            message="Test notification",
            dedupe_key="test",
        )
        response = self.client.post(reverse("notifications:mark_read", args=[notification.pk]))
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_mark_all_read(self):
        for i in range(2):
            Notification.objects.create(
                recipient=self.user,
                kind="system",
                title=f"Test {i}",
                message="Test notification",
                dedupe_key=f"test-{i}",
            )
        response = self.client.post(reverse("notifications:mark_all_read"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)
