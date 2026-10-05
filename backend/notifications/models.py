from django.conf import settings
from django.db import models


class Notification(models.Model):
    KIND_CHOICES = [
        ("order", "Order"),
        ("payment", "Payment"),
        ("low_stock", "Low stock"),
        ("out_of_stock", "Out of stock"),
        ("system", "System"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="suhaasa_notifications",
    )
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, default="system")
    title = models.CharField(max_length=180)
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True)
    dedupe_key = models.CharField(max_length=220)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "dedupe_key"],
                name="unique_notification_recipient_key",
            ),
        ]
        indexes = [
            models.Index(fields=["recipient", "is_read", "created_at"], name="notif_rec_read_created_idx"),
            models.Index(fields=["recipient", "created_at"], name="notif_recipient_created_idx"),
        ]

    def __str__(self):
        return f"{self.title} — {self.recipient}"
