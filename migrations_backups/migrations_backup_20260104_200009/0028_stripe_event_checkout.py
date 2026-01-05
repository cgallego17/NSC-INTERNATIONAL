from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0023_restore_event_fields"),
        ("accounts", "0027_userwallet_wallettransaction"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeEventCheckout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_session_id", models.CharField(max_length=255, unique=True)),
                ("currency", models.CharField(default="usd", max_length=10)),
                ("payment_mode", models.CharField(choices=[("plan", "Plan"), ("now", "Pay now")], default="plan", max_length=10)),
                ("discount_percent", models.PositiveSmallIntegerField(default=0)),
                ("player_ids", models.JSONField(blank=True, default=list)),
                ("hotel_cart_snapshot", models.JSONField(blank=True, default=dict)),
                ("breakdown", models.JSONField(blank=True, default=dict)),
                ("amount_total", models.DecimalField(decimal_places=2, default="0.00", max_digits=10)),
                ("status", models.CharField(choices=[("created", "Created"), ("paid", "Paid"), ("cancelled", "Cancelled"), ("expired", "Expired")], default="created", max_length=20)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stripe_checkouts", to="events.event")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stripe_event_checkouts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]


