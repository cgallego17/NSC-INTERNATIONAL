from django.core.management.base import BaseCommand

from apps.locations.models import Rule


class Command(BaseCommand):
    help = "Populate the database with sample rules"

    def handle(self, *args, **options):
        rules_data = [
            {
                "name": "Standard Competition Rules",
                "description": "Standard rules for regular competitions and events",
                "rule_type": "standard",
                "is_active": True,
            },
            {
                "name": "Championship Rules",
                "description": "Special rules for championship events with higher stakes",
                "rule_type": "championship",
                "is_active": True,
            },
            {
                "name": "Modified Rules",
                "description": "Modified rules for special events or different formats",
                "rule_type": "modified",
                "is_active": True,
            },
            {
                "name": "Exhibition Rules",
                "description": "Rules for exhibition events and demonstrations",
                "rule_type": "exhibition",
                "is_active": True,
            },
            {
                "name": "Custom Rules Set A",
                "description": "Custom rules set for specific event requirements",
                "rule_type": "custom",
                "is_active": True,
            },
            {
                "name": "Custom Rules Set B",
                "description": "Alternative custom rules set for different event types",
                "rule_type": "custom",
                "is_active": True,
            },
            {
                "name": "Legacy Rules",
                "description": "Older rules that are no longer actively used",
                "rule_type": "standard",
                "is_active": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for rule_data in rules_data:
            rule, created = Rule.objects.get_or_create(name=rule_data["name"], defaults=rule_data)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created rule: {rule.name}"))
            else:
                # Update existing rule
                for key, value in rule_data.items():
                    setattr(rule, key, value)
                rule.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated rule: {rule.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nRules population completed!\n"
                f"Created: {created_count}\n"
                f"Updated: {updated_count}\n"
                f"Total rules: {Rule.objects.count()}"
            )
        )
