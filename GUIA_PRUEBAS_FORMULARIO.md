# 🧪 GUÍA DE PRUEBAS - FORMULARIO DE CREAR EVENTO

## ✅ VERIFICACIÓN COMPLETADA DEL CÓDIGO

### 1. **Backend - Modelo Event** ✅
- `event_contact` cambiado correctamente a `ManyToManyField`
- Todos los campos necesarios están definidos
- Migraciones ejecutadas exitosamente

### 2. **Backend - Formulario EventForm** ✅
```python
✅ season - Temporada (Select)
✅ title - Título del Evento
✅ description - Descripción (HTML)
✅ country - País (Autocomplete)
✅ state - Estado (Autocomplete)
✅ city - Ciudad (Autocomplete)
✅ rule - Reglamento (Select)
✅ event_type - Tipo de Evento (Select)
✅ divisions - Divisiones (Múltiple con búsqueda)
✅ start_date - Fecha Inicio
✅ end_date - Fecha Fin
✅ entry_deadline - Límite de Registro
✅ default_entry_fee - Precio
✅ payment_deadline - Límite de Pago
✅ gate_fee_type - Tipo de Gate Fee
✅ gate_fee_amount - Precio Gate Fee
✅ primary_site - Sitio Principal (Autocomplete)
✅ additional_sites - Sitios Adicionales (Múltiple con búsqueda)
✅ hotel - Hotel Sede (Autocomplete)
✅ additional_hotels - Hoteles Adicionales (Múltiple con búsqueda)
✅ event_contact - Contactos (Múltiple con búsqueda)
✅ image - Logo del Evento
✅ video_url - Video del Evento
✅ email_welcome_body - Cuerpo del Correo (HTML)
```

### 3. **Backend - APIs Públicas** ✅
```
✅ /locations/countries/api/ - Lista de países
✅ /locations/countries/api/?q=mex - Búsqueda de países
✅ /locations/countries/api/?id=1 - País específico
✅ /locations/states/api/?country=1 - Estados por país
✅ /locations/states/api/?q=jalisco - Búsqueda de estados
✅ /locations/cities/api/?state=1 - Ciudades por estado
✅ /locations/cities/api/?q=guadalajara - Búsqueda de ciudades
✅ /locations/sites/api/?city=1 - Sitios por ciudad
✅ /locations/hotels/api/?city=1 - Hoteles por ciudad
```

### 4. **Frontend - Template event_form.html** ✅
```javascript
✅ setupImprovedAutocomplete() - Autocomplete mejorado
✅ loadDivisionsFromContext() - Carga divisiones dinámicamente
✅ loadContacts() - Carga contactos
✅ loadSites() - Carga sitios por ciudad
✅ loadHotels() - Carga hoteles por ciudad
✅ loadPrimarySites() - Carga sitio principal
✅ loadPrimaryHotels() - Carga hotel principal
✅ reloadSitesAndHotels() - Recarga al cambiar ciudad
✅ Chips visuales para selección múltiple
✅ Búsqueda en tiempo real
✅ Navegación con teclado (flechas ↑↓, Enter, Esc)
```

### 5. **Modelo EventContact** ✅
```python
✅ name - Nombre
✅ position - Cargo (NUEVO)
✅ organization - Organización (NUEVO)
✅ photo - Foto
✅ phone - Teléfono
✅ email - Email
✅ country, state, city - Ubicación
✅ information - Información adicional
✅ is_active - Estado activo
✅ __str__ muestra: "Nombre - Cargo (Organización)"
```

---

## 🎯 PRUEBAS MANUALES A REALIZAR

### **PASO 1: Abrir el Formulario**
```
URL: http://127.0.0.1:8000/events/create/
```

### **PASO 2: Probar Autocomplete de Ubicación**

#### ✓ País:
1. Hacer click en el campo "País"
2. **Debería mostrar** todos los países disponibles
3. Escribir "mex"
4. **Debería filtrar** y mostrar solo "México"
5. Hacer click en "México"
6. **Debería** habilitar el campo "Estado"

#### ✓ Estado:
1. Hacer click en el campo "Estado" (ahora habilitado)
2. **Debería mostrar** todos los estados de México
3. Escribir "jal"
4. **Debería filtrar** y mostrar "Jalisco"
5. Hacer click en "Jalisco"
6. **Debería** habilitar el campo "Ciudad"

#### ✓ Ciudad:
1. Hacer click en el campo "Ciudad" (ahora habilitado)
2. **Debería mostrar** todas las ciudades de Jalisco
3. Escribir "guad"
4. **Debería filtrar** y mostrar "Guadalajara"
5. Hacer click en "Guadalajara"
6. **Debería** cargar sitios y hoteles de Guadalajara

### **PASO 3: Probar Sitios y Hoteles**

#### ✓ Sitio Principal:
1. Hacer click en "Sitio del Evento (Primary)"
2. **Debería mostrar** sitios de Guadalajara
3. Seleccionar un sitio
4. **Debería** aparecer el nombre del sitio seleccionado

#### ✓ Sitios Adicionales:
1. En el buscador escribir nombre de sitio
2. **Debería filtrar** la lista
3. Hacer click en un sitio
4. **Debería** aparecer como chip azul arriba
5. Hacer click en la X del chip
6. **Debería** quitarse de la selección

