# Generated manually to merge conflicting migrations
# This migration merges 0036_add_slug_to_player with 0037_alter_sitesettings_dashboard_welcome_banner
#
# IMPORTANT: On the server, you must DELETE the old duplicate migrations:
# - 0036_alter_sitesettings_dashboard_welcome_banner.py (old, duplicate)
# - 0038_alter_sitesettings_dashboard_welcome_banner.py (old, duplicate)
#
# Keep only:
# - 0036_add_slug_to_player.py (new, correct)
# - 0037_alter_sitesettings_dashboard_welcome_banner.py (new, correct)
# - 0038_merge_slug_and_banner.py (this file)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0036_add_slug_to_player"),
        ("accounts", "0037_alter_sitesettings_dashboard_welcome_banner"),
    ]


    operations = []
