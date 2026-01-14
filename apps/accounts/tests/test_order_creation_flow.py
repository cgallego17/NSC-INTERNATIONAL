"""
Test completo del flujo de creación de órdenes
Verifica que todo el proceso desde el registro del evento hasta la creación de la orden funcione correctamente
"""

import json
import sys
import types
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import (
    Order,
    Player,
    PlayerParent,
    StripeEventCheckout,
    UserProfile,
)
from apps.events.models import Division, Event, EventAttendance, EventCategory
from apps.locations.models import Hotel, HotelReservation, HotelRoom

User = get_user_model()


class _FakeStripeSession:
    def __init__(self, id="sess_test_flow", url="https://stripe.test/checkout"):
        self.id = id
        self.url = url


class OrderCreationFlowTest(TestCase):
    """Test completo del flujo de creación de órdenes"""

    def setUp(self):
        # Mock Stripe
        self._stripe_calls = []
        fake_stripe = types.ModuleType("stripe")
        fake_stripe.api_key = None

        class _CheckoutSession:
            @staticmethod
            def create(**kwargs):
                self._stripe_calls.append(kwargs)
                return _FakeStripeSession(id=f"cs_test_{timezone.now().timestamp()}")

        class _Checkout:
            Session = _CheckoutSession

        fake_stripe.checkout = _Checkout
        sys.modules["stripe"] = fake_stripe

        # Crear divisiones
        self.div_12u = Division.objects.create(name="12U")
        self.div_14u = Division.objects.create(name="14U")

        # Crear usuario padre
        self.parent_user = User.objects.create_user(
            username="test_parent",
            email="parent@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Parent",
        )
        UserProfile.objects.create(
            user=self.parent_user,
            user_type="parent",
            phone="+1 555-123-4567",
        )

        # Crear jugadores (hijos)
        self.player1_user = User.objects.create_user(
            username="player1_user",
            email="player1@test.com",
            password="testpass123",
            first_name="Jugador",
            last_name="Uno",
        )
        UserProfile.objects.create(
            user=self.player1_user,
            user_type="player",
            phone="+1 555-000-0001",
            birth_date=date(2012, 1, 15),
        )
        self.player1 = Player.objects.create(
            user=self.player1_user,
            division=self.div_12u,
            position="catcher",
            jersey_number=10,
            is_active=True,
        )
        PlayerParent.objects.create(parent=self.parent_user, player=self.player1)

        self.player2_user = User.objects.create_user(
            username="player2_user",
            email="player2@test.com",
            password="testpass123",
            first_name="Jugador",
            last_name="Dos",
        )
        UserProfile.objects.create(
            user=self.player2_user,
            user_type="player",
            phone="+1 555-000-0002",
            birth_date=date(2011, 3, 20),
        )
        self.player2 = Player.objects.create(
            user=self.player2_user,
            division=self.div_14u,
            position="shortstop",
            jersey_number=20,
            is_active=True,
        )
        PlayerParent.objects.create(parent=self.parent_user, player=self.player2)

        # Crear categoría de evento
        self.event_category = EventCategory.objects.create(name="Test Category")

        # Crear hotel y habitación
        self.hotel = Hotel.objects.create(
            hotel_name="Test Hotel Mérida",
            address="123 Test Street",
            buy_out_fee=Decimal("1000.00"),
            is_active=True,
        )
        self.room = HotelRoom.objects.create(
            hotel=self.hotel,
            room_number="A1",
            name="Superior Room",
            room_type="double",
            capacity=4,
            price_per_night=Decimal("150.00"),
            price_includes_guests=2,
            additional_guest_price=Decimal("25.00"),
            breakfast_included=False,
            stock=5,  # 5 habitaciones disponibles de este tipo
            is_available=True,
            check_in_date=timezone.localdate(),
            check_out_date=timezone.localdate() + timedelta(days=10),
            check_in_time=timezone.now().time().replace(hour=15, minute=0),
            check_out_time=timezone.now().time().replace(hour=11, minute=0),
        )

        # Crear evento
        check_in_date = timezone.localdate() + timedelta(days=15)
        check_out_date = check_in_date + timedelta(days=5)
        self.event = Event.objects.create(
            title="Test Event 2026",
            description="Evento de prueba",
            organizer=self.parent_user,
            category=self.event_category,
            default_entry_fee=Decimal("500.00"),
            status="published",
            hotel=self.hotel,
            start_date=check_in_date,
            end_date=check_out_date,
            payment_deadline=check_in_date - timedelta(days=5),
        )

    def test_complete_order_creation_flow_with_guest_details(self):
        """
        Test completo del flujo de creación de órdenes con datos completos de huéspedes
        """
        # 1. Preparar datos del checkout
        check_in_date = self.event.start_date
        check_out_date = self.event.end_date
        nights = (check_out_date - check_in_date).days

        # Payload Vue con datos completos de huéspedes
        hotel_payload = {
            "hotel_pk": self.hotel.pk,
            "check_in_date": str(check_in_date),
            "check_out_date": str(check_out_date),
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "nights": nights,
            "rooms": [
                {
                    "roomId": str(self.room.pk),
                    "room_id": self.room.pk,
                    "price": str(self.room.price_per_night),
                    "priceIncludesGuests": self.room.price_includes_guests,
                    "additionalGuestPrice": str(self.room.additional_guest_price),
                    "capacity": self.room.capacity,
                    "room_number": self.room.room_number,
                }
            ],
            "guests": [
                # Huésped principal (índice 0) - el padre
                {
                    "id": f"parent-{self.parent_user.pk}",
                    "name": self.parent_user.get_full_name(),
                    "first_name": self.parent_user.first_name,
                    "last_name": self.parent_user.last_name,
                    "email": self.parent_user.email,
                    "type": "adult",
                    "displayName": self.parent_user.get_full_name(),
                    "isRegistrant": True,
                    "isPlayer": False,
                },
                # Jugador 1 (índice 1)
                {
                    "id": f"player-{self.player1.pk}",
                    "name": self.player1.user.get_full_name(),
                    "first_name": self.player1.user.first_name,
                    "last_name": self.player1.user.last_name,
                    "email": self.player1.user.email,
                    "type": "child",
                    "birth_date": "2012-01-15",
                    "displayName": self.player1.user.get_full_name(),
                    "isRegistrant": False,
                    "isPlayer": True,
                },
                # Jugador 2 (índice 2)
                {
                    "id": f"player-{self.player2.pk}",
                    "name": self.player2.user.get_full_name(),
                    "first_name": self.player2.user.first_name,
                    "last_name": self.player2.user.last_name,
                    "email": self.player2.user.email,
                    "type": "child",
                    "birth_date": "2011-03-20",
                    "displayName": self.player2.user.get_full_name(),
                    "isRegistrant": False,
                    "isPlayer": True,
                },
                # Huésped adicional adulto (índice 3)
                {
                    "id": "manual-1",
                    "name": "María García López",
                    "first_name": "María",
                    "last_name": "García López",
                    "type": "adult",
                    "birth_date": "1990-02-20",
                    "email": "maria@example.com",
                    "displayName": "María García López",
                    "isRegistrant": False,
                    "isPlayer": False,
                },
                # Huésped adicional niño (índice 4)
                {
                    "id": "manual-2",
                    "name": "Ana Rodríguez Sánchez",
                    "first_name": "Ana",
                    "last_name": "Rodríguez Sánchez",
                    "type": "child",
                    "birth_date": "2013-02-02",
                    "email": "",
                    "displayName": "Ana Rodríguez Sánchez",
                    "isRegistrant": False,
                    "isPlayer": False,
                },
            ],
            "guest_assignments": {
                str(self.room.pk): [
                    0,
                    1,
                    3,
                    4,
                ],  # Principal, jugador1, adulto adicional, niño adicional
            },
        }

        # 2. Crear sesión de checkout
        self.client.force_login(self.parent_user)
        url = reverse(
            "accounts:create_stripe_event_checkout_session",
            kwargs={"pk": self.event.pk},
        )

        # Preparar datos del POST
        # El TestClient de Django necesita que los múltiples valores se pasen como string codificado
        from urllib.parse import urlencode

        # Codificar los datos manualmente para soportar múltiples valores con el mismo nombre
        post_data = {
            "payment_mode": "now",
            "hotel_reservation_json": json.dumps(hotel_payload),
        }

        # Agregar players múltiples veces
        post_str = urlencode(post_data)
        # Agregar players manualmente
        for player_id in [str(self.player1.pk), str(self.player2.pk)]:
            post_str += f"&players={player_id}"

        response = self.client.post(
            url,
            data=post_str,
            content_type="application/x-www-form-urlencoded",
        )

        # 3. Verificar que se creó el checkout
        if response.status_code != 200:
            try:
                error_data = json.loads(response.content)
                error_msg = f"Error en respuesta {response.status_code}: {error_data.get('error', error_data)}"
            except:
                error_msg = f"Error en respuesta {response.status_code}: {response.content.decode('utf-8')[:500]}"
            self.fail(error_msg)

        response_data = json.loads(response.content)
        self.assertTrue(response_data.get("success"), f"Response data: {response_data}")
        self.assertIn("checkout_url", response_data)

        # Verificar que se creó StripeEventCheckout
        checkout = StripeEventCheckout.objects.get(
            user=self.parent_user, event=self.event
        )
        self.assertEqual(checkout.status, "created")
        # Verificar que ambos players están en la lista (pueden estar en cualquier orden)
        self.assertIn(self.player1.pk, checkout.player_ids)
        self.assertIn(self.player2.pk, checkout.player_ids)
        self.assertEqual(len(checkout.player_ids), 2)
        self.assertEqual(checkout.payment_mode, "now")

        # 4. Verificar que el hotel_cart_snapshot tiene datos completos de huéspedes
        hotel_cart = checkout.hotel_cart_snapshot
        self.assertIsInstance(hotel_cart, dict)
        room_key = f"vue-room-{self.room.pk}"
        self.assertIn(room_key, hotel_cart)

        room_data = hotel_cart[room_key]
        self.assertEqual(room_data["room_id"], self.room.pk)
        self.assertEqual(room_data["guests"], 4)  # Principal + jugador1 + 2 adicionales

        # Verificar que additional_guest_details tiene datos completos
        additional_guests = room_data.get("additional_guest_details", [])
        self.assertEqual(
            len(additional_guests), 3
        )  # Jugador1 + 2 adicionales (excluye principal)

        # Verificar datos del jugador1 (primer adicional)
        guest1 = additional_guests[0]
        self.assertEqual(guest1["name"], self.player1.user.get_full_name())
        self.assertEqual(guest1["type"], "child")
        self.assertEqual(guest1["birth_date"], "2012-01-15")

        # Verificar datos del huésped adicional adulto
        adult_guest = next(
            (g for g in additional_guests if g["name"] == "María García López"), None
        )
        self.assertIsNotNone(adult_guest)
        self.assertEqual(adult_guest["name"], "María García López")
        self.assertEqual(adult_guest["type"], "adult")
        self.assertEqual(adult_guest["birth_date"], "1990-02-20")
        self.assertEqual(adult_guest["email"], "maria@example.com")

        # Verificar datos del huésped adicional niño
        child_guest = next(
            (g for g in additional_guests if g["name"] == "Ana Rodríguez Sánchez"), None
        )
        self.assertIsNotNone(child_guest)
        self.assertEqual(child_guest["name"], "Ana Rodríguez Sánchez")
        self.assertEqual(child_guest["type"], "child")
        self.assertEqual(child_guest["birth_date"], "2013-02-02")

        # 5. Simular pago exitoso - finalizar checkout
        from apps.accounts.views_private import _finalize_stripe_event_checkout

        # La función _finalize_stripe_event_checkout verifica si status == "paid" y retorna temprano
        # Por lo tanto, NO debemos marcarlo como paid antes. La función misma lo marca.
        # Simulamos que Stripe confirmó el pago pero el checkout aún está en "created"

        _finalize_stripe_event_checkout(checkout)

        # Verificar que ahora está marcado como paid
        checkout.refresh_from_db()
        self.assertEqual(checkout.status, "paid")

        # 6. Verificar que se crearon los EventAttendance
        attendance1 = EventAttendance.objects.get(
            event=self.event, user=self.player1.user
        )
        self.assertEqual(attendance1.status, "confirmed")
        self.assertIn(checkout.stripe_session_id, attendance1.notes)

        attendance2 = EventAttendance.objects.get(
            event=self.event, user=self.player2.user
        )
        self.assertEqual(attendance2.status, "confirmed")

        # 7. Verificar que se creó la HotelReservation
        reservation = HotelReservation.objects.get(
            hotel=self.hotel,
            room=self.room,
            user=self.parent_user,
            status="confirmed",
        )
        self.assertEqual(reservation.guest_name, self.parent_user.get_full_name())
        self.assertEqual(reservation.guest_email, self.parent_user.email)
        self.assertEqual(reservation.number_of_guests, 4)
        self.assertEqual(reservation.check_in, check_in_date)
        self.assertEqual(reservation.check_out, check_out_date)
        self.assertIn(checkout.stripe_session_id, reservation.notes)

        # 7.1. Verificar que el stock se descontó correctamente
        self.room.refresh_from_db()
        initial_stock = 5  # stock inicial configurado en setUp
        self.assertEqual(
            self.room.stock,
            initial_stock - 1,
            "El stock debería haberse descontado en 1 al crear la reserva",
        )

        # 8. Verificar que additional_guest_details_json tiene los datos completos
        guest_details = reservation.additional_guest_details_json
        self.assertIsInstance(guest_details, list)
        self.assertEqual(len(guest_details), 3)  # Jugador1 + 2 adicionales

        # Verificar que el jugador está en los detalles
        player1_guest = next(
            (
                g
                for g in guest_details
                if g.get("name") == self.player1.user.get_full_name()
            ),
            None,
        )
        self.assertIsNotNone(player1_guest)
        self.assertEqual(player1_guest["type"], "child")
        self.assertEqual(player1_guest["birth_date"], "2012-01-15")

        # Verificar huésped adulto
        adult_detail = next(
            (g for g in guest_details if g.get("name") == "María García López"), None
        )
        self.assertIsNotNone(adult_detail)
        self.assertEqual(adult_detail["name"], "María García López")
        self.assertEqual(adult_detail["type"], "adult")
        self.assertEqual(adult_detail["birth_date"], "1990-02-20")
        self.assertEqual(adult_detail["email"], "maria@example.com")

        # Verificar huésped niño
        child_detail = next(
            (g for g in guest_details if g.get("name") == "Ana Rodríguez Sánchez"), None
        )
        self.assertIsNotNone(child_detail)
        self.assertEqual(child_detail["name"], "Ana Rodríguez Sánchez")
        self.assertEqual(child_detail["type"], "child")
        self.assertEqual(child_detail["birth_date"], "2013-02-02")

        # 9. Verificar que se creó la Order
        order = Order.objects.get(stripe_checkout=checkout)
        self.assertEqual(order.user, self.parent_user)
        self.assertEqual(order.event, self.event)
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.payment_method, "stripe")
        self.assertEqual(order.payment_mode, "now")
        self.assertEqual(
            order.registered_player_ids, [self.player1.pk, self.player2.pk]
        )
        self.assertGreater(order.total_amount, Decimal("0"))

        # 10. Verificar que el breakdown de la Order incluye datos completos
        breakdown = order.breakdown
        self.assertIn("hotel_reservations", breakdown)
        hotel_reservations_info = breakdown["hotel_reservations"]
        self.assertEqual(len(hotel_reservations_info), 1)

        reservation_info = hotel_reservations_info[0]
        self.assertEqual(reservation_info["hotel_name"], self.hotel.hotel_name)
        self.assertEqual(reservation_info["room_number"], self.room.room_number)
        self.assertEqual(reservation_info["number_of_guests"], 4)

        # Verificar que additional_guest_details está en el breakdown
        self.assertIn("additional_guest_details", reservation_info)
        breakdown_guests = reservation_info["additional_guest_details"]
        self.assertEqual(len(breakdown_guests), 3)

        # Verificar que los datos completos están en el breakdown
        breakdown_adult = next(
            (g for g in breakdown_guests if g.get("name") == "María García López"), None
        )
        self.assertIsNotNone(breakdown_adult)
        self.assertEqual(breakdown_adult["type"], "adult")
        self.assertEqual(breakdown_adult["birth_date"], "1990-02-20")
        self.assertEqual(breakdown_adult["email"], "maria@example.com")

        # 11. Verificar la property additional_guest_details del modelo
        reservation_details = reservation.additional_guest_details
        self.assertEqual(len(reservation_details), 3)
        self.assertEqual(
            reservation_details[0]["name"], self.player1.user.get_full_name()
        )
        self.assertEqual(reservation_details[0]["type"], "child")

        # 12. Verificar que los datos están correctamente vinculados
        # Order -> HotelReservation
        order_reservations = order.hotel_reservations
        self.assertEqual(order_reservations.count(), 1)
        self.assertEqual(order_reservations.first().id, reservation.id)

        # Order -> EventAttendance (a través de registered_player_ids)
        # Obtener los usuarios de los jugadores
        player_user_ids = Player.objects.filter(
            id__in=order.registered_player_ids
        ).values_list("user_id", flat=True)

        registered_attendances = EventAttendance.objects.filter(
            event=self.event,
            user_id__in=list(player_user_ids),
            status="confirmed",
        )
        self.assertEqual(registered_attendances.count(), 2)

        # Verificación final
        print("\nTest completo del flujo de creacion de ordenes PASO")
        print(f"   - Checkout creado: {checkout.stripe_session_id}")
        print(f"   - Order creada: {order.order_number}")
        print(f"   - Reserva creada: #{reservation.id}")
        print(f"   - EventAttendances creados: {registered_attendances.count()}")
        print(f"   - Huespedes adicionales guardados: {len(guest_details)}")
        print(f"   - Stock restante: {self.room.stock}")

    def test_stock_validation_prevents_checkout_when_no_stock(self):
        """
        Test que verifica que no se puede crear un checkout si no hay stock disponible
        """
        # Configurar habitación con stock limitado
        self.room.stock = 1  # Solo 1 habitación disponible
        self.room.save()

        # Crear una reserva previa que consuma el stock
        from datetime import date, timedelta

        from apps.locations.models import HotelReservation

        check_in_date = self.event.start_date
        check_out_date = self.event.end_date

        HotelReservation.objects.create(
            hotel=self.hotel,
            room=self.room,
            user=self.parent_user,
            guest_name="Otro Usuario",
            guest_email="otro@test.com",
            guest_phone="+1 555-999-9999",
            number_of_guests=2,
            check_in=check_in_date,
            check_out=check_out_date,
            status="confirmed",
        )

        # Verificar que el stock está agotado
        active_count = self.room.reservations.filter(
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
            status__in=["pending", "confirmed", "checked_in"],
        ).count()
        self.assertEqual(active_count, 1)
        self.assertTrue(
            active_count >= self.room.stock, "El stock debería estar agotado"
        )

        # Intentar crear checkout con habitación sin stock
        self.client.force_login(self.parent_user)
        url = reverse(
            "accounts:create_stripe_event_checkout_session",
            kwargs={"pk": self.event.pk},
        )

        # Preparar payload con la misma habitación
        hotel_payload = {
            "hotel_pk": self.hotel.pk,
            "check_in_date": str(check_in_date),
            "check_out_date": str(check_out_date),
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "nights": (check_out_date - check_in_date).days,
            "rooms": [
                {
                    "roomId": str(self.room.pk),
                    "room_id": self.room.pk,
                    "price": str(self.room.price_per_night),
                    "priceIncludesGuests": self.room.price_includes_guests,
                    "additionalGuestPrice": str(self.room.additional_guest_price),
                    "capacity": self.room.capacity,
                    "room_number": self.room.room_number,
                }
            ],
            "guests": [
                {
                    "id": f"parent-{self.parent_user.pk}",
                    "name": self.parent_user.get_full_name(),
                    "type": "adult",
                    "displayName": self.parent_user.get_full_name(),
                }
            ],
            "guest_assignments": {
                str(self.room.pk): [0],
            },
        }

        from urllib.parse import urlencode

        from django.http import QueryDict

        post_data = QueryDict(mutable=True)
        post_data.setlist("players", [str(self.player1.pk)])
        post_data["payment_mode"] = "now"
        post_data["hotel_reservation_json"] = json.dumps(hotel_payload)

        response = self.client.post(url, post_data)

        # Debe retornar error 400 indicando que no hay stock disponible
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data.get("success"))
        self.assertIn("not available", response_data.get("error", "").lower())

        # Verificar que NO se creó ningún checkout
        checkout_count = StripeEventCheckout.objects.filter(
            user=self.parent_user, event=self.event
        ).count()
        self.assertEqual(checkout_count, 0, "No debería haberse creado ningún checkout")
