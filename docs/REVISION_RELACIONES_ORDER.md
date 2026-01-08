# Revisión de Relaciones del Modelo Order

## ✅ Estado: **TODAS LAS RELACIONES ESTÁN CORRECTAS**

---

## 📋 Relaciones Directas (ForeignKeys)

### 1. ✅ **Evento** (`event`)
```python
event = models.ForeignKey(
    "events.Event",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders",
    verbose_name="Evento",
    help_text="Evento relacionado (si aplica)",
)
```

**Relación:** Order → Event
**Estado:** ✅ Correcta
**Acceso:** `order.event`

---

### 2. ✅ **Usuario** (`user`)
```python
user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="orders",
    verbose_name="Usuario",
    help_text="Usuario que realiza la compra",
)
```

**Relación:** Order → User
**Estado:** ✅ Correcta
**Acceso:** `order.user`

---

### 3. ✅ **Stripe Checkout** (`stripe_checkout`)
```python
stripe_checkout = models.ForeignKey(
    StripeEventCheckout,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders",
    verbose_name="Checkout de Stripe",
    help_text="Checkout de Stripe relacionado (si aplica)",
)
```

**Relación:** Order → StripeEventCheckout
**Estado:** ✅ Correcta
**Acceso:** `order.stripe_checkout`

---

## 🔗 Relaciones Indirectas (a través de otras tablas)

### 4. ✅ **Reservas de Hotel** (`hotel_reservations`)

**Relación:** Order → HotelReservation (a través de `HotelReservation.order`)

**Implementación:**
```python
@property
def hotel_reservations(self):
    """
    Obtiene las reservas de hotel relacionadas a esta orden.
    Prioriza la relación directa a través de la ForeignKey 'order',
    con fallback a la búsqueda por stripe_session_id en notes (para compatibilidad con datos antiguos).
    """
    from apps.locations.models import HotelReservation

    # Primero intentar obtener por relación directa (más eficiente y robusto)
    reservations = HotelReservation.objects.filter(order=self)
    if reservations.exists():
        return reservations

    # Fallback: búsqueda por stripe_session_id en notes (para datos antiguos)
    session_id = None
    if self.stripe_checkout and self.stripe_checkout.stripe_session_id:
        session_id = self.stripe_checkout.stripe_session_id
    elif self.stripe_session_id:
        session_id = self.stripe_session_id

    if session_id:
        return HotelReservation.objects.filter(
            notes__icontains=session_id,
            user=self.user,
        )
    return HotelReservation.objects.none()
```

**Acceso:** `order.hotel_reservations`
**Estado:** ✅ Correcta (tiene fallback para datos antiguos)

---

### 5. ✅ **Hoteles** (`hotels`)

**Relación:** Order → HotelReservation → Hotel

**Implementación:**
```python
@property
def hotels(self):
    """Obtiene los hoteles únicos relacionados con esta orden a través de las reservas"""
    reservations = self.hotel_reservations.select_related("hotel")
    hotel_ids = set()
    hotels = []
    for reservation in reservations:
        if reservation.hotel and reservation.hotel.id not in hotel_ids:
            hotels.append(reservation.hotel)
            hotel_ids.add(reservation.hotel.id)
    return hotels
```

**Acceso:** `order.hotels`
**Estado:** ✅ Correcta (nueva propiedad agregada)

---

### 6. ✅ **Habitaciones** (`rooms`)

**Relación:** Order → HotelReservation → HotelRoom

**Implementación:**
```python
@property
def rooms(self):
    """Obtiene las habitaciones únicas relacionadas con esta orden a través de las reservas"""
    reservations = self.hotel_reservations.select_related("room")
    room_ids = set()
    rooms = []
    for reservation in reservations:
        if reservation.room and reservation.room.id not in room_ids:
            rooms.append(reservation.room)
            room_ids.add(reservation.room.id)
    return rooms
```

**Acceso:** `order.rooms`
**Estado:** ✅ Correcta (nueva propiedad agregada)

---

### 7. ✅ **Jugadores Registrados** (`registered_players`)

**Relación:** Order → Player (a través de `registered_player_ids` JSONField)

**Implementación:**
```python
# Campo en el modelo:
registered_player_ids = models.JSONField(
    default=list,
    blank=True,
    verbose_name="IDs de Jugadores Registrados",
    help_text="Lista de IDs de jugadores registrados en el evento",
)

# Property:
@property
def registered_players(self):
    """Obtiene los jugadores registrados en el evento de esta orden"""
    if not self.registered_player_ids:
        return []

    try:
        # Player ya está definido en este mismo módulo (apps/accounts/models.py)
        return Player.objects.filter(
            id__in=self.registered_player_ids, is_active=True
        ).select_related("user")
    except Exception:
        return []
```

