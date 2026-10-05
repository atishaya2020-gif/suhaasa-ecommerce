from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_order_address_line2"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="stock_reserved",
            field=models.BooleanField(default=False),
        ),
    ]
