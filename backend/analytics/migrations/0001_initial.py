from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PageView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("visitor_id", models.CharField(db_index=True, max_length=64)),
                ("session_id", models.CharField(db_index=True, max_length=64)),
                ("path", models.CharField(max_length=500)),
                ("referrer", models.URLField(blank=True, max_length=1000)),
                ("utm_source", models.CharField(blank=True, max_length=120)),
                ("utm_medium", models.CharField(blank=True, max_length=120)),
                ("utm_campaign", models.CharField(blank=True, max_length=180)),
                ("device_type", models.CharField(blank=True, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["created_at", "path"], name="analytics_p_created_3a6c9f_idx"),
                    models.Index(fields=["created_at", "session_id"], name="analytics_p_created_5a1e1a_idx"),
                    models.Index(fields=["created_at", "visitor_id"], name="analytics_p_created_0f7b3d_idx"),
                ],
            },
        ),
    ]
