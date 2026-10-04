from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=30, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile — {self.user.email}"


class Address(models.Model):
    LABEL_CHOICES = [
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, default="home")
    full_name = models.CharField(max_length=180)
    phone = models.CharField(max_length=30)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    pincode = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]

    def save(self, *args, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            if self.is_default:
                Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
            elif not Address.objects.filter(user=self.user).exclude(pk=self.pk).exists():
                self.is_default = True
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_label_display()} — {self.city} ({self.user.email})"
