# Flujo Completo de Creación de Órdenes

## Resumen del Flujo

Este documento describe el flujo completo desde que un usuario se registra a un evento, selecciona habitaciones y huéspedes, hasta que se completa el pago y se crean todos los registros necesarios.

**⚠️ IMPORTANTE:**
- **NO se crean reservas, NO se descuentan stock, y NO se registran eventos hasta que el pago sea válido.**
- Todo se crea SOLO después de que Stripe confirme el pago exitoso en `_finalize_stripe_event_checkout`.

---

## 1. Selección de Jugadores y Habitaciones (Frontend)

### 1.1 Registro de Jugadores al Evento

**Ubicación:** `templates/accounts/panel_tabs/detalle_evento.html`

El usuario selecciona uno o más jugadores (hijos) que desea registrar al evento. Los jugadores deben:
- Estar asociados al usuario padre (`PlayerParent`)
- Estar activos (`is_active=True`)
- No estar ya registrados en el evento

**Datos capturados:**
- IDs de los jugadores seleccionados (`player_ids`)

### 1.2 Selección de Habitaciones

**Ubicación:** `static/js/vue/event-detail.js` (Vue Component)

El usuario puede:
- Ver habitaciones disponibles del hotel del evento
- Seleccionar una o más habitaciones
- Especificar fechas de check-in y check-out

**Datos capturados:**
- `room_id`: ID de la habitación
- `check_in_date`: Fecha de check-in
- `check_out_date`: Fecha de check-out
- `check_in_time`: Hora de check-in (opcional)
- `check_out_time`: Hora de check-out (opcional)

### 1.3 Asignación de Huéspedes a Habitaciones

**Ubicación:** `static/js/vue/event-detail.js` (Guest Assignment Modal)

El usuario debe:
- Asignar jugadores seleccionados a habitaciones
- Agregar huéspedes adicionales (adultos o niños)
- Para cada huésped adicional, se capturan:
  - **Nombre completo** (`first_name`, `last_name`)
  - **Tipo**: `adult` o `child`
  - **Fecha de nacimiento** (`birth_date`) - **REQUERIDO para niños**
  - **Email** (opcional)

**Estado en Vue:**
```javascript
reservation.state = {
  rooms: [...], // Habitaciones seleccionadas
  guests: [...], // Lista completa de huéspedes (jugadores + adicionales)
  guestAssignments: {
    "room_id_1": [0, 1, 2], // Índices de huéspedes en `guests`
    "room_id_2": [3, 4]
  },
  manualGuests: [...] // Huéspedes adicionales agregados manualmente
}
```

---

## 2. Inicio del Checkout (Creación de Sesión Stripe)

### 2.1 Endpoint: `create_stripe_event_checkout_session`

**Ubicación:** `apps/accounts/views_private.py:1858`

**Método:** `POST /accounts/events/<pk>/stripe/create-checkout-session/`

**Datos recibidos:**

1. **Jugadores:**
   - `players[]`: Lista de IDs de jugadores

2. **Modo de pago:**
   - `payment_mode`: `"plan"` o `"now"`

3. **Hotel (Vue Payload):**
   - `hotel_reservation_json`: JSON con:
     ```json
     {
       "hotel_pk": 1,
       "check_in_date": "2026-01-22",
       "check_out_date": "2026-01-27",
       "rooms": [
         {
           "roomId": "1",
           "price": "100.00",
           ...
         }
       ],
       "guest_assignments": {
         "1": [0, 1, 2]  // Índices de huéspedes
       },
       "guests": [
         {
           "id": "player-26",
           "name": "Jugador 1",
           "type": "child",
           "birth_date": "2012-01-01"
         },
         {
           "id": "manual-1",
           "first_name": "María",
           "last_name": "García",
           "type": "adult",
           "birth_date": "1990-02-20"
         }
       ]
     }
     ```

**Procesamiento:**

1. **Validación de jugadores:**
   - Verifica que los jugadores pertenezcan al usuario
   - Verifica que no estén ya registrados

2. **Cálculo de montos:**
   - `players_total`: `entry_fee * cantidad_jugadores`
   - `hotel_total`: Calculado desde `_compute_hotel_amount_from_vue_payload()`
   - `no_show_fee`: Si hay jugadores y NO hay hotel
   - Descuento 5% si `payment_mode="now"` y hay hotel

