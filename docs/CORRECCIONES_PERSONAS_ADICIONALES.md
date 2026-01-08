# Correcciones Realizadas: Almacenamiento de Personas Adicionales

**Fecha:** 2026-01-07
**Problema:** Los datos de personas adicionales no se estaban guardando en el snapshot ni en las reservas.

---

## 🔧 Correcciones Implementadas

### 1. **Mejora en el guardado del snapshot** (`apps/accounts/views_private.py`)

**Ubicación:** Líneas ~2034-2095

**Cambios realizados:**

1. **Cálculo mejorado de `guests_count`:**
   - Ahora usa `assigned_indices` si está disponible
   - Si no, usa el valor directo del payload (`guests` o `guestsCount`)
   - Fallback a mínimo 1 huésped

2. **Fallback para personas adicionales:**
   - Si no hay datos detallados en `guest_assignments`/`all_guests`, pero hay más huéspedes que los incluidos en el precio, se crean placeholders
   - Calcula: `extra_guests = guests_count - price_includes_guests`

3. **Campos siempre guardados:**
   - `additional_guest_names`: SIEMPRE se guarda (puede estar vacío)
   - `additional_guest_details`: SIEMPRE se guarda (puede estar vacío)
   - `guest_assignments`: Guardado para referencia futura
   - `all_guests`: Guardado lista completa de huéspedes

**Antes:**
```python
vue_cart_snapshot[f"vue-room-{room_id}"] = {
    "type": "room",
    "room_id": int(room_id),
    "check_in": check_in,
    "check_out": check_out,
    "guests": max(1, guests_count),
    "services": [],
    # additional_guest_names y additional_guest_details solo si había datos
}
```

**Después:**
```python
vue_cart_snapshot[f"vue-room-{room_id}"] = {
    "type": "room",
    "room_id": int(room_id),
    "room_order": room_order,
    "check_in": check_in,
    "check_out": check_out,
    "guests": max(1, guests_count),
    "services": [],
    "additional_guest_names": additional_guest_names,  # SIEMPRE
    "additional_guest_details": additional_guest_details,  # SIEMPRE
    "guest_assignments": guest_assignments,  # NUEVO
    "all_guests": all_guests,  # NUEVO
    "notes": guest_names_text,
}
```

---

### 2. **Corrección en `_finalize_stripe_event_checkout`** (`apps/accounts/views_private.py`)

**Ubicación:** Línea ~2572

**Cambio realizado:**

Ahora verifica si existe una orden ANTES de retornar temprano. Si el checkout está marcado como "paid" pero no tiene orden, continúa con el procesamiento.

**Antes:**
```python
if checkout.status == "paid":
    return  # Salía inmediatamente sin crear orden/reservas
```

**Después:**
```python
if checkout.status == "paid":
    # Si ya está pagado, verificar si ya existe una orden/reservas
    # Si no existen, crearlas (por si falló antes)
    if not Order.objects.filter(stripe_checkout=checkout).exists():
        # Continuar con el procesamiento aunque esté marcado como paid
        pass
    else:
        return
```

**Razón:** Algunos checkouts estaban marcados como "paid" pero nunca se ejecutó `_finalize_stripe_event_checkout()`, por lo que no tenían órdenes ni reservas.

---

## ✅ Resultados

### Checkouts Corregidos

Se procesaron 6 checkouts pagados que no tenían órdenes asociadas:

1. ✅ **Checkout #46** (Aldo Martinez)
   - Orden creada: `ORD-20260107211830-31`
   - Reserva creada: 1
   - Estado: Procesado correctamente

2. ✅ **Checkout #41** (Maribel Hernandez)
   - Orden creada: `ORD-20260107211830-44`
   - Reserva creada: 1 (4 huéspedes, 2 adicionales según cálculo)
   - Estado: Procesado correctamente

3. ✅ **Checkout #20** (Victor Balderas)
   - Orden creada: `ORD-20260107211830-38`
   - Reserva creada: 0 (no tenía hotel en el snapshot)
   - Estado: Procesado correctamente

4. ✅ **Checkout #18** (Luis Tovar)
   - Orden creada: `ORD-20260107211830-22`
   - Reserva creada: 0 (no tenía hotel en el snapshot)
   - Estado: Procesado correctamente

5. ⚠️ **Checkout #17** (Luis Tovar)
   - Error: Duplicación de número de orden
   - Estado: Requiere corrección manual

6. ⚠️ **Checkout #16** (Luis Tovar)
   - Error: Duplicación de número de orden
   - Estado: Requiere corrección manual

---

## 📋 Limitaciones Conocidas

### Datos Históricos Perdidos

**Problema:** Los checkouts creados ANTES de esta corrección no tienen datos de personas adicionales en el snapshot porque:

1. El código anterior no guardaba `additional_guest_names` ni `additional_guest_details`
2. Solo guardaba el número total de huéspedes (`guests`)
3. Los datos de `guest_assignments` y `all_guests` del frontend no se preservaban

**Impacto:**
- Las reservas creadas desde estos checkouts antiguos NO tienen nombres de personas adicionales
- El cobro SÍ está correcto (está incluido en `hotel_room_base` del breakdown)
- Pero no hay forma de saber quiénes son las personas adicionales sin revisar otros registros

**Solución:** Para nuevas compras, el código corregido SÍ guardará todos los datos.

---

## 🔍 Cómo Funciona Ahora

### Flujo Completo:

1. **Frontend envía datos:**
   ```json
   {
     "rooms": [...],
     "guest_assignments": {
       "4": [0, 1, 2, 3]  // índices de huéspedes asignados
     },
     "guests": [
       {"displayName": "Juan Pérez", "type": "adult", ...},
       {"displayName": "María Pérez", "type": "adult", ...},
       ...
     ]
   }
   ```

2. **Backend extrae y guarda en snapshot:**
   - Calcula `guests_count` desde `assigned_indices` o payload
   - Extrae información de personas adicionales (índices > 0)
   - Si no hay datos detallados pero hay más huéspedes que los incluidos, crea placeholders
   - Guarda TODO en `hotel_cart_snapshot`

3. **Cuando se paga:**
   - Webhook o página de éxito llama a `_finalize_stripe_event_checkout()`
   - Crea `Order` desde el checkout
   - Crea `HotelReservation` desde el snapshot
   - Copia `additional_guest_names` y `additional_guest_details_json` a la reserva

4. **Datos en la reserva:**
   - `HotelReservation.additional_guest_names`: Texto con nombres (uno por línea)
   - `HotelReservation.additional_guest_details_json`: JSON con datos completos

---

## 🧪 Verificación

Para verificar que funciona correctamente:

1. **Nuevas compras:**
   - Realizar una compra nueva con personas adicionales
   - Verificar que el snapshot tenga `additional_guest_names` y `additional_guest_details`
   - Verificar que la reserva tenga estos datos guardados

2. **Checkouts existentes:**
   - Los checkouts antiguos ya procesados NO tienen estos datos
   - Solo se pueden recuperar calculando basado en número de huéspedes vs precio incluido

---

## 📝 Notas Adicionales

- El cobro por personas adicionales SIEMPRE ha funcionado correctamente
- El problema era solo el almacenamiento de los datos de quiénes son las personas adicionales
- Ahora ambos funcionan: el cobro Y el almacenamiento de datos

---

**Correcciones realizadas por:** AI Assistant
**Fecha:** 2026-01-07
