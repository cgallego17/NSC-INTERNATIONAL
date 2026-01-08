"""
Management command para crear una orden completa siguiendo el flujo real de creación.
Simula todo el proceso desde la selección de jugadores y habitaciones hasta el pago exitoso.
"""
import json
import sys
import types
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import (
    Order,
    Player,
    PlayerParent,
    StripeEventCheckout,
    UserProfile,
)
from apps.accounts.views_private import _create_order_from_stripe_checkout, _finalize_stripe_event_checkout
from apps.events.models import Event, EventAttendance, EventCategory
from apps.locations.models import Hotel, HotelReservation, HotelRoom

User = get_user_model()


class Command(BaseCommand):
    help = "Crea una orden completa siguiendo el flujo real de creación"

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            help="ID del evento existente a usar (opcional). Si no se proporciona, se crea uno nuevo.",
        )
        parser.add_argument(
            "--parent-email",
            type=str,
            default="test_parent@nsc.com",
            help="Email del usuario padre (default: test_parent@nsc.com)",
        )
        parser.add_argument(
            "--players-count",
            type=int,
            default=2,
            help="Número de jugadores a registrar (default: 2)",
        )
        parser.add_argument(
            "--rooms-count",
            type=int,
            default=2,
            help="Número de habitaciones a reservar (default: 2)",
        )

    def handle(self, *args, **options):
        event_id = options.get("event_id")
        parent_email = options.get("parent_email")
        players_count = options.get("players_count")
        rooms_count = options.get("rooms_count")

        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS("CREANDO ORDEN COMPLETA - FLUJO COMPLETO"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        # Paso 1: Crear o obtener usuario padre
        self.stdout.write(self.style.WARNING("\n[PASO 1] Creando/obteniendo usuario padre..."))
        parent_user, created = User.objects.get_or_create(
            email=parent_email,
            defaults={
                "username": parent_email.split("@")[0],
                "first_name": "Test",
                "last_name": "Parent",
            },
        )
        if created:
            parent_user.set_password("testpass123")
            parent_user.save()
            UserProfile.objects.create(
                user=parent_user,
                user_type="parent",
                phone="+1 555-123-4567",
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario padre creado: {parent_user.email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario padre existente: {parent_user.email}"))
            if not hasattr(parent_user, "profile"):
                UserProfile.objects.create(
                    user=parent_user,
                    user_type="parent",
                    phone="+1 555-123-4567",
                )

        # Paso 2: Crear jugadores (hijos)
        self.stdout.write(self.style.WARNING(f"\n[PASO 2] Creando {players_count} jugador(es)..."))
        players = []
        for i in range(1, players_count + 1):
            player_email = f"player{i}@test.com"
            player_user, created = User.objects.get_or_create(
                email=player_email,
                defaults={
                    "username": f"player{i}_user",
                    "first_name": f"Jugador",
                    "last_name": f"{i}",
                },
            )
            if created:
                player_user.set_password("testpass123")
                player_user.save()
                UserProfile.objects.create(
                    user=player_user,
                    user_type="player",
                    phone=f"+1 555-000-000{i}",
                    birth_date=date(2012, 1, 15),
                )
            player, created = Player.objects.get_or_create(
                user=player_user,
                defaults={
                    "division": "12U",
                    "position": "catcher" if i == 1 else "pitcher",
                    "jersey_number": 10 + i,
                    "is_active": True,
                },
            )
            PlayerParent.objects.get_or_create(parent=parent_user, player=player)
            players.append(player)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Jugador {i} creado: {player.user.get_full_name()}"))

        # Paso 3: Crear o obtener evento
        self.stdout.write(self.style.WARNING("\n[PASO 3] Creando/obteniendo evento..."))
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Evento existente: {event.name}"))
            except Event.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ Evento con ID {event_id} no encontrado"))
                return
        else:
            # Crear categoría si no existe
            category, _ = EventCategory.objects.get_or_create(
                name="Test Category",
            )

            # Crear evento
            event_start = timezone.now().date() + timedelta(days=30)
            event_end = event_start + timedelta(days=3)
            # Obtener organizador (staff o superuser o el mismo parent_user)
            organizer = User.objects.filter(is_staff=True).first() or User.objects.filter(is_superuser=True).first() or parent_user

            # Obtener event_type
            from apps.events.models import EventType
            event_type, _ = EventType.objects.get_or_create(
                name="Tournament",
                defaults={"description": "Tournament event type"}
            )

            event, created = Event.objects.get_or_create(
                title="Test Event - Order Creation",
                defaults={
                    "category": category,
                    "event_type": event_type,
                    "organizer": organizer,
                    "start_date": event_start,
                    "end_date": event_end,
                    "default_entry_fee": Decimal("50.00"),
                    "entry_deadline": event_start - timedelta(days=7),
                    "status": "published",
                },
            )
            # Si el evento existe pero no tiene hotel, asignarle el hotel después
            event_name = getattr(event, 'title', f'Evento #{event.id}')
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Evento creado: {event_name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Evento existente: {event_name}"))

        # Paso 4: Crear hotel y habitaciones si no existen
        self.stdout.write(self.style.WARNING("\n[PASO 4] Creando/obteniendo hotel y habitaciones..."))
        if not event.hotel:
            hotel, created = Hotel.objects.get_or_create(
                hotel_name="Test Hotel - Order Creation",
                defaults={
                    "address": "123 Test Street",
                    "city": None,
                    "state": None,
                    "country": None,
                },
            )
            event.hotel = hotel
            event.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Hotel creado: {hotel.hotel_name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Hotel existente: {hotel.hotel_name}"))
        else:
            hotel = event.hotel
            self.stdout.write(self.style.SUCCESS(f"  [OK] Hotel existente: {hotel.hotel_name}"))

        # Crear habitaciones
        rooms = []
        for i in range(1, rooms_count + 1):
            # Usar un nombre único para cada ejecución para evitar conflictos
            import time
            room_number = f"TEST-{int(time.time())}-{i}"
            room, created = HotelRoom.objects.get_or_create(
                hotel=hotel,
                room_number=room_number,
                defaults={
                    "room_type": "double",
                    "capacity": 4,
                    "price_per_night": Decimal(f"{100 + i * 10}.00"),
                    "price_includes_guests": 2,
                    "additional_guest_price": Decimal("25.00"),
                    "stock": 10,  # Stock alto para asegurar disponibilidad
                    "is_available": True,
                },
            )
            # Si la habitación ya existe, asegurar que tenga stock disponible
            if not created:
                if room.stock is None or room.stock < 5:
                    room.stock = 10
                    room.is_available = True
                    room.save()
            rooms.append(room)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] Habitacion {i} creada: {room.room_number} (${room.price_per_night}/noche)")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] Habitacion {i} existente: {room.room_number} (${room.price_per_night}/noche)")
                )

        # Paso 5: Simular selección de jugadores y habitaciones (crear snapshot)
        self.stdout.write(self.style.WARNING("\n[PASO 5] Creando snapshot del checkout (selección de jugadores y habitaciones)..."))

        # Fechas de check-in y check-out
        check_in_date = event.start_date - timedelta(days=1)
        check_out_date = event.end_date + timedelta(days=1)

        # Crear guest_assignments y all_guests simulando la selección del usuario
        all_guests = []
        guest_assignments = {}

        # Agregar jugadores a all_guests
        for player in players:
            all_guests.append({
                "displayName": player.user.get_full_name(),
                "first_name": player.user.first_name,
                "last_name": player.user.last_name,
                "type": "child",
                "birth_date": str(player.user.profile.birth_date) if hasattr(player.user, 'profile') and player.user.profile.birth_date else "",
                "email": player.user.email,
            })

        # Agregar huéspedes adicionales (adultos)
        additional_adult_guests = [
            {"displayName": "María García", "first_name": "María", "last_name": "García", "type": "adult", "birth_date": "1990-05-15", "email": "maria@example.com"},
            {"displayName": "Juan Pérez", "first_name": "Juan", "last_name": "Pérez", "type": "adult", "birth_date": "1988-03-20", "email": "juan@example.com"},
        ]

        for guest in additional_adult_guests:
            all_guests.append(guest)

        # Asignar huéspedes a habitaciones
        guest_index = 0
        for i, room in enumerate(rooms):
            room_id = str(room.id)
            assigned = []

            # Primera habitación: jugador 1 + huésped adulto adicional
            if i == 0:
                assigned = [0, len(players)]  # Jugador 1 (índice 0) + primer adulto adicional
            # Segunda habitación: jugador 2 + segundo huésped adulto adicional
            elif i == 1 and len(players) > 1:
                assigned = [1, len(players) + 1]  # Jugador 2 (índice 1) + segundo adulto adicional
            else:
                # Para habitaciones adicionales, asignar solo el primer jugador disponible
                if i < len(players):
                    assigned = [i]
                else:
                    assigned = [0]  # Fallback al primer jugador

            guest_assignments[room_id] = assigned

        # Crear hotel_cart_snapshot como lo hace el código real
        hotel_cart_snapshot = {}
        for i, room in enumerate(rooms):
            room_id = str(room.id)
            assigned_indices = guest_assignments.get(room_id, [])
            guests_count = len(assigned_indices)

            # Extraer información de huéspedes adicionales
            additional_guest_details = []
            additional_guest_names = []

            for idx, guest_index in enumerate(assigned_indices):
                if idx == 0:
                    continue  # Skip el principal

                if 0 <= guest_index < len(all_guests):
                    guest_obj = all_guests[guest_index]
                    additional_guest_details.append({
                        "name": guest_obj.get("displayName", ""),
                        "type": guest_obj.get("type", "adult"),
                        "birth_date": guest_obj.get("birth_date", ""),
                        "email": guest_obj.get("email", ""),
                    })
                    additional_guest_names.append(guest_obj.get("displayName", ""))

            hotel_cart_snapshot[f"vue-room-{room_id}"] = {
                "type": "room",
                "room_id": int(room_id),
                "room_order": i,  # Orden de selección
                "check_in": check_in_date.strftime("%Y-%m-%d"),
                "check_out": check_out_date.strftime("%Y-%m-%d"),
                "guests": max(1, guests_count),
                "services": [],
                "additional_guest_names": additional_guest_names,
                "additional_guest_details": additional_guest_details,
                "notes": "",
            }

        player_ids = [str(p.id) for p in players]
        entry_fee = event.default_entry_fee or Decimal("0.00")
        players_total = entry_fee * Decimal(str(len(players)))

        # Calcular total de hotel (simplificado)
        hotel_total = Decimal("0.00")
        for room in rooms:
            nights = (check_out_date - check_in_date).days
            base = room.price_per_night * Decimal(str(nights))
            hotel_total += base

        total = players_total + hotel_total

        self.stdout.write(self.style.SUCCESS(f"  [OK] Snapshot creado:"))
        self.stdout.write(self.style.SUCCESS(f"    - Jugadores: {len(players)}"))
        self.stdout.write(self.style.SUCCESS(f"    - Habitaciones: {len(rooms)}"))
        self.stdout.write(self.style.SUCCESS(f"    - Total jugadores: ${players_total}"))
        self.stdout.write(self.style.SUCCESS(f"    - Total hotel: ${hotel_total}"))
        self.stdout.write(self.style.SUCCESS(f"    - Total: ${total}"))

        # Paso 6: Crear StripeEventCheckout
        self.stdout.write(self.style.WARNING("\n[PASO 6] Creando StripeEventCheckout..."))

        # Mock Stripe para evitar llamadas reales
        fake_stripe = types.ModuleType("stripe")
        fake_stripe.api_key = None

        class _FakeStripeSession:
            def __init__(self, id):
                self.id = id
                self.url = f"https://stripe.test/checkout/{id}"

        class _CheckoutSession:
            @staticmethod
            def create(**kwargs):
                session_id = f"cs_test_{int(timezone.now().timestamp())}"
                return _FakeStripeSession(id=session_id)

        class _Checkout:
            Session = _CheckoutSession

        fake_stripe.checkout = _Checkout
        sys.modules["stripe"] = fake_stripe

        # Crear el checkout
        checkout = StripeEventCheckout.objects.create(
            user=parent_user,
            event=event,
            stripe_session_id=f"cs_test_{int(timezone.now().timestamp())}",
            payment_mode="now",
            player_ids=player_ids,
            hotel_cart_snapshot=hotel_cart_snapshot,
            breakdown={
                "players_total": str(players_total),
                "hotel_total": str(hotel_total),
                "subtotal": str(total),
                "tax_amount": "0.00",
            },
            amount_total=total,
            status="created",
        )

        self.stdout.write(self.style.SUCCESS(f"  [OK] StripeEventCheckout creado: {checkout.stripe_session_id}"))

        # Paso 7: Finalizar checkout (simular pago exitoso)
        self.stdout.write(self.style.WARNING("\n[PASO 7] Finalizando checkout (simulando pago exitoso)..."))

        try:
            # Verificar que el snapshot tenga datos antes de finalizar
            if not checkout.hotel_cart_snapshot:
                self.stdout.write(self.style.ERROR("  [ERROR] El hotel_cart_snapshot está vacío"))
                return

            self.stdout.write(self.style.SUCCESS(f"  - Snapshot tiene {len(checkout.hotel_cart_snapshot)} habitaciones"))

            _finalize_stripe_event_checkout(checkout)
            self.stdout.write(self.style.SUCCESS("  [OK] Checkout finalizado correctamente"))

            # Verificar que se crearon las reservas
            from apps.locations.models import HotelReservation
            reservations_created = HotelReservation.objects.filter(
                user=checkout.user,
                notes__icontains=checkout.stripe_session_id
            ).count()
            self.stdout.write(self.style.SUCCESS(f"  - Reservas creadas: {reservations_created}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [ERROR] Error al finalizar checkout: {e}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            return

        # Paso 8: Verificar resultados
        self.stdout.write(self.style.WARNING("\n[PASO 8] Verificando resultados..."))

        checkout.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f"  [OK] Checkout status: {checkout.status}"))

        # Verificar Order
        order = Order.objects.filter(stripe_checkout=checkout).first()
        if order:
            self.stdout.write(self.style.SUCCESS(f"\n  [OK] ORDEN CREADA:"))
            self.stdout.write(self.style.SUCCESS(f"    - Order Number: {order.order_number}"))
            self.stdout.write(self.style.SUCCESS(f"    - Status: {order.status}"))
            self.stdout.write(self.style.SUCCESS(f"    - Total: ${order.total_amount}"))
            event_name = order.event.title if order.event else 'N/A'
            self.stdout.write(self.style.SUCCESS(f"    - Evento: {event_name}"))
            self.stdout.write(self.style.SUCCESS(f"    - Jugadores registrados: {len(order.registered_players)}"))
            self.stdout.write(self.style.SUCCESS(f"    - Reservas de hotel: {order.hotel_reservations.count()}"))
            # Obtener hoteles y habitaciones directamente desde las reservas
            reservations = order.hotel_reservations.all()
            hotel_ids = set()
            room_ids = set()
            for res in reservations:
                if res.hotel:
                    hotel_ids.add(res.hotel.id)
                if res.room:
                    room_ids.add(res.room.id)
            self.stdout.write(self.style.SUCCESS(f"    - Hoteles: {len(hotel_ids)}"))
            self.stdout.write(self.style.SUCCESS(f"    - Habitaciones: {len(room_ids)}"))

            # Mostrar detalles de reservas
            if order.hotel_reservations.exists():
                self.stdout.write(self.style.SUCCESS(f"\n  [OK] DETALLES DE RESERVAS:"))
                for i, reservation in enumerate(order.hotel_reservations.all(), 1):
                    self.stdout.write(self.style.SUCCESS(f"\n    Reserva {i}:"))
                    self.stdout.write(self.style.SUCCESS(f"      - Hotel: {reservation.hotel.hotel_name}"))
                    self.stdout.write(self.style.SUCCESS(f"      - Habitación: {reservation.room.room_number}"))
                    self.stdout.write(self.style.SUCCESS(f"      - Check-in: {reservation.check_in}"))
                    self.stdout.write(self.style.SUCCESS(f"      - Check-out: {reservation.check_out}"))
                    self.stdout.write(self.style.SUCCESS(f"      - Huéspedes: {reservation.number_of_guests}"))
                    if reservation.additional_guest_details_json:
                        self.stdout.write(self.style.SUCCESS(f"      - Huéspedes adicionales: {len(reservation.additional_guest_details_json)}"))
                        for guest in reservation.additional_guest_details_json:
                            self.stdout.write(
                                self.style.SUCCESS(f"        * {guest.get('name')} ({guest.get('type')}) - {guest.get('birth_date', 'N/A')}")
                            )

            # Mostrar detalles de jugadores registrados
            if order.registered_players.exists():
                self.stdout.write(self.style.SUCCESS(f"\n  [OK] JUGADORES REGISTRADOS:"))
                for player in order.registered_players:
                    self.stdout.write(self.style.SUCCESS(f"    - {player.user.get_full_name()} ({player.division})"))

            # Mostrar Event Attendances
            if order.event and order.registered_player_ids:
                from apps.events.models import EventAttendance
                player_users = [p.user for p in order.registered_players if hasattr(p, 'user')]
                if player_users:
                    attendances = EventAttendance.objects.filter(
                        event=order.event,
                        user__in=player_users,
                        status="confirmed"
                    ).select_related("user", "event")
                    if attendances.exists():
                        self.stdout.write(self.style.SUCCESS(f"\n  [OK] EVENT ATTENDANCES:"))
                        for attendance in attendances:
                            self.stdout.write(
                                self.style.SUCCESS(f"    - {attendance.user.get_full_name()} - Status: {attendance.status}")
                            )
                    self.stdout.write(
                        self.style.SUCCESS(f"    - {attendance.user.get_full_name()} - Status: {attendance.status}")
                    )

            # Verificar breakdown
            if order.breakdown and "hotel_reservations" in order.breakdown:
                self.stdout.write(self.style.SUCCESS(f"\n  [OK] BREAKDOWN DE RESERVAS EN ORDER:"))
                for i, res_info in enumerate(order.breakdown["hotel_reservations"], 1):
                    self.stdout.write(self.style.SUCCESS(f"\n    Reserva {i} (del breakdown):"))
                    self.stdout.write(self.style.SUCCESS(f"      - Habitación: {res_info.get('room_number')}"))
                    self.stdout.write(self.style.SUCCESS(f"      - Hotel: {res_info.get('hotel_name')}"))
                    if res_info.get("additional_guest_details"):
                        self.stdout.write(
                            self.style.SUCCESS(f"      - Huéspedes adicionales: {len(res_info['additional_guest_details'])}")
                        )
                        for guest in res_info["additional_guest_details"]:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"        * {guest.get('name')} ({guest.get('type')}) - {guest.get('birth_date', 'N/A')}"
                                )
                            )

        else:
            self.stdout.write(self.style.ERROR("  [ERROR] NO SE CREO LA ORDEN"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 80))
        self.stdout.write(self.style.SUCCESS("PROCESO COMPLETADO"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