3. **Construcción del snapshot de hotel:**
   ```python
   vue_cart_snapshot[f"vue-room-{room_id}"] = {
       "type": "room",
       "room_id": int(room_id),
       "check_in": check_in,
       "check_out": check_out,
       "guests": max(1, guests_count),
       "services": [],
       "additional_guest_names": [
           "María García López",
           "Pedro Hernández Martínez",
           ...
       ],
       "notes": "Additional guests: María García López, Pedro Hernández Martínez"
   }
   ```

   **⚠️ PROBLEMA IDENTIFICADO:**
   - Solo se está capturando el **nombre** del huésped adicional
   - **NO se está guardando** `birth_date` ni `type` (adult/child) en el snapshot
   - Esto ocurre porque `guest_assignments` solo contiene índices, y al construir `additional_guest_names`, solo se extrae el nombre

4. **Creación de `StripeEventCheckout`:**
   ```python
   StripeEventCheckout.objects.create(
       user=user,
       event=event,
       stripe_session_id=session_id,
       player_ids=[26, 27],
       hotel_cart_snapshot=vue_cart_snapshot,
       breakdown={...},
       amount_total=total,
       status="created",
       ...
   )
   ```

5. **Respuesta:**
   ```json
   {
     "success": true,
     "checkout_url": "https://checkout.stripe.com/..."
   }
   ```

---

## 3. Pago en Stripe

El usuario es redirigido a Stripe Checkout y completa el pago.

---

## 5. Confirmación de Pago (Webhook o Success Callback)

### 4.1 Webhook de Stripe

**Ubicación:** `apps/accounts/views_private.py:2715`

**Endpoint:** `POST /accounts/stripe/webhook/`

**Evento:** `checkout.session.completed`

Cuando Stripe confirma el pago:
1. Busca el `StripeEventCheckout` por `stripe_session_id`
2. Actualiza `stripe_subscription_id` y `stripe_subscription_schedule_id` si aplica
3. Llama a `_finalize_stripe_event_checkout(checkout)`

### 4.2 Success Callback

**Ubicación:** `apps/accounts/views_private.py:2628`

**Endpoint:** `GET /accounts/events/<pk>/stripe/checkout/success/`

Similar al webhook, verifica el pago y llama a `_finalize_stripe_event_checkout(checkout)`.

---

## 6. Finalización del Checkout

**⚠️ IMPORTANTE: Este es el ÚNICO lugar donde se crean reservas, registros y se descuenta stock.**

### 5.1 Función: `_finalize_stripe_event_checkout`

**Ubicación:** `apps/accounts/views_private.py:2421`

**Proceso (SOLO se ejecuta después de pago exitoso de Stripe):**

1. **Verificar que el checkout NO esté ya procesado:**
   ```python
   checkout.refresh_from_db()
   if checkout.status == "paid":
       return  # Ya procesado, evitar duplicados
   ```

2. **Crear registros de evento (`EventAttendance`):**
   - ✅ **REGISTRO AL EVENTO:** Se crean los registros de los jugadores al evento
   - ✅ Se crean SOLO después del pago exitoso
   - ✅ Status: `"confirmed"`
   - ✅ Se agrega nota con `stripe_session_id`
   - ✅ Un `EventAttendance` por cada jugador en `checkout.player_ids`

   ```python
   for pp in player_parents:
       player_user = pp.player.user
       attendance, _ = EventAttendance.objects.get_or_create(
           event=event,
           user=player_user,
           defaults={"status": "confirmed"}
       )
       attendance.status = "confirmed"
       attendance.notes = f"\nPaid via Stripe session {checkout.stripe_session_id}"
       attendance.save()
   ```

