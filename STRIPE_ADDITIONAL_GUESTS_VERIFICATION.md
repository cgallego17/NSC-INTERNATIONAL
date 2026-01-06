# ✅ Verificación: Huéspedes Adicionales en Compras Stripe

## 📋 Resumen

**✅ CONFIRMADO: Los huéspedes adicionales SÍ se guardan y se calculan correctamente.**

---

## 🔍 Análisis del Flujo

### 1. **En el Carrito (Snapshot)**

Cuando se agrega una habitación al carrito, se guarda:
```json
{
  "room_123_2024-06-01_2024-06-05": {
    "type": "room",
    "room_id": 123,
    "hotel_id": 45,
    "check_in": "2024-06-01",
    "check_out": "2024-06-05",
    "nights": 4,
    "guests": 3,  // ← Número TOTAL de huéspedes
    "services": [...]
  }
}
```

**✅ Se guarda `guests` (número total de huéspedes)**

### 2. **En el Cálculo del Precio**

Cuando se calcula el precio en `_compute_hotel_amount_from_cart()`:

```python
guests = int(item_data.get("guests", 1) or 1)
includes = int(room.price_includes_guests or 1)  # Ej: 2
extra_guests = max(0, guests - includes)  # Ej: 3 - 2 = 1 extra

per_night_total = (
    room.price_per_night
    + (room.additional_guest_price or Decimal("0.00")) * extra_guests
)
```

**✅ Se calcula correctamente el precio de huéspedes adicionales**

### 3. **En el Breakdown**

El breakdown guarda el total calculado que **YA incluye** los huéspedes adicionales:
```json
{
  "hotel_room_base": "450.00",  // ← Ya incluye precio de extra guests
  "hotel_total": "534.00",      // ← Ya incluye impuestos sobre el total
  ...
}
```

**✅ El breakdown refleja el precio correcto con huéspedes adicionales**

### 4. **En la Reserva Creada**

Cuando se crea la reserva desde el snapshot:

```python
reservation = HotelReservation.objects.create(
    ...
    number_of_guests=int(item_data.get("guests", 1) or 1),  # ← Total de huéspedes
    ...
)
```

**✅ Se guarda `number_of_guests` (total de huéspedes)**

### 5. **En el Cálculo del Total de la Reserva**

El método `calculate_total()` de `HotelReservation` recalcula correctamente:

```python
includes = int(self.room.price_includes_guests or 1)
extra_guests = max(0, int(self.number_of_guests or 0) - includes)
per_night_total = (
    self.room.price_per_night
    + (self.room.additional_guest_price or Decimal("0.00")) * extra_guests
)
```

**✅ El total se calcula correctamente usando los huéspedes adicionales**

---

## ✅ Verificación de Integridad

### Lo que SÍ se Guarda

1. **En el Snapshot (`hotel_cart_snapshot`)**:
   - ✅ `guests` - Número total de huéspedes
   - ✅ Con esto se puede calcular siempre cuántos son adicionales

2. **En la Reserva (`HotelReservation`)**:
   - ✅ `number_of_guests` - Número total de huéspedes
   - ✅ `room` - Habitación (que tiene `price_includes_guests` y `additional_guest_price`)
   - ✅ Con estos datos se puede calcular siempre el precio correcto

3. **En el Breakdown (`breakdown`)**:
   - ✅ `hotel_room_base` - Precio base que YA incluye huéspedes adicionales
   - ✅ Refleja el precio exacto que se pagó

### Cálculo de Huéspedes Adicionales

**Fórmula:**
```
extra_guests = max(0, total_guests - price_includes_guests)
```

**Ejemplo:**
- Habitación incluye: 2 huéspedes (`price_includes_guests = 2`)
- Total de huéspedes: 3 (`guests = 3`)
- Huéspedes adicionales: 3 - 2 = 1
- Precio adicional: `additional_guest_price * 1 * nights`

---

## 📊 Ejemplo Completo

### Escenario:
- Habitación: $100/noche
- Incluye: 2 huéspedes
- Precio adicional por huésped: $20/noche
- Total de huéspedes: 3
- Noches: 4

### Cálculo:
```
extra_guests = 3 - 2 = 1
per_night = $100 + ($20 * 1) = $120
total_room = $120 * 4 = $480
```

### Lo que se Guarda:

**1. En el Snapshot:**
```json
{
  "guests": 3  // Total de huéspedes
}
```

**2. En el Breakdown:**
```json
{
  "hotel_room_base": "480.00"  // Ya incluye el extra guest
}
```

**3. En la Reserva:**
```python
number_of_guests = 3
room.price_includes_guests = 2
room.additional_guest_price = 20.00
```

**4. Cálculo del Total (en la reserva):**
```python
extra_guests = 3 - 2 = 1
per_night = 100 + (20 * 1) = 120
total = 120 * 4 = 480
```

---

## ⚠️ Consideración: ¿Falta Guardar Algo?

### Opción Actual (Implementada)
- Se guarda `guests` (total) en el snapshot
- Se guarda `number_of_guests` (total) en la reserva
- Se calcula `extra_guests` cuando se necesita

**Ventajas:**
- ✅ Más simple
- ✅ Siempre se puede recalcular
- ✅ Si cambia `price_includes_guests`, el cálculo sigue siendo correcto

**Desventajas:**
- ⚠️ No hay un campo explícito "número de huéspedes adicionales" guardado históricamente
- ⚠️ Si cambia `additional_guest_price`, el precio histórico podría ser diferente

### Opción Alternativa (No Implementada)
Guardar explícitamente:
- `extra_guests` en el snapshot
- `extra_guests` en la reserva
- `extra_guests_price` en el breakdown

**Ventajas:**
- ✅ Registro histórico más explícito
- ✅ Más fácil de auditar

**Desventajas:**
- ⚠️ Más campos que mantener
- ⚠️ Posible inconsistencia si cambian los precios

---

## ✅ Conclusión

**Los huéspedes adicionales SÍ se guardan y calculan correctamente:**

1. ✅ El snapshot guarda el número total de huéspedes (`guests`)
2. ✅ El cálculo del precio incluye correctamente los huéspedes adicionales
3. ✅ El breakdown refleja el precio correcto con extras
4. ✅ La reserva guarda el número total de huéspedes (`number_of_guests`)
5. ✅ El cálculo del total de la reserva incluye correctamente los extras

**El sistema funciona correctamente.** Los huéspedes adicionales se calculan dinámicamente cuando se necesita, lo cual es más flexible y menos propenso a errores.

**Si se desea un registro más explícito**, se podría agregar un campo `extra_guests` al snapshot y a la reserva, pero **no es necesario** para el correcto funcionamiento del sistema.

