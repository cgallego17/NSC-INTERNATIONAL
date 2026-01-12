# Flujo de Compra (Checkout) - Documentación

## Resumen del Flujo

El flujo de compra en el sistema maneja el registro de jugadores para eventos, reservas de hotel, y pagos a través de Stripe. Incluye soporte para pagos únicos, planes de pago, y uso de wallet (billetera digital).

---

## 1. Inicio del Checkout

### Ubicación: `templates/accounts/panel_tabs/detalle_evento_vue.html`
- El usuario selecciona jugadores, habitaciones de hotel, y opciones de pago
- El frontend (Vue.js) calcula los totales y muestra un resumen
- El usuario hace clic en "Pay Now" o "Register now, pay later"

### Endpoint: `create_stripe_event_checkout_session` (POST)
**Archivo:** `apps/accounts/views_private.py:1976`

**Validaciones iniciales:**
1. Verifica que el usuario sea padre o espectador
2. Valida que se hayan seleccionado jugadores (si no es espectador)
3. Verifica que los jugadores no estén ya registrados y pagados
4. Valida disponibilidad de stock de habitaciones (si aplica)

**Cálculos:**
- `players_total`: Total por jugadores seleccionados
- `hotel_total`: Total por habitaciones y servicios
- `hotel_buy_out_fee`: Fee si hay hotel pero no se reservó habitación
- `subtotal`: Suma de players + hotel + buy_out_fee
- `service_fee`: Porcentaje del subtotal
- `total_before_discount`: subtotal + service_fee
- `total`: Aplicando descuento (si hay)
- `total_after_wallet`: total - wallet_deduction

---

## 2. Reserva de Fondos del Wallet

**Si el usuario selecciona usar wallet:**
```python
wallet.reserve_funds(
    amount=wallet_deduction,
    description=f"Reserva para checkout: {event.title}",
    reference_id=f"event_checkout_pending:{event.pk}",
)
```

**Efecto:**
- Los fondos se **reservan** (no se descuentan aún)
- `wallet.pending_balance` aumenta
- `wallet.available_balance` disminuye
- Se crea una transacción de tipo "reservation"

**Si falla:**
- Se retorna error y el checkout no se crea

---

## 3. Creación del StripeEventCheckout

**Se crea un registro `StripeEventCheckout` con:**
- `status = "created"` (o `"registered"` si es register_only)
- `stripe_session_id`: ID de la sesión de Stripe (o placeholder)
- `player_ids`: Lista de IDs de jugadores
- `hotel_cart_snapshot`: Snapshot del carrito de hotel (JSON)
- `breakdown`: Desglose completo de precios (JSON)
- `amount_total`: Total a pagar después del wallet
- `payment_mode`: "plan", "now", o "register_only"

**Se crea también una `Order` pendiente:**
- `status = "pending"` o `"pending_registration"`
- Vinculada al `StripeEventCheckout`

---

## 4. Creación de Sesión de Stripe

**Se crea una sesión de checkout en Stripe:**
```python
session = stripe.checkout.Session.create(**session_params)
```

**Parámetros importantes:**
- `line_items`: Items ajustados para reflejar el descuento del wallet
- `mode`: "payment" (pago único) o "subscription" (plan)
- `success_url`: Redirige a `stripe_event_checkout_success`
- `cancel_url`: Redirige a `stripe_event_checkout_cancel`

**Ajuste de line_items:**
- Si se usó wallet, los `line_items` se ajustan para que el total coincida con `total_after_wallet`
- Se itera desde el último item hacia atrás para ajustar montos
- Evita valores negativos en `unit_amount`

**Se actualiza el `StripeEventCheckout`:**
- `stripe_session_id = session.id`
- `status = "created"`

---

## 5. Redirección a Stripe

El usuario es redirigido a la página de checkout de Stripe donde:
- Completa el pago con tarjeta
- O cancela y regresa

---

## 6. Casos de Éxito

### 6.1. Pago Exitoso - Redirect desde Stripe

**Endpoint:** `stripe_event_checkout_success` (GET)
**Archivo:** `apps/accounts/views_private.py:3677`