3. **Crear reservas de hotel (`HotelReservation`):**

   **Validaciones antes de crear:**
   - ✅ Verifica que la habitación esté disponible (`is_available=True`)
   - ✅ **Valida stock disponible**:
     - Cuenta reservas activas (`pending`, `confirmed`, `checked_in`) en las fechas seleccionadas
     - Compara con el `stock` total de la habitación
     - Si `reservas_activas >= stock`, omite la creación de la reserva
   - ✅ Usa `select_for_update()` para evitar condiciones de carrera

   ```python
   for room_key, item_data in checkout.hotel_cart_snapshot.items():
       room = HotelRoom.objects.select_for_update().get(id=item_data["room_id"])

       # Validar stock disponible
       if room.stock is not None and room.stock > 0:
           active_reservations_count = room.reservations.filter(
               check_in__lt=check_out,
               check_out__gt=check_in,
               status__in=["pending", "confirmed", "checked_in"],
           ).count()

           if active_reservations_count >= room.stock:
               continue  # No hay disponibilidad

       # Extraer información completa de huéspedes adicionales
       additional_guest_details = item_data.get("additional_guest_details", [])

       HotelReservation.objects.create(
           hotel=room.hotel,
           room=room,
           user=checkout.user,
           guest_name=checkout.user.get_full_name(),
           guest_email=checkout.user.email,
           guest_phone=user.profile.phone,
           number_of_guests=item_data["guests"],
           check_in=check_in,
           check_out=check_out,
           status="confirmed",
           notes=f"Reserva pagada vía Stripe session {checkout.stripe_session_id}",
           additional_guest_names="\n".join([g["name"] for g in additional_guest_details]),
           additional_guest_details_json=additional_guest_details,  # Datos completos en JSON
           order=order  # Asignación directa a la orden
       )

       # Descontar stock de la habitación
       if room.stock is not None and room.stock > 0:
           room.stock -= 1
           room.save(update_fields=["stock"])
   ```

   **✅ IMPLEMENTADO:**
   - ✅ Se guardan datos completos en `additional_guest_details_json` (nombre, tipo, fecha de nacimiento, email)
   - ✅ Se guardan nombres en `additional_guest_names` para compatibilidad
   - ✅ **Stock se descuenta automáticamente** al crear la reserva
   - ✅ **Validación de stock** antes de crear la reserva
   - ✅ **Relación directa** con `Order` a través de ForeignKey

4. **Descontar stock de habitaciones:**
   - ✅ Se descuenta SOLO cuando la reserva está confirmada (`status="confirmed"`)
   - ✅ Solo si `stock > 0` y `stock is not None`
   - ✅ Usa `select_for_update()` para evitar condiciones de carrera

5. **Actualizar estado del checkout:**
   ```python
   checkout.status = "paid"
   checkout.paid_at = timezone.now()
   checkout.save()
   ```

6. **Crear Order:**
   ```python
   order = _create_order_from_stripe_checkout(checkout)
   ```
   - ✅ El `Order` incluye `registered_player_ids` (IDs de los jugadores registrados)
   - ✅ El `Order` incluye toda la información del evento y reservas en `breakdown`

7. **Asignar relación Order → HotelReservation:**
   ```python
   for reservation in reservations_to_update:
       reservation.order = order
       reservation.save(update_fields=["order"])
   ```

**Resumen de lo que se crea en este paso:**
1. ✅ **EventAttendance** (registro al evento) - uno por cada jugador
2. ✅ **HotelReservation** (reserva de habitación) - una por cada habitación reservada
3. ✅ **HotelReservationService** (servicios adicionales) - si hay servicios seleccionados
4. ✅ **Stock** de habitaciones descontado
5. ✅ **Order** (orden centralizada con toda la información)
6. ✅ Relación **Order → HotelReservation** (ForeignKey)

---

## 6. Creación de la Orden

### 6.1 Función: `_create_order_from_stripe_checkout`

**Ubicación:** `apps/accounts/views_private.py:2271`

**Proceso:**

1. **Verificar si ya existe:**
   - Evita duplicados

2. **Extraer información de reservas de hotel:**
   ```python
   for room_key, item_data in checkout.hotel_cart_snapshot.items():
       reservation_info = {
           "room_id": item_data.get("room_id"),
           "room_number": item_data.get("room_number", ""),
           "hotel_name": hotel_name,
           "check_in": item_data.get("check_in"),
           "check_out": item_data.get("check_out"),
           "number_of_guests": item_data.get("guests"),
           "guest_name": checkout.user.get_full_name(),
           "guest_email": checkout.user.email,
           "guest_phone": "",
           "additional_guest_names": [
               "María García López",
               "Pedro Hernández Martínez"
           ]  # Solo nombres
       }
   ```

