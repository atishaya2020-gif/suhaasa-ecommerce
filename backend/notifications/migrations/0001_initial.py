from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("order", "Order"), ("payment", "Payment"), ("low_stock", "Low stock"), ("out_of_stock", "Out of stock"), ("system", "System")], default="system", max_length=30)),
                ("title", models.CharField(max_length=180)),
                ("message", models.CharField(max_length=500)),
                ("link", models.CharField(blank=True, max_length=500)),
                ("dedupe_key", models.CharField(max_length=220)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="suhaasa_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["recipient", "is_read", "created_at"], name="notif_rec_read_created_idx"),
                    models.Index(fields=["recipient", "created_at"], name="notif_recipient_created_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("recipient", "dedupe_key"), name="unique_notification_recipient_key"),
                ],
            },
        ),
    ]
