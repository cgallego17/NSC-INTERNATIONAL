#!/usr/bin/env python
"""
Script para actualizar SiteSettings a valores en inglés
Ejecutar: python update_site_settings.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import SiteSettings

def update_site_settings():
    """Actualiza los valores de SiteSettings a inglés"""
    try:
        settings = SiteSettings.objects.first()
        if settings:
            print(f"Actualizando SiteSettings (ID: {settings.id})...")
            
            # Actualizar schedule_title
            if settings.schedule_title == "CALENDARIO DE EVENTOS 2026":
                settings.schedule_title = "2026 EVENT CALENDAR"
                print("  - schedule_title actualizado")
            
            # Actualizar schedule_subtitle
            if settings.schedule_subtitle == "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026":
                settings.schedule_subtitle = "REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026"
                print("  - schedule_subtitle actualizado")
            
            settings.save()
            print("✓ SiteSettings actualizado correctamente")
        else:
            print("No hay SiteSettings en la base de datos. Se crearán con valores en inglés por defecto.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_site_settings()