3. **Crear `Order`:**
   ```python
   Order.objects.create(
       user=checkout.user,
       stripe_checkout=checkout,
       event=checkout.event,
       status="paid",
       payment_method="stripe",
       registered_player_ids=checkout.player_ids,
       breakdown={
           "hotel_reservations": [reservation_info, ...],
           ...
       },
       ...
   )
   ```

---

## 7. Modelos Finales y Datos Almacenados

### 7.1 `EventAttendance`

✅ **Datos completos:**
- `event`: Evento
- `user`: Usuario del jugador
- `status`: "confirmed"
- `notes`: Incluye `stripe_session_id`

### 7.2 `HotelReservation`

⚠️ **Datos incompletos:**
- `hotel`: ✅ Hotel
- `room`: ✅ Habitación
- `user`: ✅ Usuario que pagó
- `guest_name`: ✅ Nombre del huésped principal
- `guest_email`: ✅ Email del huésped principal
- `guest_phone`: ✅ Teléfono del huésped principal
- `number_of_guests`: ✅ Total de huéspedes
- `check_in`, `check_out`: ✅ Fechas
- `additional_guest_names`: ⚠️ **Solo nombres** (TextField)
  - Ejemplo: `"María García López\nPedro Hernández Martínez"`
  - **NO incluye:** `birth_date`, `type` (adult/child), `email`

### 7.3 `Order`

✅ **Datos completos:**
- `user`: ✅ Usuario
- `event`: ✅ Evento
- `stripe_checkout`: ✅ Checkout de Stripe
- `registered_player_ids`: ✅ IDs de jugadores
- `breakdown.hotel_reservations`: ⚠️ **Solo nombres** de huéspedes adicionales
- `status`: ✅ "paid"
- Montos: ✅ Completos

---

## 8. Problemas Identificados

### ❌ Problema 1: Faltan Datos de Huéspedes Adicionales

**Problema:**
- Los huéspedes adicionales solo guardan el **nombre**
- **NO se guardan:**
  - Fecha de nacimiento (`birth_date`)
  - Tipo (adulto/niño)
  - Email

**Causa:**
- En `create_stripe_event_checkout_session`, al construir `additional_guest_names`, solo se extrae el nombre del objeto guest
- El campo `additional_guest_names` en `HotelReservation` es un `TextField`, no un `JSONField`

**Ubicación del problema:**
- `apps/accounts/views_private.py:1975-2003`

### ❌ Problema 2: Datos Perdidos en el Snapshot

**Problema:**
- `guest_assignments` solo contiene índices, no objetos completos
- Los datos completos están en `guests`, pero no se están enviando al backend

**Ubicación del problema:**
- `static/js/vue/event-detail.js:3473`

---

## 9. Recomendaciones de Mejora

### ✅ Mejora 1: Almacenar Datos Completos de Huéspedes

**Cambio necesario:**

1. **Modificar `HotelReservation` para almacenar JSON:**
   ```python
   additional_guest_details = models.JSONField(
       default=list,
       blank=True,
       verbose_name="Detalles de Huéspedes Adicionales",
       help_text="Lista de huéspedes adicionales con nombre, tipo y fecha de nacimiento"
   )
   ```

2. **Actualizar `create_stripe_event_checkout_session` para capturar datos completos:**
   ```python
   # En lugar de solo nombres, guardar objetos completos
   additional_guests = []
   for idx, guest_index in enumerate(assigned):
       if idx > 0:  # Skip principal
           guest_obj = hotel_payload.get("guests", [])[guest_index]
           additional_guests.append({
               "name": guest_obj.get("name") or f"{guest_obj.get('first_name')} {guest_obj.get('last_name')}",
               "type": guest_obj.get("type", "adult"),
               "birth_date": guest_obj.get("birth_date", ""),
               "email": guest_obj.get("email", "")
           })

   vue_cart_snapshot[f"vue-room-{room_id}"]["additional_guest_details"] = additional_guests
   ```

3. **Actualizar `_finalize_stripe_event_checkout` para guardar JSON:**
   ```python
   reservation = HotelReservation.objects.create(
       ...
       additional_guest_details=item_data.get("additional_guest_details", []),
       additional_guest_names="\n".join([g["name"] for g in item_data.get("additional_guest_details", [])])  # Para compatibilidad
   )
   ```