**Proceso:**
1. Verifica el `session_id` desde Stripe
2. Recupera la sesión de Stripe para verificar `payment_status == "paid"`
3. Busca el `StripeEventCheckout` por `stripe_session_id`
4. Si es plan de pago, guarda `subscription_id` y crea schedule
5. **Confirma fondos reservados del wallet:**
   ```python
   wallet.confirm_reserved_funds(
       amount=wallet_deduction,
       description=f"Pago confirmado para: {checkout.event.title}",
       reference_id=f"checkout_confirmed:{checkout.pk}",
   )
   ```
6. Llama a `_finalize_stripe_event_checkout(checkout)`
7. Redirige a página de confirmación

### 6.2. Pago Exitoso - Webhook de Stripe

**Endpoint:** `stripe_webhook` (POST)
**Archivo:** `apps/accounts/views_private.py:3900`

**Evento:** `checkout.session.completed`

**Proceso:**
1. Verifica la firma del webhook
2. Busca el `StripeEventCheckout` por `session_id`
3. Guarda `subscription_id` y crea schedule (si es plan)
4. **Confirma fondos reservados del wallet** (igual que en success)
5. Llama a `_finalize_stripe_event_checkout(checkout)`

**Nota:** El webhook es el método más confiable, ya que Stripe lo llama automáticamente cuando el pago se completa.

---

## 7. Finalización del Checkout

**Función:** `_finalize_stripe_event_checkout`
**Archivo:** `apps/accounts/views_private.py:3314`

**Proceso (idempotente):**

1. **Verifica si ya está procesado:**
   - Si `checkout.status == "paid"` y ya existe `Order`, retorna (idempotencia)

2. **Confirma asistencia al evento:**
   - Crea/actualiza `EventAttendance` para cada jugador
   - `status = "confirmed"`

3. **Crea reservas de hotel:**
   - Itera sobre `hotel_cart_snapshot`
   - Valida disponibilidad de stock
   - Crea `HotelReservation` con `status = "pending"`
   - Crea `HotelReservationService` para servicios adicionales
   - Usa `select_for_update()` para evitar condiciones de carrera

4. **Crea/actualiza la Order:**
   - Llama a `_create_order_from_stripe_checkout(checkout)`
   - `status = "paid"`
   - `paid_at = timezone.now()`
   - Vincula las reservas de hotel

5. **Marca el checkout como pagado:**
   ```python
   checkout.status = "paid"
   checkout.paid_at = timezone.now()
   checkout.save()
   ```

---

## 8. Casos de Cancelación/Error

### 8.1. Usuario Cancela en Stripe

**Endpoint:** `stripe_event_checkout_cancel` (GET)
**Archivo:** `apps/accounts/views_private.py:3780`

**Proceso:**
1. Busca el checkout más reciente del usuario para el evento
   - Primero busca en estado "created"
   - Si no encuentra, busca en últimos 24 horas
2. **Libera fondos reservados del wallet:**
   ```python
   wallet.release_reserved_funds(
       amount=wallet_deduction,
       description=f"Liberación de reserva por cancelación: {event.title}",
       reference_id=f"checkout_cancel:{checkout.pk}",
   )
   ```
3. Muestra mensaje al usuario
4. Redirige de vuelta al detalle del evento

### 8.2. Sesión de Stripe Expira

**Endpoint:** `stripe_webhook` (POST)
**Evento:** `checkout.session.expired`

**Proceso:**
1. Busca el checkout por `session_id` con `status = "created"`
2. **Libera fondos reservados del wallet:**
   ```python
   wallet.release_reserved_funds(
       amount=wallet_deduction,
       description=f"Reserva liberada por expiración: {checkout.event.title}",
       reference_id=f"checkout_expired:{checkout.pk}",
   )
   ```
3. Marca el checkout como `status = "expired"`

---

## 9. Sistema de Wallet (Reservas)

### Estados del Wallet:

1. **Reserva (`reserve_funds`):**
   - Se llama cuando se crea el checkout
   - `pending_balance` aumenta
   - `available_balance` disminuye
   - Los fondos están "bloqueados" pero no descontados

