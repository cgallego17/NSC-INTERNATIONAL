# Mejoras Implementadas en APIs de Ubicaciones

**Fecha:** 2026-01-07

---

## 📋 Resumen

Se han implementado mejoras de seguridad y rendimiento en las 8 APIs públicas de ubicaciones:

1. **Rate Limiting** - Limita el número de requests por IP
2. **Caché** - Almacena respuestas para mejorar rendimiento
3. **Validación de Parámetros** - Valida y sanitiza parámetros de entrada

---

## 🔒 APIs Mejoradas

### 1. `/locations/ajax/states/<int:country_id>/`
### 2. `/locations/ajax/cities/<int:state_id>/`
### 3. `/locations/api/countries/`
### 4. `/locations/api/states/`
### 5. `/locations/api/cities/`
### 6. `/locations/api/seasons/`
### 7. `/locations/api/rules/`
### 8. `/locations/api/sites/`

---

## ✅ Mejoras Implementadas

### 1. Rate Limiting

**Límite:** 150 requests por hora por IP

- Más permisivo que Instagram (150 vs 100) porque estas APIs se usan frecuentemente en formularios
- El contador se resetea después de 1 hora
- Si se excede el límite, retorna HTTP 429 con mensaje de error

**Headers de Respuesta:**
- `X-RateLimit-Remaining`: Requests restantes
- `X-RateLimit-Limit`: Límite total (150)

### 2. Caché

**Duración:** 30 minutos (1800 segundos)

- Reduce significativamente la carga en la base de datos
- Claves de caché basadas en parámetros de búsqueda
- Mejora tiempos de respuesta

**Claves de Caché:**
- `locations_states_by_country_{country_id}`
- `locations_cities_by_state_{state_id}`
- `locations_countries_api_{id}_{search_query}`
- `locations_states_api_{country_id}_{state_id}_{search_query}`
- `locations_cities_api_{state_id}_{city_id}_{search_query}`
- `locations_seasons_api_all`
- `locations_rules_api_all`
- `locations_sites_api_{city_id or 'all'}`

### 3. Validación de Parámetros

**Mejoras:**
- IDs validados como enteros (retorna 400 si es inválido)
- Búsquedas limitadas a 100 caracteres máximo
- Validación de tipos antes de procesar

**Ejemplo:**
```python
# Validar country_id
try:
    country_id = int(country_id)
except (ValueError, TypeError):
    return JsonResponse({"error": "Invalid country ID"}, status=400)

# Limitar tamaño de búsqueda
search_query = request.GET.get("q", "").strip()
if len(search_query) > 100:
    search_query = search_query[:100]
```

---

## 📊 Comparativa Antes/Después

### Antes

| Característica | Estado |
|----------------|--------|
| Rate Limiting | ❌ No |
| Caché | ❌ No |
| Validación de Tamaño | ❌ No |
| Headers Informativos | ❌ No |
| Protección DoS | ❌ No |

### Después

| Característica | Estado |
|----------------|--------|
| Rate Limiting | ✅ 150 requests/hora |
| Caché | ✅ 30 minutos |
| Validación de Tamaño | ✅ 100 caracteres max |
| Headers Informativos | ✅ X-RateLimit-* |
| Protección DoS | ✅ Implementada |

---

## 🔧 Funciones Implementadas

### `_get_client_ip(request)`
Obtiene la IP real del cliente, considerando proxies y headers `X-Forwarded-For`.

### `_check_rate_limit(request, cache_key_prefix, max_requests=150, window_seconds=3600)`
Verifica rate limiting usando caché de Django.

**Parámetros:**
- `request`: HttpRequest object
- `cache_key_prefix`: Prefijo para la clave de caché
- `max_requests`: Número máximo de requests (por defecto 150)
- `window_seconds`: Ventana de tiempo (por defecto 3600 = 1 hora)

**Retorna:**
- `is_allowed`: Si se permite el request
- `remaining_requests`: Requests restantes

---

## 📈 Ejemplo de Uso

### Request Normal

```http
GET /locations/api/countries/?q=mexico
```

**Respuesta:**
```json
[
  {"id": 1, "name": "Mexico", "code": "MX"}
]
```

**Headers:**
```
X-RateLimit-Remaining: 149
X-RateLimit-Limit: 150
```

### Rate Limit Excedido

```http
GET /locations/api/countries/
```

**Respuesta (HTTP 429):**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

---

## 🛡️ Protecciones Implementadas

### 1. Protección contra DoS
- Rate limiting previene abuso masivo de recursos
- Caché reduce carga en base de datos

### 2. Validación de Entrada
- IDs validados como enteros
- Búsquedas limitadas en tamaño
- Manejo de errores mejorado

### 3. Optimización de Rendimiento
- Caché de 30 minutos reduce queries
- Headers informativos para monitoreo

---

## ⚙️ Configuración

### Parámetros Ajustables

```python
# En cada función API

MAX_REQUESTS_PER_HOUR = 150  # Máximo 150 requests por hora
CACHE_DURATION = 1800        # Caché de 30 minutos
MAX_SEARCH_LENGTH = 100      # Máximo 100 caracteres en búsquedas
```

### Ajustar Límites

Para cambiar los límites, modificar en cada función:

```python
is_allowed, remaining = _check_rate_limit(
    request,
    "locations_countries_api",
    max_requests=200,  # Cambiar aquí
    window_seconds=3600
)
```

---

## ✅ Checklist de Implementación

- [x] Rate limiting en todas las APIs
- [x] Caché en todas las APIs
- [x] Validación de parámetros
- [x] Validación de tamaño de búsquedas
- [x] Headers informativos
- [x] Manejo de errores mejorado
- [x] Soporte para proxies (X-Forwarded-For)

---

## 📊 Impacto Esperado

### Rendimiento
- **Reducción de queries:** ~70% (gracias al caché)
- **Tiempo de respuesta:** Mejora significativa en requests cacheados
- **Carga del servidor:** Reducción notable

### Seguridad
- **Protección DoS:** Implementada
- **Abuso de recursos:** Prevenido
- **Validación:** Mejorada

---

## 🔄 Próximas Mejoras Recomendadas

### Prioridad Baja

1. **Logging de Requests**
   - Registrar requests que exceden límites
   - Alertas para patrones anómalos

2. **Métricas de Uso**
   - Tracking de uso por API
   - Dashboard de monitoreo

3. **Rate Limiting por Usuario Autenticado**
   - Límites más altos para usuarios autenticados
   - Tracking por usuario además de IP

---

## 📝 Resumen

**Estado:** ✅ **Todas las APIs Mejoradas**

**Protecciones:**
- ✅ Rate limiting: 150 requests/hora por IP
- ✅ Caché: 30 minutos
- ✅ Validación de parámetros
- ✅ Headers informativos

**APIs Mejoradas:** 8/8 (100%)

---

**Última actualización:** 2026-01-07



