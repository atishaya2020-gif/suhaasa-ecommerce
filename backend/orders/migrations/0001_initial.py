from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("commerce", "0002_guestsession_user"),
        ("products", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(db_index=True, editable=False, max_length=24, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("full_name", models.CharField(max_length=180)),
                ("phone", models.CharField(max_length=30)),
                ("address_line1", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=120)),
                ("state", models.CharField(max_length=120)),
                ("pincode", models.CharField(max_length=20)),
                ("shipping_method", models.CharField(choices=[("standard", "Standard"), ("express", "Express")], max_length=30)),
                ("shipping_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("placed", "Placed"), ("processing", "Processing"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="placed", max_length=30)),
                ("payment_status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("refunded", "Refunded")], default="pending", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="commerce.guestsession")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=180)),
                ("product_sku", models.CharField(max_length=70)),
                ("variant_name", models.CharField(max_length=80)),
                ("image_url", models.TextField(blank=True)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.PositiveIntegerField()),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="order_items", to="products.product")),
                ("variant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="order_items", to="products.productvariant")),
            ],
        ),
    ]
