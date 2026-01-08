# Datos de Transacción Guardados en la Base de Datos

## Modelo Principal: `StripeEventCheckout`

Toda la información de la transacción se guarda en el modelo `StripeEventCheckout` en la base de datos. Este modelo almacena un snapshot completo de la transacción al momento del checkout.

### Campos del Modelo

#### Información del Usuario y Evento
- **`user`** (ForeignKey): Usuario que realizó el pago
- **`event`** (ForeignKey): Evento para el cual se realizó el pago

#### Información de Stripe
- **`stripe_session_id`** (CharField, unique): ID de la sesión de checkout de Stripe
- **`stripe_subscription_id`** (CharField): ID de la suscripción (si es plan de pagos)
- **`stripe_subscription_schedule_id`** (CharField): ID del schedule de la suscripción (para detener después de N meses)
- **`currency`** (CharField): Moneda del pago (default: "usd")

#### Información del Pago
- **`payment_mode`** (CharField): Modo de pago ("plan" o "now")
- **`discount_percent`** (PositiveSmallIntegerField): Porcentaje de descuento aplicado (0-100)
- **`amount_total`** (DecimalField): Monto total pagado
- **`plan_months`** (PositiveIntegerField): Número de meses del plan de pagos
- **`plan_monthly_amount`** (DecimalField): Monto mensual del plan de pagos

#### Estado y Fechas
- **`status`** (CharField): Estado del checkout ("created", "paid", "cancelled", "expired")
- **`paid_at`** (DateTimeField): Fecha y hora en que se completó el pago
- **`created_at`** (DateTimeField): Fecha y hora de creación
- **`updated_at`** (DateTimeField): Fecha y hora de última actualización

### Campos JSON (Snapshots Completos)

#### 1. `player_ids` (JSONField)
Lista de IDs de los jugadores registrados en el evento:
```json
[1, 2, 3]
```

#### 2. `hotel_cart_snapshot` (JSONField)
Snapshot completo del carrito de hotel al momento del checkout. Incluye:

**Para cada habitación:**
```json
{
  "item_123": {
    "type": "room",
    "room_id": 5,
    "hotel_id": 2,
    "check_in": "2024-03-15",
    "check_out": "2024-03-20",
    "guests": 3,
    "guests_included": 2,           // Huéspedes incluidos en el precio base
    "extra_guests": 1,              // Huéspedes adicionales
    "additional_guest_price": "50.00", // Precio por huésped adicional
    "services": [
      {
        "service_id": 10,
        "quantity": 2,
        "name": "Breakfast",
        "price": "15.00"
      }
    ],
    "room_name": "Standard Double",
    "room_price": "150.00"
  }
}
```

#### 3. `breakdown` (JSONField)
Desglose completo de costos calculados al momento del checkout:
```json
{
  "players_total": "200.00",           // Total por registro de jugadores
  "hotel_room_base": "750.00",         // Precio base de habitaciones
  "hotel_services_total": "30.00",      // Total de servicios adicionales
  "hotel_iva": "124.80",               // IVA del hotel
  "hotel_ish": "78.00",                // ISH del hotel
  "hotel_total": "982.80",             // Total del hotel (base + servicios + impuestos)
  "no_show_fee": "1000.00",            // Fee por no seleccionar hotel (si aplica)
  "subtotal": "2182.80",               // Subtotal antes de descuentos
  "discount_percent": 5,                // Porcentaje de descuento aplicado
  "discount_amount": "109.14",          // Monto del descuento (calculado)
  "total": "2073.66"                   // Total final después de descuentos
}
```

## Modelos Relacionados Creados Después del Pago

### 1. `EventAttendance` (apps.events.models)
Se crea un registro por cada jugador registrado:
- **`event`**: Evento
- **`user`**: Usuario del jugador
- **`status`**: "confirmed" (confirmado)
- **`notes`**: Incluye "Paid via Stripe session {session_id}"

