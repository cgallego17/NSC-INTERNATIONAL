#!/usr/bin/env python
"""Script para forzar la recarga de traducciones"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _

# Limpiar caché de traducciones
if hasattr(translation, "_translations"):
    translation._translations = {}

# Activar español
translation.activate("es")
print(f"Idioma activo: {translation.get_language()}")
print(f"LOCALE_PATHS: {settings.LOCALE_PATHS}")

# Forzar recarga
translation._check_for_language("es")

# Probar traducciones
print(f'Pending: {_("Pending")}')
print(f'Total Players: {_("Total Players")}')
print(f'Different Teams: {_("Different Teams")}')
print(f'Divisions: {_("Divisions")}')
print(f'Verified: {_("Verified")}')
print(f'No team assigned: {_("No team assigned")}')


