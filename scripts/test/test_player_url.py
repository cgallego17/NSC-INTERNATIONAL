#!/usr/bin/env python
"""Script para probar las URLs de los jugadores"""
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

# Obtener un jugador activo
player = Player.objects.filter(is_active=True).first()

if player:
    print(f"Jugador: {player.user.get_full_name()}")
    print(f"Slug: {player.slug}")
    print(f"PK: {player.pk}")
    print(f"Activo: {player.is_active}")

    if player.slug:
        try:
            url = reverse("public_player_profile", kwargs={"slug": player.slug})
            print(f"URL generada: {url}")
            print(f"URL completa: http://localhost:8000{url}")
        except Exception as e:
            print(f"Error al generar URL: {e}")
    else:
        print("ERROR: El jugador no tiene slug")
else:
    print("No se encontraron jugadores activos")

# Verificar todos los jugadores activos
print("\n" + "="*60)
print("Verificando todos los jugadores activos:")
players = Player.objects.filter(is_active=True)
print(f"Total jugadores activos: {players.count()}")

players_sin_slug = players.filter(slug__isnull=True) | players.filter(slug='')
print(f"Jugadores activos sin slug: {players_sin_slug.count()}")

if players_sin_slug.exists():
    print("\nJugadores sin slug:")
    for p in players_sin_slug[:5]:
        print(f"  - {p.user.get_full_name()} (PK: {p.pk})")