**Acceso:** `order.registered_players`
**Estado:** ✅ Correcta

---

### 8. ✅ **Event Attendances** (`event_attendances`)

**Relación:** Order → Event → EventAttendance (a través de jugadores registrados)

**Implementación:**
```python
@property
def event_attendances(self):
    """Obtiene los registros de asistencia al evento (EventAttendance) relacionados con esta orden"""
    if not self.event or not self.registered_player_ids:
        return []

    try:
        from apps.events.models import EventAttendance
        # Obtener los usuarios de los jugadores registrados
        player_users = [player.user for player in self.registered_players if hasattr(player, 'user')]
        if not player_users:
            return []

        return EventAttendance.objects.filter(
            event=self.event,
            user__in=player_users,
            status="confirmed"
        ).select_related("user", "event")
    except Exception:
        return []
```

**Acceso:** `order.event_attendances`
**Estado:** ✅ Correcta (nueva propiedad agregada)

---

## 📊 Resumen de Accesos

### Relaciones Directas:
- ✅ `order.event` - Evento relacionado
- ✅ `order.user` - Usuario que realizó la compra
- ✅ `order.stripe_checkout` - Checkout de Stripe relacionado

### Propiedades (Relaciones Indirectas):
- ✅ `order.hotel_reservations` - QuerySet de reservas de hotel
- ✅ `order.hotels` - Lista de hoteles únicos (nueva)
- ✅ `order.rooms` - Lista de habitaciones únicas (nueva)
- ✅ `order.registered_players` - QuerySet de jugadores registrados
- ✅ `order.event_attendances` - QuerySet de registros de asistencia al evento (nueva)
- ✅ `order.hotel_reservations_with_guests` - Información detallada de reservas con huéspedes

### Propiedades de Verificación:
- ✅ `order.has_event_registration` - Verifica si hay registro de evento
- ✅ `order.has_hotel_reservation` - Verifica si hay reservas de hotel
- ✅ `order.is_payment_plan` - Verifica si es plan de pagos

---

## 🔍 Ejemplo de Uso

```python
# Obtener una orden
order = Order.objects.get(order_number="ORD-20260107195044-1")

# Acceder al evento
event = order.event  # ✅ Directo

# Acceder a las reservas de hotel
reservations = order.hotel_reservations  # ✅ A través de property

# Acceder a los hoteles únicos
hotels = order.hotels  # ✅ Nueva propiedad

# Acceder a las habitaciones únicas
rooms = order.rooms  # ✅ Nueva propiedad

# Acceder a los jugadores registrados
players = order.registered_players  # ✅ A través de property

# Acceder a los registros de asistencia al evento
attendances = order.event_attendances  # ✅ Nueva propiedad

# Verificar relaciones
if order.has_event_registration:
    print(f"Evento: {order.event.name}")
    print(f"Jugadores registrados: {[p.user.get_full_name() for p in order.registered_players]}")

if order.has_hotel_reservation:
    print(f"Hoteles: {[h.hotel_name for h in order.hotels]}")
    print(f"Habitaciones: {[r.room_number for r in order.rooms]}")
    for reservation in order.hotel_reservations:
        print(f"Reserva #{reservation.id}: {reservation.room.room_number} en {reservation.hotel.hotel_name}")
```

---

## ✅ Conclusión

**Todas las relaciones están correctamente implementadas:**

1. ✅ **Evento**: Relación directa (ForeignKey)
2. ✅ **Hotel**: Acceso a través de `hotels` property (desde reservas)
3. ✅ **Habitaciones**: Acceso a través de `rooms` property (desde reservas)
4. ✅ **Jugadores registrados**: Acceso a través de `registered_players` property (desde `registered_player_ids`)
5. ✅ **Event Attendances**: Acceso a través de `event_attendances` property (nueva)
6. ✅ **Reservas de hotel**: Acceso a través de `hotel_reservations` property

**Mejoras realizadas:**
- ✅ Agregada propiedad `hotels` para acceso directo a hoteles
- ✅ Agregada propiedad `rooms` para acceso directo a habitaciones
- ✅ Agregada propiedad `event_attendances` para acceso directo a registros de asistencia

**No se requieren cambios adicionales.**

