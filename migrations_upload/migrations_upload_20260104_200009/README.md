# Migraciones para Subir al Servidor

Fecha: 2026-01-04 20:00:09
Total de migraciones: 38

## Instrucciones para Aplicar en el Servidor

1. Detén el servidor Django:
   sudo systemctl stop gunicorn
   # O
   sudo supervisorctl stop nsc

2. Haz backup de las migraciones actuales:
   cd /var/www/NSC-INTERNATIONAL
   cp -r apps/accounts/migrations apps/accounts/migrations.backup_$(date +%Y%m%d_%H%M%S)

3. Sube este directorio al servidor:
   scp -r migrations_upload_20260104_200009 root@servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/
   
   O usando rsync:
   rsync -avz migrations_upload_20260104_200009/ root@servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/

4. Verifica que los archivos estén en el lugar correcto:
   ls -la /var/www/NSC-INTERNATIONAL/apps/accounts/migrations/ | grep -E "003[678]"

5. Aplica las migraciones:
   cd /var/www/NSC-INTERNATIONAL
   python manage.py migrate accounts

6. Reinicia el servidor:
   sudo systemctl start gunicorn
   # O
   sudo supervisorctl start nsc

## Migraciones Incluidas

- 0001_initial.py
- 0002_userprofile_address_line_2_and_more.py
- 0003_alter_team_city_alter_team_country_alter_team_state.py
- 0004_alter_userprofile_user_type_playerparent.py
- 0005_dashboardcontent.py
- 0006_player_batting_glove_size_player_batting_helmet_size_and_more.py
- 0007_player_age_verification_approved_date_and_more.py
- 0008_player_graduation_year_and_more.py
- 0009_player_position_2_player_position_3.py
- 0010_player_is_pitcher_alter_player_position_and_more.py
- 0011_alter_player_is_pitcher.py
- 0012_alter_player_position_alter_player_position_2_and_more.py
- 0013_player_shorts_size_select.py
- 0014_player_sports_shirt_size_and_more.py
- 0015_player_photo.py
- 0016_remove_player_graduation_year_and_more.py
- 0017_homebanner.py
- 0018_sitesettings.py
- 0019_sitesettings_showcase_description_and_more.py
- 0020_sponsor.py
- 0021_sitesettings_dashboard_welcome_banner.py
- 0022_dashboardbanner.py
- 0023_dashboardcontent_user_type.py
- 0024_add_multilanguage_fields.py
- 0025_sitesettings_contact_address_and_more.py
- 0026_userprofile_preferred_language.py
- 0027_userwallet_wallettransaction.py
- 0028_stripe_event_checkout.py
- 0029_stripe_event_checkout_subscription_fields.py
- 0030_alter_stripeeventcheckout_amount_total.py
- 0031_marqueemessage.py
- 0032_player_is_pitcher_player_secondary_position_and_more.py
- 0033_alter_player_batting_glove_size_and_more.py
- 0034_userprofile_last_name2.py
- 0035_homebanner_mobile_image_alter_homebanner_image.py
- 0036_add_slug_to_player.py
- 0037_alter_sitesettings_dashboard_welcome_banner.py
- 0038_merge_slug_and_banner.py
