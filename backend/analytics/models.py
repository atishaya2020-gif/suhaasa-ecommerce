from django.db import models


class PageView(models.Model):
    visitor_id = models.CharField(max_length=64, db_index=True)
    session_id = models.CharField(max_length=64, db_index=True)
    path = models.CharField(max_length=500)
    referrer = models.URLField(max_length=1000, blank=True)
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=180, blank=True)
    device_type = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at", "path"], name="analytics_p_created_3a6c9f_idx"),
            models.Index(fields=["created_at", "session_id"], name="analytics_p_created_5a1e1a_idx"),
            models.Index(fields=["created_at", "visitor_id"], name="analytics_p_created_0f7b3d_idx"),
        ]

    def __str__(self):
        return f"{self.path} — {self.created_at:%Y-%m-%d %H:%M}"