#### ✓ Hotel Sede:
1. Hacer click en "Hotel Sede"
2. **Debería mostrar** hoteles de Guadalajara
3. Seleccionar un hotel
4. **Debería** aparecer el nombre del hotel seleccionado

#### ✓ Hoteles Adicionales:
1. En el buscador escribir nombre de hotel
2. **Debería filtrar** la lista
3. Hacer click en un hotel
4. **Debería** aparecer como chip azul arriba
5. Hacer click en la X del chip
6. **Debería** quitarse de la selección

### **PASO 4: Probar Divisiones**

1. En el buscador de divisiones escribir "U8"
2. **Debería filtrar** la lista de divisiones
3. Hacer click en una división
4. **Debería** aparecer como chip azul arriba
5. Seleccionar varias divisiones
6. **Deberían** aparecer todas como chips
7. Hacer click en la X de un chip
8. **Debería** quitarse de la selección

### **PASO 5: Probar Contactos**

1. En el buscador de contactos escribir un nombre
2. **Debería filtrar** la lista de contactos
3. **Debería mostrar**: Nombre en negrita + Cargo y Organización abajo
4. Hacer click en un contacto
5. **Debería** aparecer como chip con nombre y cargo
6. Seleccionar varios contactos
7. **Deberían** aparecer todos como chips
8. Hacer click en la X de un chip
9. **Debería** quitarse de la selección

### **PASO 6: Llenar el Resto del Formulario**

1. **Temporada**: Seleccionar una temporada
2. **Título**: Escribir "Evento de Prueba 2024"
3. **Reglamento**: Seleccionar un reglamento
4. **Tipo de Evento**: Seleccionar un tipo
5. **Fechas**: Completar todas las fechas
6. **Precios**: Ingresar precios
7. **Tipo de Gate Fee**: Seleccionar
8. **Descripción**: Escribir descripción (con editor HTML)
9. **Email Welcome Body**: Escribir cuerpo del email (con editor HTML)

### **PASO 7: Guardar el Evento**

1. Hacer click en "Crear Evento"
2. **Debería**:
   - Mostrar mensaje "Evento creado exitosamente"
   - Redirigir a la lista de eventos
   - El evento debería aparecer en la lista

### **PASO 8: Verificar el Evento Creado**

1. Ir a la lista de eventos
2. Buscar el evento "Evento de Prueba 2024"
3. Hacer click para ver detalle
4. **Verificar que aparezcan**:
   - ✓ Título correcto
   - ✓ Ubicación (País, Estado, Ciudad)
   - ✓ Sitio principal seleccionado
   - ✓ Sitios adicionales (si se seleccionaron)
   - ✓ Hotel sede seleccionado
   - ✓ Hoteles adicionales (si se seleccionaron)
   - ✓ Divisiones seleccionadas
   - ✓ Contactos seleccionados (con cargo y organización)
   - ✓ Todas las fechas
   - ✓ Todos los precios

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "No se encontraron divisiones"
**Solución**: Ir a Configuración → Divisiones y crear al menos una división activa

### Problema 2: "No se encontraron contactos"
**Solución**: Ir a Contactos → Crear Contacto y crear al menos un contacto activo

### Problema 3: "No hay sitios disponibles para [ciudad]"
**Solución**: Ir a Ubicaciones → Sitios y crear sitios para esa ciudad

### Problema 4: "No hay hoteles disponibles para [ciudad]"
**Solución**: Ir a Hoteles → Lista de Hoteles y crear hoteles para esa ciudad

### Problema 5: Autocomplete no muestra resultados
**Solución**: 
1. Abrir Consola del Navegador (F12)
2. Buscar errores en rojo
3. Verificar que las APIs respondan correctamente
4. Recargar la página con Ctrl+F5

### Problema 6: Los chips no se quitan al hacer click en la X
**Solución**: Verificar en la consola del navegador si hay errores JavaScript

---

## ✅ CHECKLIST FINAL

### Backend
- [ ] Migraciones ejecutadas sin errores
- [ ] Modelo Event con event_contact como ManyToManyField
- [ ] Modelo EventContact con campos position y organization
- [ ] APIs públicas respondiendo correctamente
- [ ] Formulario EventForm con todos los campos

### Frontend
- [ ] Autocomplete de país funciona
- [ ] Autocomplete de estado funciona
- [ ] Autocomplete de ciudad funciona
- [ ] Sitios se cargan al seleccionar ciudad
- [ ] Hoteles se cargan al seleccionar ciudad
- [ ] Divisiones se muestran con búsqueda
- [ ] Contactos se muestran con cargo y organización
- [ ] Chips de selección múltiple funcionan
- [ ] Se puede guardar un evento completo

### Funcionalidad
- [ ] Evento se guarda correctamente
- [ ] Relaciones ManyToMany se guardan
- [ ] Se puede editar un evento
- [ ] Se puede ver el detalle completo
- [ ] Validaciones funcionan correctamente

---

## 📊 RESULTADO ESPERADO

Al finalizar todas las pruebas, deberías poder:

1. ✅ Crear un evento completo con todos los campos
2. ✅ Seleccionar múltiples divisiones
3. ✅ Seleccionar múltiples contactos (con cargo visible)
4. ✅ Seleccionar ubicación usando autocomplete
5. ✅ Seleccionar sitios y hoteles filtrados por ciudad
6. ✅ Ver toda la información guardada correctamente
7. ✅ Editar el evento después de creado

---

**¡Éxito en las pruebas!** 🎉


