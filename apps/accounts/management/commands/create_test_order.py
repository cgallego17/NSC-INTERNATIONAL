"""
Comando para crear una orden de prueba con datos de ejemplo.
Útil para probar la funcionalidad del modelo Order.
"""
from decimal import Decimal
from datetime import datetime, timedelta, date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Order, StripeEventCheckout
from apps.events.models import Event


class Command(BaseCommand):
    help = "Crea una orden de prueba con datos de ejemplo para ensayar"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="ID del usuario para crear la orden (si no se especifica, usa el primer usuario disponible)",
        )
        parser.add_argument(
            "--event-id",
            type=int,
            help="ID del evento para asociar la orden (opcional)",
        )
        parser.add_argument(
            "--payment-mode",
            type=str,
            choices=["plan", "now"],
            default="now",
            help="Modo de pago: 'plan' para plan de pagos o 'now' para pago único (default: now)",
        )
        parser.add_argument(
            "--plan-months",
            type=int,
            default=3,
            help="Número de meses del plan (solo si payment-mode es 'plan', default: 3)",
        )

    def handle(self, *args, **options):
        user_id = options.get("user_id")
        event_id = options.get("event_id")
        payment_mode = options.get("payment_mode", "now")
        plan_months = options.get("plan_months", 3)

        self.stdout.write("=" * 60)
        self.stdout.write("CREACION DE ORDEN DE PRUEBA")
        self.stdout.write("=" * 60)

        # Obtener o crear usuario
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Usuario con ID {user_id} no encontrado.")
                )
                return
        else:
            user = User.objects.filter(is_active=True).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR(
                        "No hay usuarios activos en el sistema. Crea un usuario primero."
                    )
                )
                return

        self.stdout.write(f"\nUsuario: {user.get_full_name()} ({user.username})")

        # Obtener o crear evento
        event = None
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                event_name = getattr(event, 'title', getattr(event, 'name', f'Evento #{event.id}'))
                self.stdout.write(f"Evento: {event_name}")
            except Event.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Evento con ID {event_id} no encontrado. Continuando sin evento."
                    )
                )
        else:
            # Buscar un evento existente
            event = Event.objects.first()
            if event:
                event_name = getattr(event, 'title', getattr(event, 'name', f'Evento #{event.id}'))
                self.stdout.write(f"Usando evento existente: {event_name} (ID: {event.id})")
            else:
                # Crear un evento de prueba si no existe ninguno
                try:
                    from apps.events.models import EventCategory

                    # Obtener o crear categoría
                    category = EventCategory.objects.first()
                    if not category:
                        category = EventCategory.objects.create(
                            name="Test Category",
                            description="Categoría de prueba",
                            is_active=True
                        )

                    # Obtener organizador (staff o superuser)
                    organizer = User.objects.filter(is_staff=True).first() or User.objects.filter(is_superuser=True).first() or user

                    event = Event.objects.create(
                        title="Evento de Prueba - Test Event",
                        description="Este es un evento de prueba creado automáticamente para la orden de prueba",
                        start_date=timezone.now() + timedelta(days=30),
                        end_date=timezone.now() + timedelta(days=35),
                        category=category,
                        organizer=organizer,
                        is_published=True,
                        default_entry_fee=Decimal("200.00"),
                    )
                    self.stdout.write(f"Evento de prueba creado: {event.title} (ID: {event.id})")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No se pudo crear evento de prueba: {str(e)}. Continuando sin evento."
                        )
                    )
                    event = None

        # Crear o usar un StripeEventCheckout existente (opcional)
        stripe_checkout = None
        if event:
            # Buscar un checkout existente o crear datos simulados
            stripe_checkout = (
                StripeEventCheckout.objects.filter(user=user, event=event).first()
                if event
                else None
            )

        # Obtener información de hoteles y habitaciones reales
        from apps.locations.models import Hotel, HotelRoom

        hotel1 = Hotel.objects.filter(is_active=True).first()
        hotel2 = Hotel.objects.filter(is_active=True).exclude(id=hotel1.id).first() if hotel1 else None
        if not hotel2:
            hotel2 = hotel1

        room1 = HotelRoom.objects.filter(hotel=hotel1).first() if hotel1 else None
        room2 = HotelRoom.objects.filter(hotel=hotel2).exclude(id=room1.id if room1 else None).first() if hotel2 else None
        if not room2 and room1:
            room2 = room1

        # Crear breakdown de ejemplo
        breakdown = {
            "subtotal": "500.00",
            "players_total": "200.00",
            "hotel_total": "300.00",
            "tax_amount": "80.00",
            "hotel_room_base": "250.00",
            "hotel_services_total": "50.00",
            "hotel_iva": "48.00",
            "hotel_ish": "15.00",
            "hotel_total_taxes": "63.00",
            "hotel_reservations": [
                {
                    "room_id": room1.id if room1 else 1,
                    "room_number": room1.room_number if room1 else "101",
                    "hotel_name": hotel1.hotel_name if hotel1 else "Hotel de Prueba 1",
                    "check_in": "2024-02-15",
                    "check_out": "2024-02-20",
                    "number_of_guests": 4,
                    "guest_name": user.get_full_name() or user.username,
                    "guest_email": user.email,
                    "guest_phone": getattr(user.profile, "phone", "") if hasattr(user, "profile") else "",
                    "additional_guest_names": [
                        "María García López",
                        "Pedro Hernández Martínez",
                        "Ana Rodríguez Sánchez",
                    ],
                },
                {
                    "room_id": room2.id if room2 else 2,
                    "room_number": room2.room_number if room2 else "202",
                    "hotel_name": hotel2.hotel_name if hotel2 else "Hotel de Prueba 2",
                    "check_in": "2024-02-15",
                    "check_out": "2024-02-18",
                    "number_of_guests": 2,
                    "guest_name": user.get_full_name() or user.username,
                    "guest_email": user.email,
                    "guest_phone": getattr(user.profile, "phone", "") if hasattr(user, "profile") else "",
                    "additional_guest_names": ["Carlos Mendez"],
                },
            ],
        }

        # Calcular montos según el modo de pago
        subtotal = Decimal(breakdown["subtotal"])
        tax_amount = Decimal(breakdown.get("tax_amount", "0.00"))
        discount_amount = Decimal("25.00")  # Descuento de ejemplo

        if payment_mode == "plan":
            plan_monthly_amount = (subtotal + tax_amount - discount_amount) / Decimal(str(plan_months))
            plan_total_amount = subtotal + tax_amount - discount_amount
            total_amount = plan_monthly_amount  # Primer pago del plan
            plan_payments_completed = 1
            plan_payments_remaining = plan_months - 1
        else:
            plan_monthly_amount = Decimal("0.00")
            plan_total_amount = Decimal("0.00")
            total_amount = subtotal + tax_amount - discount_amount
            plan_payments_completed = 0
            plan_payments_remaining = 0
            plan_months = 1

        # IDs de jugadores de ejemplo - crear si no existen o actualizar existentes
        from apps.accounts.models import PlayerParent, Player, UserProfile
        from datetime import date

        registered_player_ids = []
        player_parents = PlayerParent.objects.filter(parent=user).select_related("player", "player__user", "player__user__profile")

        positions = ['pitcher', 'catcher', 'shortstop', 'utility']
        divisions = ['10U', '12U', '14U']
        grades = ['4th', '6th', '8th']

        if player_parents.exists():
            self.stdout.write("Actualizando jugadores existentes con datos completos...")
            for i, pp in enumerate(player_parents[:3], 1):
                p = pp.player
                p.division = divisions[i % len(divisions)]
                p.position = positions[i % len(positions)]
                p.height = "5'10\""
                p.weight = 150 + i*5
                p.jersey_number = 10+i
                p.grade = grades[i % len(grades)]
                p.save()

                if hasattr(p.user, 'profile'):
                    prof = p.user.profile
                    prof.phone = f"+1 555-000-{i}"
                    prof.birth_date = date(2012, 1, 1)
                    prof.save()

                registered_player_ids.append(p.id)
        else:
            self.stdout.write(
                self.style.WARNING(
                    "El usuario no tiene jugadores asociados. Creando jugadores de prueba..."
                )
            )
            try:
                # Asegurarse de que el usuario sea padre
                if not hasattr(user, 'profile'):
                    UserProfile.objects.create(user=user, user_type='parent')
                elif user.profile.user_type != 'parent':
                    user.profile.user_type = 'parent'
                    user.profile.save()

                # Crear 2-3 jugadores de prueba con datos completos
                for i in range(1, 3):
                    player_user = User.objects.create_user(
                        username=f"{user.username}_player_{i}_{timezone.now().timestamp()}",
                        email=f"player_{i}_{user.email}" if user.email else f"player_{i}_{user.username}@test.com",
                        first_name=f"Jugador {i}",
                        last_name=user.last_name or "Test",
                        password="test12345",
                    )
                    # Perfil de usuario con teléfono y fecha de nacimiento
                    UserProfile.objects.create(
                        user=player_user,
                        user_type='player',
                        phone=f"+1 555-000-{i}{i}{i}{i}",
                        birth_date=date(2012, 5, 15 + i),
                        address="Street 123 #45-67",
                    )
                    # Perfil de jugador con datos deportivos completos
                    player = Player.objects.create(
                        user=player_user,
                        division=divisions[i % len(divisions)],
                        position=positions[i % len(positions)],
                        secondary_position=positions[(i+1) % len(positions)],
                        is_pitcher=(i % 2 == 0),
                        height="5'8\"",
                        weight=145 + (i * 5),
                        jersey_number=10 + i,
                        batting_hand='R',
                        throwing_hand='R',
                        grade=grades[i % len(grades)],
                        emergency_contact_name="Emergency Contact Test",
                        emergency_contact_phone="+1 999-888-7777",
                        emergency_contact_relation="Parent",
                        medical_conditions="Ninguna / None"
                    )
                    PlayerParent.objects.create(parent=user, player=player)
                    registered_player_ids.append(player.id)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Jugadores de prueba creados: {len(registered_player_ids)}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"No se pudieron crear jugadores de prueba: {str(e)}. Continuando sin jugadores."
                    )
                )

        # Crear o actualizar StripeEventCheckout si no existe
        if not stripe_checkout and event:
            from django.db import transaction
            from datetime import datetime, timedelta

            stripe_session_id = f"cs_test_{timezone.now().timestamp()}"

            # Crear hotel_cart_snapshot con información completa
            hotel_cart_snapshot = {}
            if hotel1 and room1:
                check_in = date.today() + timedelta(days=15)
                check_out = check_in + timedelta(days=5)
                hotel_cart_snapshot["vue-room-1"] = {
                    "type": "room",
                    "room_id": room1.id,
                    "room_number": room1.room_number,
                    "check_in": str(check_in),
                    "check_out": str(check_out),
                    "guests": 4,
                    "services": [],
                    "additional_guest_names": [
                        "María García López",
                        "Pedro Hernández Martínez",
                        "Ana Rodríguez Sánchez",
                    ],
                    "notes": "Additional guests: María García López, Pedro Hernández Martínez, Ana Rodríguez Sánchez",
                }
            if hotel2 and room2 and room2.id != (room1.id if room1 else None):
                check_in2 = date.today() + timedelta(days=15)
                check_out2 = check_in2 + timedelta(days=3)
                hotel_cart_snapshot["vue-room-2"] = {
                    "type": "room",
                    "room_id": room2.id,
                    "room_number": room2.room_number,
                    "check_in": str(check_in2),
                    "check_out": str(check_out2),
                    "guests": 2,
                    "services": [],
                    "additional_guest_names": ["Carlos Mendez"],
                    "notes": "Additional guests: Carlos Mendez",
                }

            with transaction.atomic():
                stripe_checkout = StripeEventCheckout.objects.create(
                    user=user,
                    event=event,
                    stripe_session_id=stripe_session_id,
                    currency="usd",
                    payment_mode=payment_mode,
                    player_ids=registered_player_ids,
                    hotel_cart_snapshot=hotel_cart_snapshot,
                    breakdown=breakdown,
                    amount_total=total_amount,
                    plan_months=plan_months,
                    plan_monthly_amount=plan_monthly_amount,
                    status="paid",
                    paid_at=timezone.now(),
                )

                # Crear reservas reales de hotel si hay hoteles disponibles
                if hotel1 and room1:
                    from apps.locations.models import HotelReservation
                    from datetime import date

                    check_in = date.today() + timedelta(days=15)
                    check_out = check_in + timedelta(days=5)

                    reservation1 = HotelReservation.objects.create(
                        hotel=hotel1,
                        room=room1,
                        user=user,
                        guest_name=user.get_full_name() or user.username,
                        guest_email=user.email,
                        guest_phone=getattr(user.profile, "phone", "") if hasattr(user, "profile") else "",
                        number_of_guests=4,
                        check_in=check_in,
                        check_out=check_out,
                        status="confirmed",
                        notes=f"Reserva pagada vía Stripe session {stripe_session_id}",
                        additional_guest_names="\n".join([
                            "María García López",
                            "Pedro Hernández Martínez",
                            "Ana Rodríguez Sánchez",
                        ]),
                    )
                    reservation1.total_amount = reservation1.calculate_total()
                    reservation1.save()

                if hotel2 and room2 and room2.id != (room1.id if room1 else None):
                    check_in2 = date.today() + timedelta(days=15)
                    check_out2 = check_in2 + timedelta(days=3)

                    reservation2 = HotelReservation.objects.create(
                        hotel=hotel2,
                        room=room2,
                        user=user,
                        guest_name=user.get_full_name() or user.username,
                        guest_email=user.email,
                        guest_phone=getattr(user.profile, "phone", "") if hasattr(user, "profile") else "",
                        number_of_guests=2,
                        check_in=check_in2,
                        check_out=check_out2,
                        status="confirmed",
                        notes=f"Reserva pagada vía Stripe session {stripe_session_id}",
                        additional_guest_names="Carlos Mendez",
                    )
                    reservation2.total_amount = reservation2.calculate_total()
                    reservation2.save()

        # Crear la orden
        try:
            stripe_session_id_for_order = stripe_checkout.stripe_session_id if stripe_checkout else f"cs_test_{timezone.now().timestamp()}"

            order = Order.objects.create(
                user=user,
                stripe_checkout=stripe_checkout,
                event=event,
                status="paid",
                payment_method="stripe",
                payment_mode=payment_mode,
                stripe_session_id=stripe_session_id_for_order,
                stripe_customer_id=f"cus_test_{user.id}",
                stripe_subscription_id=f"sub_test_{timezone.now().timestamp()}" if payment_mode == "plan" else "",
                stripe_subscription_schedule_id=f"sub_sched_test_{timezone.now().timestamp()}" if payment_mode == "plan" else "",
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                currency="usd",
                breakdown=breakdown,
                registered_player_ids=registered_player_ids,
                plan_months=plan_months,
                plan_monthly_amount=plan_monthly_amount,
                plan_total_amount=plan_total_amount,
                plan_payments_completed=plan_payments_completed,
                plan_payments_remaining=plan_payments_remaining,
                notes=f"Orden de prueba creada el {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
                paid_at=timezone.now(),
            )

            self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
            self.stdout.write(self.style.SUCCESS("ORDEN CREADA EXITOSAMENTE"))
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(f"\nOrder ID: {order.id}")
            self.stdout.write(f"Order Number: {order.order_number}")
            self.stdout.write(f"Status: {order.get_status_display()}")
            self.stdout.write(f"Payment Mode: {order.get_payment_mode_display()}")
            self.stdout.write(f"Total Amount: ${order.total_amount}")
            self.stdout.write(f"Currency: {order.currency.upper()}")

            if order.is_payment_plan:
                plan_summary = order.payment_plan_summary
                self.stdout.write(f"\nPlan de Pagos:")
                self.stdout.write(f"  - Total de meses: {plan_summary['total_months']}")
                self.stdout.write(f"  - Monto mensual: ${plan_summary['monthly_amount']}")
                self.stdout.write(f"  - Total del plan: ${plan_summary['total_amount']}")
                self.stdout.write(f"  - Pagos completados: {plan_summary['completed']}")
                self.stdout.write(f"  - Pagos pendientes: {plan_summary['remaining']}")

            if order.has_event_registration:
                self.stdout.write(f"\nJugadores Registrados: {len(order.registered_players)}")
                for player in order.registered_players:
                    self.stdout.write(f"  - {player.user.get_full_name()}")

            if order.has_hotel_reservation:
                reservations = order.hotel_reservations_with_guests
                self.stdout.write(f"\nReservas de Hotel: {len(reservations)}")
                for i, res in enumerate(reservations, 1):
                    self.stdout.write(f"  Reserva {i}:")
                    self.stdout.write(f"    - Habitación: {res.get('room_number', 'N/A')}")
                    self.stdout.write(f"    - Check-in: {res.get('check_in', 'N/A')}")
                    self.stdout.write(f"    - Check-out: {res.get('check_out', 'N/A')}")
                    self.stdout.write(f"    - Huéspedes: {res.get('number_of_guests', 0)}")
                    additional_guests = res.get("additional_guest_names", [])
                    if additional_guests:
                        self.stdout.write(f"    - Huéspedes adicionales:")
                        for guest in additional_guests:
                            self.stdout.write(f"      * {guest}")

            self.stdout.write(self.style.SUCCESS("\nOrden creada exitosamente!"))
            self.stdout.write(f"\nPara ver la orden: Order.objects.get(id={order.id})")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError al crear la orden: {str(e)}"))
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))

