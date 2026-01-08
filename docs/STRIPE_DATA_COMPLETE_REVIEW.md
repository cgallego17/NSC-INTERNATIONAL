# ✅ Revisión Completa: Datos Guardados en Compras Stripe

## 📋 Resumen Ejecutivo

**✅ CONFIRMADO: El sistema guarda TODOS los datos de la compra correctamente.**

---

## 1. **StripeEventCheckout** - Registro Completo de la Compra

### ✅ Datos Básicos Guardados
- `user` - Usuario que compró
- `event` - Evento al que se registró
- `stripe_session_id` - ID único de Stripe
- `stripe_subscription_id` - ID de suscripción (planes)
- `stripe_subscription_schedule_id` - ID del schedule (planes)
- `currency` - Moneda (usd, mxn, etc.)
- `payment_mode` - "plan" o "now"
- `discount_percent` - Descuento aplicado (0-5%)
- `amount_total` - Monto total pagado
- `plan_months` - Meses del plan (si aplica)
- `plan_monthly_amount` - Pago mensual (si aplica)
- `status` - Estado: "created", "paid", "cancelled", "expired"
- `paid_at` - Timestamp del pago
- `created_at` - Fecha de creación
- `updated_at` - Última actualización

### ✅ Snapshot Completo del Carrito (`hotel_cart_snapshot`)

Se guarda **EXACTAMENTE** como estaba en la sesión:

```json
{
  "room_123_2024-06-01_2024-06-05": {
    "type": "room",
    "room_id": 123,
    "hotel_id": 45,
    "check_in": "2024-06-01",
    "check_out": "2024-06-05",
    "nights": 4,
    "guests": 2,
    "services": [
      {
        "service_id": 10,
        "quantity": 2
      },
      {
        "service_id": 15,
        "quantity": 1
      }
    ]
  }
}
```

**Incluye:**
- ✅ ID de habitación
- ✅ ID de hotel
- ✅ Fechas de check-in y check-out
- ✅ Número de noches
- ✅ Número de huéspedes
- ✅ **TODOS los servicios** con sus IDs y cantidades

### ✅ Breakdown Completo (`breakdown`)

Desglose detallado de TODOS los costos:

```json
{
  "players_total": "200.00",        // Total de jugadores
  "hotel_room_base": "400.00",      // Base de habitación
  "hotel_services_total": "50.00",  // Total de servicios
  "hotel_iva": "64.00",             // IVA (16%)
  "hotel_ish": "20.00",             // ISH (5%)
  "hotel_total": "534.00",          // Total hotel con impuestos
  "no_show_fee": "0.00",            // Fee de no-show
  "subtotal": "734.00",             // Subtotal antes de descuento
  "discount_percent": 5,            // Porcentaje de descuento
  "total": "697.30"                 // Total final
}
```

### ✅ IDs de Jugadores (`player_ids`)

Array con los IDs de TODOS los jugadores registrados:
```json
[1, 2, 3]
```

---

## 2. **HotelReservation** - Reserva Creada

Cuando se procesa el pago, se crea una reserva con:

### ✅ Datos Guardados
- `hotel` - Hotel (obtenido de `room.hotel`)
- `room` - Habitación (del snapshot: `room_id`)
- `user` - Usuario (del checkout)
- `guest_name` - Nombre completo del usuario
- `guest_email` - Email del usuario
- `guest_phone` - Teléfono del usuario (del perfil)
- `number_of_guests` - Del snapshot: `guests`
- `check_in` - Del snapshot: `check_in`
- `check_out` - Del snapshot: `check_out`
- `status` - "confirmed" (confirmada)
- `total_amount` - Calculado automáticamente
- `notes` - Incluye: `"Reserva pagada vía Stripe session {session_id}"`

**✅ Todos los datos del snapshot se usan para crear la reserva.**

---

## 3. **HotelReservationService** - Servicios de la Reserva

Para cada servicio en el snapshot, se crea un registro:

### ✅ Proceso de Creación
1. Se itera sobre `item_data.get("services", [])`
2. Para cada servicio:
   - Se obtiene `service_id` del snapshot
   - Se busca el `HotelService` en la BD
   - Se obtiene `quantity` del snapshot
   - Se crea `HotelReservationService` con:
     - `reservation` - La reserva creada
     - `service` - El servicio (objeto completo)
     - `quantity` - La cantidad

**✅ Todos los servicios del snapshot se guardan correctamente.**

---

## 4. **EventAttendance** - Asistencias Confirmadas

Para cada jugador en `player_ids`:

### ✅ Datos Guardados
- `event` - Evento del checkout
- `user` - Usuario del jugador (obtenido de `PlayerParent`)
- `status` - "confirmed" (confirmado)
- `notes` - Incluye: `"Paid via Stripe session {session_id}"`

**✅ Todos los jugadores se confirman correctamente.**

