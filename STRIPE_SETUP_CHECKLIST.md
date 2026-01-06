# ✅ Checklist de Configuración de Stripe - Sistema de Pagos

## 📋 Estado del Sistema

### ✅ Componentes Implementados

#### 1. **Backend (Django)**
- ✅ Modelo `StripeEventCheckout` creado y migrado
- ✅ Vistas implementadas:
  - `create_stripe_event_checkout_session` - Crea sesión de checkout
  - `stripe_event_checkout_success` - Callback de éxito
  - `stripe_event_checkout_cancel` - Callback de cancelación
  - `stripe_webhook` - Webhook para confirmación de pagos
- ✅ Función `_finalize_stripe_event_checkout` - Procesa pagos y crea reservas
- ✅ Función `_ensure_plan_subscription_schedule` - Gestiona planes de pago
- ✅ URLs configuradas en `apps/accounts/urls.py`
- ✅ Tests unitarios completos (8/8 tests pasando)

#### 2. **Frontend (Templates)**
- ✅ Botones "Pay now" y "Payment plan" en `detalle_evento.html`
- ✅ JavaScript `startStripeCheckout()` implementado
- ✅ Loader visual durante redirección a Stripe
- ✅ Cálculo de descuentos y fees
- ✅ Template `plan_pagos.html` para mostrar planes activos e historial

#### 3. **Configuración**
- ✅ Variables de entorno en `settings.py`:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_CURRENCY`
- ✅ Archivo `config/env.example` con variables documentadas

#### 4. **Migraciones**
- ✅ `0028_stripe_event_checkout.py` - Modelo base
- ✅ `0029_stripe_event_checkout_subscription_fields.py` - Campos de suscripción
- ✅ `0030_alter_stripeeventcheckout_amount_total.py` - Ajustes de campos

---

## 🔧 Configuración Requerida para Producción

### 1. **Variables de Entorno**

Configurar en el servidor de producción:

```bash
# Stripe API Keys (obtener de https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_...          # Clave secreta de producción
STRIPE_PUBLISHABLE_KEY=pk_live_...      # Clave pública de producción
STRIPE_WEBHOOK_SECRET=whsec_...         # Secreto del webhook
STRIPE_CURRENCY=usd                     # Moneda (usd, eur, mxn, etc.)
```

**⚠️ IMPORTANTE:**
- Usar claves de **producción** (`sk_live_...`, `pk_live_...`) en producción
- Usar claves de **test** (`sk_test_...`, `pk_test_...`) en desarrollo
- **NUNCA** commitear las claves reales al repositorio

### 2. **Configuración del Webhook en Stripe**

1. Ir a [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Crear nuevo endpoint:
   - **URL**: `https://tudominio.com/accounts/stripe/webhook/`
   - **Eventos a escuchar**:
     - `checkout.session.completed`
     - `checkout.session.expired`
3. Copiar el **Signing secret** (empieza con `whsec_...`)
4. Agregarlo a `STRIPE_WEBHOOK_SECRET` en variables de entorno

### 3. **URLs de Callback**

Las URLs de éxito y cancelación se generan automáticamente:
- **Éxito**: `https://tudominio.com/accounts/events/{event_id}/stripe/success/`
- **Cancelación**: `https://tudominio.com/accounts/events/{event_id}/stripe/cancel/`

Asegurarse de que `ALLOWED_HOSTS` en `settings.py` incluya el dominio de producción.

### 4. **Base de Datos**

Aplicar migraciones:
```bash
python manage.py migrate accounts
```

Verificar que las tablas existan:
```bash
python manage.py dbshell
\dt accounts_stripeeventcheckout
```

---

## 🧪 Verificación Pre-Producción

### 1. **Tests**
```bash
python manage.py test apps.accounts.test_stripe_checkout
```
✅ Debe pasar todos los tests (8/8)

### 2. **Verificación Manual en Test Mode**

1. Configurar claves de **test** en desarrollo
2. Crear un evento de prueba
3. Intentar hacer un pago con tarjeta de prueba:
   - Tarjeta exitosa: `4242 4242 4242 4242`
   - CVC: cualquier 3 dígitos
   - Fecha: cualquier fecha futura
4. Verificar que:
   - Se crea el `StripeEventCheckout` con status `"created"`
   - Al completar el pago, se marca como `"paid"`
   - Se crean las `EventAttendance` confirmadas
   - Se crean las `HotelReservation` (si hay hotel)
   - Aparece en "Plans & Payments"

### 3. **Verificar Webhook (Test Mode)**

1. En Stripe Dashboard, usar el webhook de test
2. Enviar evento de prueba `checkout.session.completed`
3. Verificar logs del servidor que se procesó correctamente

---

## 📊 Flujo Completo de Pago

### Modo "Pay Now"
1. Usuario selecciona jugadores y hotel (opcional)
2. Click en "Pay now"
3. Se crea sesión de Stripe Checkout (modo `payment`)
4. Usuario es redirigido a Stripe
5. Usuario completa el pago
6. Stripe redirige a `/stripe/success/`
7. Sistema verifica pago y llama `_finalize_stripe_event_checkout()`
8. Se crean reservas y asistencias
9. Usuario ve mensaje de éxito

### Modo "Payment Plan"
1. Usuario selecciona jugadores y hotel (opcional)
2. Click en "Payment plan"
3. Se crea sesión de Stripe Checkout (modo `subscription`)
4. Usuario es redirigido a Stripe
5. Usuario completa el primer pago
6. Stripe crea suscripción y redirige a `/stripe/success/`
7. Sistema crea `SubscriptionSchedule` para limitar meses
8. Sistema verifica pago y llama `_finalize_stripe_event_checkout()`
9. Se crean reservas y asistencias
10. Stripe cobra automáticamente los meses restantes

---

## 🔒 Seguridad

- ✅ CSRF protection habilitado (excepto webhook que usa `@csrf_exempt`)
- ✅ `@login_required` en todas las vistas de checkout
- ✅ Verificación de `payment_status == "paid"` antes de procesar
- ✅ Webhook verifica firma con `STRIPE_WEBHOOK_SECRET`
- ✅ Variables de entorno no están en el código
- ✅ `settings.py` en `.gitignore`

---

## 📝 Notas Importantes

1. **Idempotencia**: `_finalize_stripe_event_checkout()` es idempotente, puede llamarse múltiples veces sin duplicar datos.

2. **Dos vías de confirmación**:
   - **Callback de éxito**: Más rápido, pero puede fallar si el usuario cierra el navegador
   - **Webhook**: Más confiable, Stripe lo envía automáticamente

3. **Descuento del 5%**: Solo aplica en "Pay now" cuando hay hotel seleccionado.

4. **No-show fee**: Se aplica cuando hay jugadores pero NO hay hotel ($5.00).

5. **Planes de pago**: El sistema crea un `SubscriptionSchedule` para que la suscripción se cancele automáticamente después de N meses.

---

## ✅ Estado Final

**El sistema está COMPLETO y LISTO para procesar pagos reales.**

Solo falta:
1. Configurar las variables de entorno en producción
2. Configurar el webhook en Stripe Dashboard
3. Probar con claves de test antes de pasar a producción

