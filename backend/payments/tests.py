from django.test import TestCase
from rest_framework.test import APIClient


class PaymentAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_payment_creation_requires_login(self):
        response = self.client.post("/api/payments/create/", {"order_number": "SH-TEST"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_payment_verification_requires_login(self):
        response = self.client.post("/api/payments/verify/", {"order_number": "SH-TEST"}, format="json")
        self.assertIn(response.status_code, (401, 403))