### ✅ Mejora 2: Enviar Datos Completos desde Vue

**Cambio necesario:**

En `static/js/vue/event-detail.js`, asegurar que `guests` se envíe en el payload:

```javascript
const hotelData = {
    ...
    guests: reservation.state.guests,  // Lista completa de huéspedes
    guest_assignments: reservation.state.guestAssignments
};
```

---

## 10. Verificación del Flujo Actual

### ✅ Funciona Correctamente:
- ✅ Registro de jugadores al evento
- ✅ Creación de reservas de hotel
- ✅ Cálculo de montos
- ✅ Creación de Order
- ✅ Links entre Order, HotelReservation y EventAttendance

### ⚠️ Funciona Parcialmente:
- ⚠️ Datos de huéspedes adicionales (solo nombres)

### ❌ No Funciona:
- ❌ Almacenamiento de `birth_date` de huéspedes adicionales
- ❌ Almacenamiento de `type` (adult/child) de huéspedes adicionales
- ❌ Almacenamiento de `email` de huéspedes adicionales

---

## 11. Cambios Implementados

### ✅ Mejora 1: Captura de Datos Completos de Huéspedes

**Cambios realizados en `apps/accounts/views_private.py`:**

1. **Actualizado `create_stripe_event_checkout_session` (líneas ~1963-2003):**
   - Ahora accede a `all_guests` del payload Vue
   - Construye `additional_guest_details` con datos completos (nombre, tipo, birth_date, email)
   - Guarda tanto `additional_guest_names` (para compatibilidad) como `additional_guest_details` (datos completos)

2. **Actualizado `_finalize_stripe_event_checkout` (líneas ~2484-2560):**
   - Prioriza `additional_guest_details` si está disponible
   - Guarda nombres con fechas de nacimiento en formato "Nombre (YYYY-MM-DD)"
   - Guarda JSON completo en las notas para uso futuro

3. **Actualizado `_create_order_from_stripe_checkout` (líneas ~2341-2382):**
   - Incluye `additional_guest_details` en el breakdown de la Order

### ✅ Mejora Implementada: Campo JSON en HotelReservation

**Implementado:**

✅ Agregado campo `additional_guest_details_json` al modelo `HotelReservation`:
```python
additional_guest_details_json = models.JSONField(
    default=list,
    blank=True,
    verbose_name="Detalles Completos de Huéspedes Adicionales",
    help_text="Lista de huéspedes adicionales con nombre, tipo, fecha de nacimiento y email"
)
```

✅ Creada migración: `apps/locations/migrations/0026_add_additional_guest_details_json.py`

✅ Actualizado `_finalize_stripe_event_checkout` para guardar datos en el campo JSON

✅ Actualizado `additional_guest_details` property para priorizar el campo JSON sobre el parsing de texto

✅ Actualizado `HotelReservationAdmin` para mostrar el campo `additional_guest_details_json` en el admin de Django

✅ Migración aplicada exitosamente

## 12. Estado de Implementación

1. ✅ **Implementada captura de datos completos** desde Vue payload
2. ✅ **Implementado:** Campo `additional_guest_details_json` en `HotelReservation`
3. ✅ **Implementado:** Migración creada y aplicada
4. ✅ **Implementado:** `_finalize_stripe_event_checkout` guarda datos en el campo JSON
5. ✅ **Implementado:** `additional_guest_details` property prioriza el campo JSON
6. ✅ **Implementado:** Validación de stock antes de crear checkout
7. ✅ **Implementado:** Validación de stock antes de crear reserva
8. ✅ **Implementado:** Descuento automático de stock al crear reserva
9. ✅ **Implementado:** Relación directa `Order` → `HotelReservation` (ForeignKey)
10. ✅ **Implementado:** Asignación automática de `order` a reservas al finalizar checkout

## 13. Validación y Gestión de Stock de Habitaciones ✅

### 13.1 Validación Pre-Checkout

**Ubicación:** `apps/accounts/views_private.py:1955-2010` (en `create_stripe_event_checkout_session`)

