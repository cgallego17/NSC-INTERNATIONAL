#!/usr/bin/env python
"""Script para probar la URL del perfil en vivo"""
import os
import sys
import django

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.test import Client
from apps.accounts.models import Player
from django.urls import resolve, reverse

print("=" * 60)
print("PRUEBA EN VIVO DE URL DEL PERFIL")
print("=" * 60)

client = Client()
player = Player.objects.filter(is_active=True).first()

if not player:
    print("ERROR: No se encontraron jugadores activos")
    exit(1)

print(f"\nJugador de prueba:")
print(f"  Nombre: {player.user.get_full_name()}")
print(f"  Slug: {player.slug}")
print(f"  PK: {player.pk}")

# Probar URL con slug
print(f"\n1. Prueba de acceso con slug:")
url_slug = f"/players/{player.slug}/"
print(f"  URL: {url_slug}")

try:
    response = client.get(url_slug)
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"  [OK] URL funciona correctamente")
        if hasattr(response, 'template_name'):
            print(f"  Template: {response.template_name}")
    elif response.status_code == 404:
        print(f"  [ERROR] 404 - No se encontró el jugador")
        print(f"  Contenido: {response.content[:200]}")
    else:
        print(f"  [ERROR] Status inesperado: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] Excepción: {e}")
    import traceback
    traceback.print_exc()

# Probar URL con pk
print(f"\n2. Prueba de acceso con pk:")
url_pk = f"/players/{player.pk}/"
print(f"  URL: {url_pk}")

try:
    response = client.get(url_pk)
    print(f"  Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"  [OK] URL funciona correctamente")
    elif response.status_code == 404:
        print(f"  [ERROR] 404 - No se encontró el jugador")
    else:
        print(f"  [ERROR] Status inesperado: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] Excepción: {e}")
    import traceback
    traceback.print_exc()

# Verificar resolución de URLs
print(f"\n3. Verificar resolución de URLs:")
try:
    match_slug = resolve(url_slug)
    print(f"  URL con slug resuelve a: {match_slug.view_name}")
    print(f"  Parámetros: {match_slug.kwargs}")
except Exception as e:
    print(f"  [ERROR] No se pudo resolver URL con slug: {e}")

try:
    match_pk = resolve(url_pk)
    print(f"  URL con pk resuelve a: {match_pk.view_name}")
    print(f"  Parámetros: {match_pk.kwargs}")
except Exception as e:
    print(f"  [ERROR] No se pudo resolver URL con pk: {e}")

print("\n" + "=" * 60)

