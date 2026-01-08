# REPORTE: Almacenamiento de Personas Adicionales en Reservas de Hotel

**Fecha:** 2026-01-07
**Análisis:** Verificación de dónde se guardan los datos de personas adicionales

---

## 📊 Resumen Ejecutivo

Se realizó un análisis exhaustivo de la base de datos para verificar dónde se almacenan los datos de las **personas adicionales** (additional guests) en las reservas de hotel pagadas a través de Stripe.

### Resultados Principales:

❌ **PROBLEMA IDENTIFICADO:** Los datos de personas adicionales **NO se están guardando** en ningún lugar de la base de datos, a pesar de que:
- El código está preparado para guardarlos
- Se calcula correctamente el cobro por personas adicionales
- El breakdown financiero incluye el cobro

---

## 🔍 Análisis Detallado

### 1. StripeEventCheckout.hotel_cart_snapshot

**Estado:** ❌ **NO SE GUARDAN LOS DATOS**

**Checkouts revisados:** 6 (todos los pagados)

**Campos encontrados en hotel_cart_snapshot:**
- `type`: "room"
- `room_id`: ID de la habitación
- `check_in`: Fecha de check-in
- `check_out`: Fecha de check-out
- `guests`: Número total de huéspedes (solo el número)
- `services`: Lista de servicios (vacía en todos los casos)

**Campos FALTANTES:**
- ❌ `additional_guest_names`: NO está presente
- ❌ `additional_guest_details`: NO está presente
- ❌ `guest_assignments`: NO está presente

