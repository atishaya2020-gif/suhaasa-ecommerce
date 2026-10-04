from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


User = get_user_model()


class OrderAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_order_creation_requires_login(self):
        response = self.client.post(
            "/api/orders/create/",
            {
                "name": "Guest Customer",
                "email": "guest@example.com",
                "phone": "9999999999",
                "address": "Test address",
                "city": "Chandigarh",
                "state": "Punjab",
                "pincode": "160001",
                "shipping_method": "standard",
            },
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_order_history_requires_login(self):
        response = self.client.get("/api/orders/")
        self.assertIn(response.status_code, (401, 403))
