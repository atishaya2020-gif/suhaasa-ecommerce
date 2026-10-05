from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="low_stock_threshold",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.CreateModel(
            name="InventoryAdjustment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity_before", models.PositiveIntegerField()),
                ("quantity_change", models.IntegerField()),
                ("quantity_after", models.PositiveIntegerField()),
                ("reason", models.CharField(choices=[("restock", "Restock"), ("correction", "Manual correction"), ("damaged", "Damaged"), ("returned", "Returned"), ("order_adjustment", "Order adjustment"), ("other", "Other")], max_length=30)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("adjusted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="inventory_adjustments", to=settings.AUTH_USER_MODEL)),
                ("variant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory_adjustments", to="products.productvariant")),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "indexes": [
                    models.Index(fields=["variant", "-created_at"], name="products_inve_variant__e8a8f8_idx"),
                    models.Index(fields=["reason", "-created_at"], name="products_inve_reason_2c1a8d_idx"),
                ],
            },
        ),
    ]
