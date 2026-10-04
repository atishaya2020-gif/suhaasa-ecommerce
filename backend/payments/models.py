from django.db import models
from orders.models import Order

class Payment(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("authorized", "Authorized"),
        ("captured", "Captured"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    gateway = models.CharField(max_length=30, default="razorpay")
    gateway_order_id = models.CharField(max_length=100, unique=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="created")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} — {self.gateway_payment_id or self.gateway_order_id}"
