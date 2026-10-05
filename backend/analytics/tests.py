import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PageView


class AnalyticsTests(TestCase):
    def test_pageview_tracking(self):
        response = self.client.post(
            "/api/analytics/track/",
            data=json.dumps({
                "visitor_id": "visitor-1",
                "session_id": "session-1",
                "path": "/",
                "device_type": "desktop",
                "utm_source": "linkedin",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PageView.objects.count(), 1)
        self.assertEqual(PageView.objects.get().utm_source, "linkedin")

    def test_dashboard_requires_staff(self):
        response = self.client.get("/api/analytics/dashboard/")
        self.assertEqual(response.status_code, 302)

    def test_dashboard_for_staff(self):
        user = get_user_model().objects.create_user(username="analytics-admin", password="test-password", is_staff=True, is_superuser=True)
        self.client.force_login(user)
        PageView.objects.create(visitor_id="v1", session_id="s1", path="/", device_type="mobile")
        response = self.client.get("/api/analytics/dashboard/?period=7")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["traffic"]["visitors"], 1)
        self.assertEqual(payload["traffic"]["pageviews"], 1)
        self.assertEqual(payload["period_days"], 7)
