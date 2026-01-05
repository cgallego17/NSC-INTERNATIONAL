# Generated manually to merge conflicting migrations
# This migration merges 0036_add_slug_to_player with either:
# - 0037_alter_sitesettings_dashboard_welcome_banner (local)
# - 0038_alter_sitesettings_dashboard_welcome_banner (server)
#
# On the server, this migration should depend on:
# - ('accounts', '0036_add_slug_to_player')
# - ('accounts', '0038_alter_sitesettings_dashboard_welcome_banner')
#
# Locally, this migration depends on:
# - ('accounts', '0036_add_slug_to_player')
# - ('accounts', '0037_alter_sitesettings_dashboard_welcome_banner')

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0036_add_slug_to_player"),
        ("accounts", "0037_alter_sitesettings_dashboard_welcome_banner"),
    ]

    # Note: On the server, if 0038_alter_sitesettings_dashboard_welcome_banner exists instead of 0037,
    # you may need to manually update this migration's dependencies to:
    # dependencies = [
    #     ('accounts', '0036_add_slug_to_player'),
    #     ('accounts', '0038_alter_sitesettings_dashboard_welcome_banner'),
    # ]

    operations = []
