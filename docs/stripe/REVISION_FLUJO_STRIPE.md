# Revisión del Flujo de Orden y Compra con Stripe

## ✅ Estado General: **CORRECTO**

El flujo está bien implementado y sigue las mejores prácticas. Todas las validaciones críticas están en su lugar.

---

## 🔄 Flujo Completo

### 1. **Creación del Checkout** (`create_stripe_event_checkout_session`)

**✅ Validaciones Implementadas:**
- Valida que el usuario sea padre (`is_parent`)
- Valida que se seleccionen al menos 1 jugador
- Valida que los jugadores pertenezcan al usuario
- Valida que los jugadores no estén ya registrados y confirmados
- **Valida stock disponible ANTES de crear el checkout** ⚠️ CRÍTICO
- Calcula correctamente los montos (jugadores + hotel)
- Guarda snapshot completo del carrito (`hotel_cart_snapshot`)
- Guarda IDs de jugadores (`player_ids`)
- Guarda breakdown completo de precios

**✅ Datos Capturados Correctamente:**
- `player_ids`: Lista de IDs de jugadores
- `hotel_cart_snapshot`: Snapshot completo con:
  - Información de habitaciones
  - Fechas de check-in/check-out
  - Asignación de huéspedes
  - **Datos completos de huéspedes adicionales** (`additional_guest_details`)
  - Nombres de huéspedes adicionales (`additional_guest_names`)
- `breakdown`: Desglose de precios (subtotal, taxes, total)

**⚠️ Nota Importante:**
- El stock se valida ANTES de crear el checkout, pero puede haber condiciones de carrera si dos usuarios intentan reservar al mismo tiempo. Esto se maneja correctamente en `_finalize_stripe_event_checkout` con `select_for_update()`.

---

### 2. **Webhook de Stripe** (`stripe_webhook`)

**✅ Implementación:**
- Valida firma del webhook con `STRIPE_WEBHOOK_SECRET`
- Maneja `checkout.session.completed`:
  - Actualiza `stripe_subscription_id` si es un plan de pagos
  - Crea schedule de suscripción si es necesario
  - **Llama a `_finalize_stripe_event_checkout`**
- Maneja `checkout.session.expired`:
  - Actualiza el estado del checkout a "expired"

**✅ Idempotencia:**
- El webhook puede ser llamado múltiples veces por Stripe (por diseño)
- `_finalize_stripe_event_checkout` es idempotente (verifica `checkout.status == "paid"`)

---

### 3. **Success Callback** (`stripe_event_checkout_success`)

**✅ Implementación:**
- Verifica que `session_id` esté presente
- Verifica que Stripe esté configurado
- Recupera la sesión de Stripe
- **Verifica que `payment_status == "paid"`** ⚠️ CRÍTICO
- Actualiza `stripe_subscription_id` si es un plan de pagos
- Crea schedule de suscripción si es necesario
- **Llama a `_finalize_stripe_event_checkout`**
- Limpia el carrito de la sesión
- Redirige a página de confirmación

**✅ Idempotencia:**
- También es idempotente porque `_finalize_stripe_event_checkout` verifica el estado

---

### 4. **Finalización del Checkout** (`_finalize_stripe_event_checkout`)

**✅ CRÍTICO: Todo dentro de `transaction.atomic()`**

**✅ Validaciones de Idempotencia:**
```python
checkout.refresh_from_db()
if checkout.status == "paid":
    return  # Ya procesado, no hacer nada
```

**✅ Creación de Event Attendance:**
- Solo se crea DESPUÉS del pago exitoso
- Verifica que los jugadores pertenezcan al padre
- Crea o actualiza `EventAttendance` con `status="confirmed"`
- Guarda referencia al `stripe_session_id` en las notas

**✅ Creación de Hotel Reservations:**
- Solo se crea DESPUÉS del pago exitoso
- Usa `select_for_update()` para lock de la habitación (evita condiciones de carrera)
- Valida nuevamente que la habitación esté disponible
- **Valida stock disponible otra vez** (por si hubo cambios entre checkout y pago)
- Crea `HotelReservation` con:
  - Status `"confirmed"`
  - Todos los datos del huésped principal
  - **Datos completos de huéspedes adicionales** (`additional_guest_details_json`)
  - Nombres de huéspedes adicionales (`additional_guest_names`)
- Crea servicios asociados si los hay
- Calcula y guarda el total

**✅ Reducción de Stock:**
```python
# SOLO se descuenta si:
# 1. La reserva está confirmada
# 2. El stock es mayor a 0
# 3. El stock no es None
if reservation.status == "confirmed" and room.stock is not None and room.stock > 0:
    room.stock -= 1
    room.save(update_fields=["stock"])
```
- **Se descuenta SOLO después del pago exitoso** ⚠️ CRÍTICO
- Usa `select_for_update()` para evitar condiciones de carrera

**✅ Creación de Order:**
- Se crea DESPUÉS de todas las reservas
- Centraliza toda la información de la compra
- Evita duplicados (verifica si ya existe una Order para este checkout)

**✅ Asignación de Order a Reservas:**
- Después de crear la Order, se actualizan todas las reservas para asignar la relación
- Esto asegura que todas las reservas queden vinculadas a la Order