### 2. `HotelReservation` (apps.locations.models)
Se crea una reserva por cada habitación en el carrito:
- **`hotel`**: Hotel de la reserva
- **`room`**: Habitación reservada
- **`user`**: Usuario que realizó el pago
- **`guest_name`**: Nombre del huésped
- **`guest_email`**: Email del huésped
- **`guest_phone`**: Teléfono del huésped
- **`number_of_guests`**: Número de huéspedes (incluye extra guests)
- **`check_in`**: Fecha de check-in
- **`check_out`**: Fecha de check-out
- **`status`**: "confirmed" (confirmada)
- **`notes`**: "Reserva pagada vía Stripe session {session_id}"
- **`total_amount`**: Monto total calculado de la reserva

### 3. `HotelReservationService` (apps.locations.models)
Se crea un registro por cada servicio adicional seleccionado:
- **`reservation`**: Reserva relacionada
- **`service`**: Servicio del hotel
- **`quantity`**: Cantidad del servicio

## Resumen de Información Guardada

### ✅ Información Completa Guardada:

1. **Datos del Usuario**: Usuario que pagó
2. **Datos del Evento**: Evento para el cual se pagó
3. **IDs de Stripe**: Session ID, Subscription ID, Schedule ID
4. **Modo de Pago**: Plan o pago único
5. **Descuentos**: Porcentaje y monto de descuento aplicado
6. **Jugadores Registrados**: Lista completa de IDs de jugadores
7. **Carrito de Hotel Completo**:
   - Habitaciones seleccionadas
   - Fechas de check-in/check-out
   - Número de huéspedes (incluidos y adicionales)
   - Precios de huéspedes adicionales
   - Servicios adicionales seleccionados
8. **Desglose de Costos**:
   - Total por jugadores
   - Desglose del hotel (base, servicios, IVA, ISH)
   - Fee de no-show (si aplica)
   - Subtotal y total
   - Descuentos aplicados
9. **Montos**: Total pagado, monto mensual (si es plan)
10. **Fechas**: Fecha de creación, fecha de pago
11. **Estado**: Estado actual del checkout

### 🔗 Relaciones Creadas:

- **EventAttendance**: Confirma la asistencia de cada jugador al evento
- **HotelReservation**: Crea las reservas de hotel confirmadas
- **HotelReservationService**: Vincula servicios adicionales a las reservas

## Ventajas de Este Sistema

1. **Snapshot Completo**: Toda la información se guarda al momento del checkout, incluso si los precios cambian después
2. **Auditoría**: Se puede rastrear exactamente qué se pagó y cuándo
3. **Recuperación**: Si hay problemas, se puede reconstruir la transacción completa
4. **Reportes**: Se puede generar cualquier reporte financiero con los datos guardados
5. **Huéspedes Adicionales**: Se guarda información detallada de huéspedes incluidos vs adicionales
6. **Desglose Completo**: Se guarda el breakdown completo de costos para transparencia

## Consultas Útiles

```python
# Obtener todos los checkouts de un usuario
checkouts = StripeEventCheckout.objects.filter(user=user)

# Obtener todos los checkouts pagados de un evento
paid_checkouts = StripeEventCheckout.objects.filter(
    event=event,
    status='paid'
)

# Obtener el breakdown de un checkout
breakdown = checkout.breakdown
players_total = Decimal(checkout.breakdown['players_total'])
hotel_total = Decimal(checkout.breakdown['hotel_total'])

# Obtener el carrito de hotel guardado
cart = checkout.hotel_cart_snapshot
for item_id, item_data in cart.items():
    room_id = item_data['room_id']
    guests = item_data['guests']
    extra_guests = item_data.get('extra_guests', 0)
```

## Notas Importantes

- Los datos se guardan **antes** de que el usuario complete el pago en Stripe (status="created")
- Una vez que el pago se completa, el status cambia a "paid" y se actualiza `paid_at`
- El `hotel_cart_snapshot` incluye información enriquecida de huéspedes adicionales que se calcula al momento del checkout
- El `breakdown` es calculado por el servidor y representa los costos exactos al momento del checkout
- Las reservas de hotel se crean automáticamente cuando el pago se confirma (status="paid")