2. **Confirmación (`confirm_reserved_funds`):**
   - Se llama cuando el pago es exitoso
   - `balance` disminuye (descuenta los fondos)
   - `pending_balance` disminuye (libera la reserva)
   - Crea transacción de tipo "payment"

3. **Liberación (`release_reserved_funds`):**
   - Se llama cuando se cancela o expira
   - `pending_balance` disminuye
   - `available_balance` aumenta
   - Los fondos vuelven a estar disponibles

---

## 10. Flujo de "Register Now, Pay Later"

**Modo:** `payment_mode = "register_only"`

**Proceso:**
1. No se crea sesión de Stripe
2. Se crea `StripeEventCheckout` con `status = "registered"`
3. Se crea `Order` con `status = "pending_registration"`
4. Los jugadores se registran pero no se confirma asistencia
5. El usuario puede "resumir" el checkout más tarde para pagar

**Resumir checkout:**
- Endpoint: `start_pending_payment` o `resume_checkout_data`
- Convierte el checkout a modo de pago normal
- Crea sesión de Stripe
- Sigue el flujo normal de pago

---

## 11. Diagrama de Flujo

```
Usuario selecciona opciones
    ↓
create_stripe_event_checkout_session
    ↓
[Validaciones]
    ↓
[Reserva wallet si aplica]
    ↓
[Crea StripeEventCheckout + Order]
    ↓
[Crea sesión Stripe]
    ↓
Usuario redirigido a Stripe
    ↓
    ├─→ Pago exitoso
    │       ↓
    │   stripe_event_checkout_success (redirect)
    │   stripe_webhook (checkout.session.completed)
    │       ↓
    │   [Confirma wallet]
    │       ↓
    │   _finalize_stripe_event_checkout
    │       ↓
    │   [Crea EventAttendance]
    │   [Crea HotelReservation]
    │   [Actualiza Order a "paid"]
    │       ↓
    │   ✅ Completado
    │
    └─→ Cancelación/Expiración
            ↓
        stripe_event_checkout_cancel (redirect)
        stripe_webhook (checkout.session.expired)
            ↓
        [Libera wallet]
            ↓
        ❌ Cancelado
```

---

## 12. Puntos Importantes

1. **Idempotencia:** `_finalize_stripe_event_checkout` es idempotente - puede llamarse múltiples veces sin duplicar datos

2. **Wallet Reservations:** Los fondos se reservan, no se descuentan, hasta que el pago sea exitoso

3. **Stock Validation:** Se valida disponibilidad de habitaciones antes de crear el checkout y antes de crear reservas

4. **Webhooks vs Redirects:** Ambos métodos (webhook y redirect) pueden procesar el pago exitoso, pero el webhook es más confiable

5. **Atomic Transactions:** Las operaciones críticas usan `transaction.atomic()` y `select_for_update()` para evitar condiciones de carrera

6. **Snapshot del Carrito:** Se guarda un snapshot del carrito de hotel en el checkout para procesarlo después del pago

---

## 13. Archivos Clave

- **Vista principal:** `apps/accounts/views_private.py`
  - `create_stripe_event_checkout_session` (línea 1976)
  - `stripe_event_checkout_success` (línea 3677)
  - `stripe_event_checkout_cancel` (línea 3780)
  - `stripe_webhook` (línea 3900)
  - `_finalize_stripe_event_checkout` (línea 3314)
  - `_create_order_from_stripe_checkout` (línea 3057)

- **Modelos:** `apps/accounts/models.py`
  - `StripeEventCheckout`
  - `Order`
  - `UserWallet`
  - `WalletTransaction`

- **Frontend:** `static/js/vue/event-detail.js`
  - Maneja la UI y cálculos del frontend
  - Envía datos al backend para crear checkout

---

## 14. Logs y Debugging

El sistema incluye logging extensivo en:
- Creación de checkout (línea 2483)
- Procesamiento de wallet
- Finalización de checkout
- Errores en webhooks

Los logs incluyen:
- IDs de evento, usuario, checkout
- Totales calculados (backend vs frontend)
- Estados de wallet
- Errores y excepciones