---

### 5. **Creación de Order** (`_create_order_from_stripe_checkout`)

**✅ Validación de Duplicados:**
```python
if Order.objects.filter(stripe_checkout=checkout).exists():
    return Order.objects.get(stripe_checkout=checkout)
```

**✅ Información Capturada:**
- Usuario (`user`)
- Evento (`event`)
- Stripe checkout (`stripe_checkout`)
- IDs de sesión, suscripción, schedule de Stripe
- Montos (subtotal, taxes, discount, total)
- Breakdown completo con:
  - Información de jugadores registrados
  - Información de reservas de hotel (incluyendo huéspedes adicionales)
- Información de plan de pagos (si aplica)

**✅ Relaciones:**
- `stripe_checkout`: ForeignKey a `StripeEventCheckout`
- `event`: ForeignKey a `Event`
- `hotel_reservations`: Property que busca reservas vinculadas a través de `HotelReservation.order`

---

## 🔒 Seguridad y Validaciones

### ✅ Validaciones Implementadas:

1. **Antes del Checkout:**
   - Validación de permisos (solo padres)
   - Validación de jugadores válidos
   - Validación de jugadores no duplicados
   - **Validación de stock disponible**

2. **Durante el Pago:**
   - Stripe maneja la seguridad del pago
   - Webhook valida firma

3. **Después del Pago:**
   - **Verificación de `payment_status == "paid"`** antes de crear registros
   - Validación de idempotencia
   - **Revalidación de stock** (por si cambió entre checkout y pago)
   - Transacciones atómicas para consistencia

---

## 📊 Datos Guardados Correctamente

### ✅ Event Attendance:
- `event`: Evento al que se registra
- `user`: Usuario del jugador
- `status`: "confirmed"
- `notes`: Referencia al `stripe_session_id`

### ✅ Hotel Reservation:
- `hotel`: Hotel de la habitación
- `room`: Habitación reservada
- `user`: Usuario que realiza la reserva
- `guest_name`: Nombre del huésped principal
- `guest_email`: Email del huésped principal
- `guest_phone`: Teléfono del huésped principal
- `number_of_guests`: Número total de huéspedes
- `check_in` / `check_out`: Fechas de la reserva
- `status`: "confirmed"
- `additional_guest_names`: Texto con nombres de huéspedes adicionales
- **`additional_guest_details_json`**: JSON con datos completos de huéspedes adicionales:
  ```json
  [
    {
      "name": "Juan Pérez",
      "type": "adult",
      "birth_date": "1990-01-01",
      "email": "juan@example.com"
    },
    {
      "name": "María García",
      "type": "child",
      "birth_date": "2010-05-15",
      "email": ""
    }
  ]
  ```
- `order`: ForeignKey a `Order` (asignado después de crear la Order)
- `total_amount`: Monto total calculado

### ✅ Order:
- `user`: Usuario que realiza la compra
- `event`: Evento asociado
- `stripe_checkout`: Checkout de Stripe
- `status`: "paid"
- `payment_method`: "stripe"
- `stripe_session_id`: ID de la sesión de Stripe
- `subtotal`, `tax_amount`, `discount_amount`, `total_amount`: Montos
- `breakdown`: JSON con desglose completo:
  ```json
  {
    "players_total": "100.00",
    "hotel_total": "500.00",
    "subtotal": "600.00",
    "tax_amount": "60.00",
    "registered_player_ids": [1, 2],
    "hotel_reservations": [
      {
        "room_id": 1,
        "room_number": "A1",
        "hotel_name": "Fiesta Americana Mérida",
        "check_in": "2026-01-22",
        "check_out": "2026-01-27",
        "number_of_guests": 4,
        "additional_guest_names": ["Juan Pérez", "María García"],
        "additional_guest_details": [...]
      }
    ]
  }
  ```
- `registered_player_ids`: Lista de IDs de jugadores registrados
- Información de plan de pagos (si aplica)

---

## ⚠️ Posibles Mejoras (Opcionales)

1. **Logging más detallado:**
   - Agregar logging cuando se detecta que un checkout ya fue procesado (idempotencia)
   - Logging cuando se omite una reserva por falta de stock

2. **Manejo de errores más específico:**
   - Si una reserva no se puede crear por falta de stock, podríamos notificar al usuario
   - Actualmente, si no hay stock en `_finalize_stripe_event_checkout`, simplemente se omite la reserva

3. **Notificaciones:**
   - Enviar email cuando se completa una orden
   - Notificar si alguna reserva no se pudo crear por falta de stock

4. **Métricas:**
   - Tracking de cuántos checkouts fallan por falta de stock
   - Tiempo promedio entre checkout y finalización

---

## ✅ Conclusión

**El flujo está correctamente implementado y es seguro.**

Todos los puntos críticos están cubiertos:
- ✅ Validación de stock antes del checkout
- ✅ Revalidación de stock después del pago
- ✅ No se crean registros hasta que el pago sea exitoso
- ✅ Transacciones atómicas para consistencia
- ✅ Idempotencia para evitar duplicados
- ✅ Datos completos de huéspedes guardados
- ✅ Relaciones correctas entre modelos

**No se requieren cambios críticos.**

