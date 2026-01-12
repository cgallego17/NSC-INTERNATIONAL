#!/usr/bin/env python
"""Script completo para probar las URLs de los jugadores"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from apps.accounts.models import Player
from django.urls import reverse

print("=" * 60)
print("PRUEBA DE URLs DEL PERFIL DE JUGADOR")
print("=" * 60)

# Obtener un jugador activo
player = Player.objects.filter(is_active=True).first()

if not player:
    print("ERROR: No se encontraron jugadores activos")
    exit(1)

print(f"\n1. Información del jugador:")
print(f"   Nombre: {player.user.get_full_name()}")
print(f"   Slug: {player.slug}")
print(f"   PK: {player.pk}")
print(f"   Activo: {player.is_active}")

# Probar URL con slug
print(f"\n2. Prueba de URL con slug:")
if player.slug:
    try:
        url_slug = reverse("public_player_profile", kwargs={"slug": player.slug})
        print(f"   [OK] URL generada: {url_slug}")
        print(f"   [OK] URL completa: http://localhost:8000{url_slug}")
    except Exception as e:
        print(f"   [ERROR] Error al generar URL: {e}")
else:
    print(f"   [WARNING] El jugador no tiene slug")

# Probar URL con pk
print(f"\n3. Prueba de URL con pk:")
try:
    url_pk = reverse("public_player_profile_pk", kwargs={"pk": player.pk})
    print(f"   [OK] URL generada: {url_pk}")
    print(f"   [OK] URL completa: http://localhost:8000{url_pk}")
except Exception as e:
    print(f"   [ERROR] Error al generar URL: {e}")

# Verificar todos los jugadores
print(f"\n4. Verificación de todos los jugadores activos:")
players = Player.objects.filter(is_active=True)
print(f"   Total jugadores activos: {players.count()}")

players_sin_slug = players.filter(slug__isnull=True) | players.filter(slug='')
print(f"   Jugadores sin slug: {players_sin_slug.count()}")

if players_sin_slug.exists():
    print(f"\n   [WARNING] Jugadores sin slug encontrados:")
    for p in players_sin_slug[:5]:
        print(f"     - {p.user.get_full_name()} (PK: {p.pk})")
        # Generar slug automáticamente
        p.save()
        print(f"       -> Slug generado: {p.slug}")

# Probar generación de URLs para varios jugadores
print(f"\n5. Prueba de URLs para múltiples jugadores:")
test_players = players[:5]
for p in test_players:
    if p.slug:
        try:
            url = reverse("public_player_profile", kwargs={"slug": p.slug})
            print(f"   [OK] {p.user.get_full_name()}: {url}")
        except Exception as e:
            print(f"   [ERROR] {p.user.get_full_name()}: {e}")
    else:
        print(f"   [WARNING] {p.user.get_full_name()}: Sin slug")

print("\n" + "=" * 60)
print("[OK] Pruebas completadas")
print("=" * 60)

