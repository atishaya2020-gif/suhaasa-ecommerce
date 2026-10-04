from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AccountExperienceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="customer@example.com", email="customer@example.com", password="StrongPass123!")
        self.other = User.objects.create_user(username="other@example.com", email="other@example.com", password="StrongPass123!")

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertIn(response.status_code, (401, 403))

    def test_customer_can_update_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch("/api/auth/me/", {"first_name": "Asha", "phone": "9876543210"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Asha")
        self.assertEqual(self.user.customer_profile.phone, "9876543210")

    def test_customer_can_manage_own_addresses(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/auth/addresses/", {
            "label": "home", "full_name": "Asha Jain", "phone": "9876543210",
            "address_line1": "12 Main Road", "address_line2": "Sector 1",
            "city": "Chandigarh", "state": "Punjab", "pincode": "160001", "is_default": True,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        address_id = response.data["id"]
        response = self.client.get("/api/auth/addresses/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f"/api/auth/addresses/{address_id}/", {"city": "Delhi"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/auth/addresses/{address_id}/").status_code, 404)