**Ejemplo real (Checkout #46):**
```json
{
  "vue-room-4": {
    "type": "room",
    "room_id": 4,
    "check_in": "2026-07-22",
    "check_out": "2026-07-30",
    "guests": 4,
    "services": []
  }
}
```

**Ejemplo real (Checkout #41):**
```json
{
  "vue-room-1": {
    "type": "room",
    "room_id": 1,
    "check_in": "2026-06-20",
    "check_out": "2026-06-28",
    "guests": 4,
    "services": []
  }
}
```

---

### 2. HotelReservation

**Estado:** ❌ **NO HAY RESERVAS CREADAS**

**Resultado:** No se encontraron reservas (`HotelReservation`) asociadas a los checkouts pagados.

**Implicación:** Cuando un checkout de Stripe se marca como "paid", no se están creando las reservas de hotel correspondientes, o las reservas se crean sin la información de personas adicionales.

---

### 3. Order (Órdenes)

**Estado:** ❌ **NO HAY ÓRDENES ASOCIADAS**

**Resultado:** No se encontraron órdenes (`Order`) asociadas a los checkouts pagados.

**Implicación:** El proceso de finalización del checkout (`_finalize_stripe_event_checkout`) no se está ejecutando correctamente, o las órdenes no se están creando.

---

## 💰 Análisis Financiero - Personas Adicionales COBRADAS

A pesar de que los datos NO están guardados, el **cobro SÍ se está realizando correctamente**:

### Checkout #41 - Maribel Hernandez
- **Habitación:** Superior Room, 2 Doble (Fiesta Americana Mérida)
- **Precio incluye:** 2 huéspedes
- **Huéspedes registrados:** 4
- **Personas adicionales:** 2
- **Cobro calculado:** $560.00 USD (2 personas × 8 noches × $35.00/noche)
- **Estado:** ✅ **El cobro ESTÁ incluido en `hotel_room_base` ($1,884.72)**

### Checkout #46 - Aldo Martinez
- **Habitación:** Double Bed Suite (Embassy Suites)
- **Precio incluye:** 5 huéspedes
- **Huéspedes registrados:** 4
- **Personas adicionales:** 0
- **Cobro:** $0.00 USD (no aplica)

---

## 🐛 Problemas Identificados

### Problema #1: Datos no se guardan en hotel_cart_snapshot

**Código relevante:** `apps/accounts/views_private.py` líneas 2034-2089

El código intenta guardar:
```python
"additional_guest_names": additional_guest_names,
"additional_guest_details": additional_guest_details,
```

Pero estos campos **NO aparecen** en los snapshots guardados en la base de datos.

**Posibles causas:**
1. El código que guarda el snapshot se ejecuta antes de que se extraigan los datos de huéspedes adicionales
2. Hay un problema con el payload de Vue que no está enviando `guest_assignments` o `guests`
3. El snapshot se está sobrescribiendo en algún punto sin incluir estos campos

### Problema #2: No se crean reservas ni órdenes

**Código relevante:** `apps/accounts/views_private.py` función `_finalize_stripe_event_checkout()`

El código debería:
1. Crear una `Order` desde el checkout
2. Crear `HotelReservation` con los datos de personas adicionales
3. Asociar la reserva con la orden

**Estado actual:** Ninguna de estas operaciones se está ejecutando para los checkouts pagados.

---

## 📋 Recomendaciones

### Acción Inmediata #1: Verificar el flujo de finalización

Verificar si `_finalize_stripe_event_checkout()` se está ejecutando cuando un checkout se marca como "paid". Esta función debería:
- Ser llamada desde el webhook de Stripe (`checkout.session.completed`)
- Ser llamada desde `stripe_event_checkout_success`

### Acción Inmediata #2: Verificar el payload de Vue

Revisar si el frontend está enviando correctamente:
- `guest_assignments`: Mapeo de room_id → índices de huéspedes
- `guests`: Lista completa de objetos de huéspedes con sus datos

### Acción Inmediata #3: Agregar logging

Agregar logs en:
1. `create_stripe_event_checkout_session`: Para ver qué datos se reciben del frontend
2. `_finalize_stripe_event_checkout`: Para ver si se está ejecutando
3. Webhook handler: Para ver si está procesando correctamente

---

## 🔧 Solución Propuesta

### Paso 1: Guardar datos en el snapshot AL CREAR el checkout

Modificar `create_stripe_event_checkout_session` para asegurar que los datos de personas adicionales se guarden en `hotel_cart_snapshot`:

```python
vue_cart_snapshot[f"vue-room-{room_id}"] = {
    "type": "room",
    "room_id": int(room_id),
    "check_in": check_in,
    "check_out": check_out,
    "guests": max(1, guests_count),
    "services": [],
    # AGREGAR ESTOS CAMPOS:
    "additional_guest_names": additional_guest_names,
    "additional_guest_details": additional_guest_details,
    "guest_assignments": guest_assignments,  # Para referencia
    "all_guests": all_guests,  # Lista completa de huéspedes
}
```

### Paso 2: Asegurar que se creen las reservas

Verificar que `_finalize_stripe_event_checkout()` se ejecute correctamente y que cree las reservas con la información de personas adicionales desde el snapshot.

---

## 📝 Ejemplo de Datos que DEBERÍAN estar guardados

### Checkout #41 - Lo que DEBERÍA tener:

```json
{
  "vue-room-1": {
    "type": "room",
    "room_id": 1,
    "check_in": "2026-06-20",
    "check_out": "2026-06-28",
    "guests": 4,
    "services": [],
    "additional_guest_names": ["Nombre Persona 1", "Nombre Persona 2"],
    "additional_guest_details": [
      {
        "name": "Nombre Persona 1",
        "type": "adult",
        "birth_date": "2010-05-15",
        "email": "persona1@example.com"
      },
      {
        "name": "Nombre Persona 2",
        "type": "child",
        "birth_date": "2015-08-20",
        "email": ""
      }
    ]
  }
}
```

---

## ✅ Conclusión

**Estado actual:**
- ❌ Los nombres y detalles de personas adicionales NO se están guardando
- ✅ El cobro por personas adicionales SÍ se está calculando y cobrando correctamente
- ❌ Las reservas de hotel NO se están creando cuando el checkout se marca como pagado
- ❌ Las órdenes NO se están creando para los checkouts pagados

**Prioridad:** 🔴 **ALTA** - Es necesario corregir el flujo para que:
1. Los datos de personas adicionales se guarden en el snapshot
2. Se creen las reservas con la información completa
3. Se cree la orden asociada

---

**Reporte generado automáticamente el:** 2026-01-07
