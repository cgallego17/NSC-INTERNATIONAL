from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0028_stripe_event_checkout"),
    ]

    operations = [
        migrations.AddField(
            model_name="stripeeventcheckout",
            name="stripe_subscription_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="stripeeventcheckout",
            name="stripe_subscription_schedule_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="stripeeventcheckout",
            name="plan_months",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="stripeeventcheckout",
            name="plan_monthly_amount",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10),
        ),
    ]



