from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Refund",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("currency", models.CharField(default="INR", max_length=3)),
                ("reason", models.CharField(
                    choices=[("cancellation", "Order cancellation"), ("return", "Customer return"), ("other", "Other")],
                    default="cancellation", max_length=30,
                )),
                ("note", models.CharField(blank=True, max_length=500)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"), ("processing", "Processing"),
                        ("processed", "Processed"), ("failed", "Failed"), ("cancelled", "Cancelled"),
                    ],
                    default="pending", max_length=30,
                )),
                ("gateway_refund_id", models.CharField(blank=True, db_index=True, max_length=100)),
                ("raw_response", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("processed_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="processed_refunds", to=settings.AUTH_USER_MODEL,
                )),
                ("requested_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="refund_requests", to=settings.AUTH_USER_MODEL,
                )),
                ("order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="refunds", to="orders.order",
                )),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="refund",
            constraint=models.UniqueConstraint(
                condition=~models.Q(gateway_refund_id=""),
                fields=("gateway_refund_id",),
                name="unique_nonempty_gateway_refund_id",
            ),
        ),
    ]
