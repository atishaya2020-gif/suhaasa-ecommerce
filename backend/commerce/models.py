import uuid

from django.conf import settings
from django.db import models

from products.models import Product, ProductVariant


class GuestSession(models.Model):
    """Anonymous shopper state keyed by a random bearer token stored in the browser."""

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="commerce_session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Guest session {self.token}"


class CartItem(models.Model):
    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="cart_items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "variant"], name="unique_guest_cart_variant"),
        ]
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.session.token} — {self.variant} × {self.quantity}"


class WishlistItem(models.Model):
    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "product"], name="unique_guest_wishlist_product"),
        ]
        ordering = ["-created_at", "id"]

    def __str__(self):
        return f"{self.session.token} — {self.product.name}"
