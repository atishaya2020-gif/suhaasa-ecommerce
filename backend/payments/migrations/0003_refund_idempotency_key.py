import uuid
from django.db import migrations, models


def set_idempotency_keys(apps, schema_editor):
    Refund = apps.get_model("payments", "Refund")
    for refund in Refund.objects.filter(idempotency_key=""):
        refund.idempotency_key = str(uuid.uuid4())
        refund.save(update_fields=["idempotency_key"])


class Migration(migrations.Migration):
    dependencies = [("payments", "0002_refund")]

    operations = [
        migrations.AddField(
            model_name="refund",
            name="idempotency_key",
            field=models.CharField(default="", max_length=64),
        ),
        migrations.RunPython(set_idempotency_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="refund",
            name="idempotency_key",
            field=models.CharField(default=uuid.uuid4, max_length=64, unique=True),
        ),
    ]