**Proceso:**
1. **Antes de crear el checkout**, se valida la disponibilidad de stock:
   - Para cada habitación seleccionada en el payload
   - Cuenta reservas activas (`pending`, `confirmed`, `checked_in`) en las fechas seleccionadas
   - Compara con el `stock` total de la habitación
   - Si `reservas_activas >= stock`, retorna error 400 y no permite crear el checkout
   - Si `stock` es `None` o `0`, no se valida límite (stock ilimitado)

**Ventaja:** Evita que se cree un checkout si no hay habitaciones disponibles, previniendo pagos que no se pueden cumplir.

### 13.2 Validación y Descuento Post-Pago

**Ubicación:** `apps/accounts/views_private.py:2528-2568` (en `_finalize_stripe_event_checkout`)

**Proceso:**
1. **Antes de crear la reserva:**
   - Usa `select_for_update()` para lock de la habitación (evita condiciones de carrera)
   - Verifica que `room.is_available = True`
   - Cuenta reservas activas en las fechas seleccionadas
   - Compara con `stock` total
   - Si no hay disponibilidad, omite la creación de la reserva

2. **Creación de la reserva:**
   - Se crea la reserva con `status="confirmed"` (porque el pago ya fue exitoso)

3. **Después de crear la reserva exitosamente (SOLO si status="confirmed"):**
   - **IMPORTANTE:** El stock SOLO se descuenta cuando:
     - El pago de Stripe fue exitoso
     - La reserva tiene `status="confirmed"`
     - La función `_finalize_stripe_event_checkout` se ejecuta dentro de una transacción atómica
   - Descuenta el stock: `room.stock -= 1`
   - Solo descuenta si `stock > 0` y `stock is not None`
   - Guarda el cambio en la base de datos

**NOTA:** Las reservas creadas desde otros lugares (como `cart_views.py` o `views_front.py`) se crean con `status="pending"` y NO descuentan stock hasta que el pago sea exitoso.

**Ventaja:** Garantiza que el stock se actualiza correctamente y evita sobre-reservaciones.

### 13.3 Consideraciones

- **Stock ilimitado:** Si `stock` es `None` o `0`, no se aplica límite de disponibilidad
- **Condiciones de carrera:** Se usa `select_for_update()` dentro de una transacción para evitar que múltiples usuarios reserven la misma habitación simultáneamente
- **Reversión de stock:** Actualmente, el stock no se incrementa automáticamente cuando:
  - Se cancela una reserva
  - Se completa el check-out
  - Se rechaza un pago

  **Recomendación futura:** Implementar signals o métodos para incrementar stock cuando sea apropiado.

## 14. Implementación Completada ✅

### Campos y Funcionalidades Implementadas:

1. ✅ **Campo JSON agregado** al modelo `HotelReservation`
2. ✅ **Migración creada y aplicada** (`0026_add_additional_guest_details_json`)
3. ✅ **Captura de datos completos** desde el payload Vue
4. ✅ **Almacenamiento en JSON** durante la creación de reservas
5. ✅ **Property actualizada** para priorizar JSON sobre parsing de texto
6. ✅ **Admin actualizado** para mostrar el campo en Django Admin
7. ✅ **Order breakdown** incluye `additional_guest_details` completos

### Estructura de Datos Almacenados:

```json
{
  "additional_guest_details_json": [
    {
      "name": "María García López",
      "type": "adult",
      "birth_date": "1990-02-20",
      "email": "maria@example.com"
    },
    {
      "name": "Pedro Hernández Martínez",
      "type": "adult",
      "birth_date": "1988-05-15",
      "email": ""
    },
    {
      "name": "Ana Rodríguez Sánchez",
      "type": "child",
      "birth_date": "2013-02-02",
      "email": ""
    }
  ]
}
```

## 14. Próximos Pasos (Opcionales)

1. ⏳ **Probar flujo completo** con datos reales incluyendo fecha de nacimiento y tipo de huésped
2. ⏳ **Verificar** que los templates muestren correctamente todos los datos desde `additional_guest_details_json`
3. ⏳ **Opcional:** Crear script de migración para convertir datos antiguos desde `additional_guest_names` (texto) a `additional_guest_details_json` (JSON)
4. ⏳ **Opcional:** Agregar validación en el formulario Vue para requerir fecha de nacimiento en niños

