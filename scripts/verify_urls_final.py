#!/usr/bin/env python
"""Verificación final de URLs"""
import os
import sys
import django

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
django.setup()

from django.urls import resolve, reverse
from apps.accounts.models import Player

print("=" * 60)
print("VERIFICACIÓN FINAL DE URLs")
print("=" * 60)

player = Player.objects.filter(is_active=True).first()

if not player:
    print("ERROR: No se encontraron jugadores")
    exit(1)

print(f"\nJugador: {player.user.get_full_name()}")
print(f"Slug: {player.slug}")
print(f"PK: {player.pk}")

# Verificar resolución de URLs
print(f"\n1. Verificar resolución de URLs:")

# URL con slug
url_slug = f"/players/{player.slug}/"
try:
    match = resolve(url_slug)
    print(f"  [OK] {url_slug}")
    print(f"      -> Vista: {match.view_name}")
    print(f"      -> Params: {match.kwargs}")
except Exception as e:
    print(f"  [ERROR] {url_slug}: {e}")

# URL con pk
url_pk = f"/players/{player.pk}/"
try:
    match = resolve(url_pk)
    print(f"  [OK] {url_pk}")
    print(f"      -> Vista: {match.view_name}")
    print(f"      -> Params: {match.kwargs}")
except Exception as e:
    print(f"  [ERROR] {url_pk}: {e}")

# Verificar generación de URLs
print(f"\n2. Verificar generación de URLs:")

try:
    url_gen_slug = reverse("public_player_profile", kwargs={"slug": player.slug})
    print(f"  [OK] reverse('public_player_profile', slug='{player.slug}')")
    print(f"      -> {url_gen_slug}")
except Exception as e:
    print(f"  [ERROR] {e}")

try:
    url_gen_pk = reverse("public_player_profile_pk", kwargs={"pk": player.pk})
    print(f"  [OK] reverse('public_player_profile_pk', pk={player.pk})")
    print(f"      -> {url_gen_pk}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Verificar que las URLs generadas coincidan con las resueltas
print(f"\n3. Verificar coherencia:")
if url_gen_slug == url_slug:
    print(f"  [OK] URL con slug coincide")
else:
    print(f"  [WARNING] URL con slug no coincide: {url_gen_slug} vs {url_slug}")

if url_gen_pk == url_pk:
    print(f"  [OK] URL con pk coincide")
else:
    print(f"  [WARNING] URL con pk no coincide: {url_gen_pk} vs {url_pk}")

print("\n" + "=" * 60)
print("[OK] Verificación completada")
print("=" * 60)