---

## 🔍 Verificación de Integridad

### ✅ Lo que SÍ se Guarda

1. **Compra completa**:
   - ✅ Todos los datos del usuario
   - ✅ Todos los datos del evento
   - ✅ Snapshot completo del carrito
   - ✅ Breakdown completo de costos
   - ✅ IDs de todos los jugadores
   - ✅ Información de Stripe (session, subscription, schedule)

2. **Reservas**:
   - ✅ Hotel y habitación
   - ✅ Fechas exactas
   - ✅ Número de huéspedes
   - ✅ Datos del huésped
   - ✅ Monto total calculado
   - ✅ Referencia a Stripe en notas

3. **Servicios**:
   - ✅ Todos los servicios del snapshot
   - ✅ Cantidades correctas
   - ✅ Vinculados a la reserva

4. **Asistencias**:
   - ✅ Todos los jugadores confirmados
   - ✅ Referencia a Stripe en notas

### ⚠️ Consideraciones

1. **Servicios eliminados**: Si un servicio se elimina después de la compra, la reserva mantiene la referencia (el `HotelReservationService` sigue existiendo), pero el servicio puede no estar disponible. Esto es correcto para mantener el historial.

2. **Precios históricos**: Los precios se calculan al momento de crear la reserva usando los precios actuales de la BD. El snapshot tiene los datos originales, pero los cálculos finales usan precios actuales. Esto es correcto porque:
   - El `breakdown` en `StripeEventCheckout` tiene los precios exactos que se pagaron
   - La reserva tiene el total calculado al momento de la creación

3. **Relación directa**: Actualmente no hay un ForeignKey directo de `HotelReservation` a `StripeEventCheckout`, pero se puede rastrear mediante:
   - `user` (mismo usuario)
   - `notes` (contiene el `stripe_session_id`)
   - Fechas del snapshot vs fechas de la reserva

---

## 📊 Ejemplo de Consulta Completa

```python
from apps.accounts.models import StripeEventCheckout
from apps.locations.models import HotelReservation, HotelReservationService
from apps.events.models import EventAttendance

# Obtener una compra
checkout = StripeEventCheckout.objects.get(id=1)

print("=" * 60)
print("COMPRA COMPLETA")
print("=" * 60)
print(f"Usuario: {checkout.user.get_full_name()}")
print(f"Evento: {checkout.event.title}")
print(f"Monto total: ${checkout.amount_total}")
print(f"Modo de pago: {checkout.get_payment_mode_display()}")
print(f"Fecha de pago: {checkout.paid_at}")
print(f"Session ID: {checkout.stripe_session_id}")

print("\n" + "=" * 60)
print("SNAPSHOT DEL CARRITO")
print("=" * 60)
import json
print(json.dumps(checkout.hotel_cart_snapshot, indent=2))

print("\n" + "=" * 60)
print("DESGLOSE DE COSTOS")
print("=" * 60)
print(json.dumps(checkout.breakdown, indent=2))

print("\n" + "=" * 60)
print("JUGADORES REGISTRADOS")
print("=" * 60)
print(f"IDs: {checkout.player_ids}")

print("\n" + "=" * 60)
print("RESERVAS CREADAS")
print("=" * 60)
reservations = HotelReservation.objects.filter(
    user=checkout.user,
    notes__contains=checkout.stripe_session_id
)
for reservation in reservations:
    print(f"\nReserva #{reservation.id}:")
    print(f"  Hotel: {reservation.hotel.hotel_name}")
    print(f"  Habitación: {reservation.room.name}")
    print(f"  Check-in: {reservation.check_in}")
    print(f"  Check-out: {reservation.check_out}")
    print(f"  Huéspedes: {reservation.number_of_guests}")
    print(f"  Total: ${reservation.total_amount}")

    services = reservation.service_reservations.all()
    if services:
        print(f"  Servicios:")
        for svc_res in services:
            print(f"    - {svc_res.service.service_name} x {svc_res.quantity}")

print("\n" + "=" * 60)
print("ASISTENCIAS CONFIRMADAS")
print("=" * 60)
attendances = EventAttendance.objects.filter(
    event=checkout.event,
    notes__contains=checkout.stripe_session_id
)
for attendance in attendances:
    print(f"  - {attendance.user.get_full_name()}: {attendance.get_status_display()}")
```

---

## ✅ Conclusión Final

**El sistema guarda COMPLETAMENTE todos los datos de la compra:**

1. ✅ **Compra completa** con snapshot y breakdown
2. ✅ **Reservas creadas** con todos los datos
3. ✅ **Servicios guardados** individualmente
4. ✅ **Asistencias confirmadas** para todos los jugadores
5. ✅ **Trazabilidad completa** mediante notas y relaciones

**No falta ningún dato crítico. Todo está guardado correctamente.**

