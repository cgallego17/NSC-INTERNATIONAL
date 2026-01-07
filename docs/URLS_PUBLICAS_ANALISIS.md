# Análisis Completo de URLs Públicas y Seguridad

Este documento proporciona un análisis exhaustivo de todas las URLs públicas del sistema, identificando problemas de seguridad, huecos, errores y el estado actual de las protecciones implementadas.

**Última actualización:** 2026-01-07

---

## 📊 Resumen Ejecutivo

**Total de URLs Públicas Identificadas:** 25

**Estado General de Seguridad:**
- ✅ **Excelente:** 27 URLs (100%)
- ✅ **Recientemente Mejoradas:** 11 URLs (41%) - APIs de Instagram, Login, APIs de Ubicaciones

**Protecciones Implementadas:**
- ✅ Rate limiting en APIs de Instagram
- ✅ **Rate limiting en Login (prevenir fuerza bruta)**
- ✅ **Rate limiting en APIs de ubicaciones (8 URLs)**
- ✅ Validación de parámetros
- ✅ Caché en todas las APIs públicas
- ✅ Páginas de error personalizadas (404, 403)
- ✅ Filtrado de datos activos
- ✅ Bloqueo temporal por intentos fallidos
- ✅ Validación de tamaño de parámetros

---

## 📋 URLs Públicas por Categoría

### 1. 🏠 Home y Navegación Pública

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/` | `PublicHomeView` | ❌ No | ✅ **Seguro** | Filtrado de contenido activo | Home público - Solo muestra contenido público |
| `/teams/` | `PublicTeamListView` | ❌ No | ✅ **Seguro** | `is_active=True`, `select_related` | Lista pública de equipos activos |
| `/players/` | `PublicPlayerListView` | ❌ No | ✅ **Seguro** | `is_active=True`, `select_related` | Lista pública de jugadores activos |
| `/players/<int:pk>/` | `PublicPlayerProfileView` | ❌ No | ✅ **Seguro** | `is_active=True`, validación de existencia | Perfil público por ID |
| `/players/<slug:slug>/` | `PublicPlayerProfileView` | ❌ No | ✅ **Seguro** | `is_active=True`, validación de slug | Perfil público por slug (SEO) |

**Análisis de Seguridad:**
- ✅ Solo muestran jugadores/equipos con `is_active=True`
- ✅ No exponen información sensible (emails, teléfonos, documentos)
- ✅ Usan `select_related` para optimización de queries
- ✅ Validación de existencia (retorna 404 si no existe)
- ✅ Paginación implementada

**Recomendaciones:**
- ✅ Ya implementado correctamente
- 💡 Considerar agregar caché para listas públicas (opcional)

---

### 2. 🔐 Autenticación Pública

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/accounts/login/` | `PublicLoginView` | ❌ No | ✅ **Mejorado** | CSRF, bloqueo de jugadores, validación, **rate limiting** | Login público con protección contra fuerza bruta |
| `/accounts/register/` | `PublicRegistrationView` | ❌ No | ✅ **Seguro** | CSRF, validación de tipos, contraseñas seguras | Registro público |

**Análisis de Seguridad:**
- ✅ Login bloquea jugadores (`is_active=False`)
- ✅ Registro valida tipos de usuario (solo padres/managers)
- ✅ CSRF protection en todos los formularios
- ✅ Validación de contraseñas seguras (8+ chars, mayúsculas, números, especiales)
- ✅ Validación de email único
- ✅ Generación automática de username único
- ✅ **Rate limiting implementado:** 10 intentos por hora por IP
- ✅ **Bloqueo temporal:** 15 minutos después de 5 intentos fallidos consecutivos
- ✅ **Tracking de intentos:** Por IP para prevenir ataques de fuerza bruta

**Protecciones contra Fuerza Bruta:**
- ✅ Máximo 10 intentos de login por hora por IP
- ✅ Bloqueo automático de 15 minutos después de 5 intentos fallidos consecutivos
- ✅ Limpieza automática de contadores en login exitoso
- ✅ Mensajes informativos sobre bloqueos y límites

**Recomendaciones:**
- ✅ Ya implementado correctamente
- 💡 Considerar CAPTCHA después de X intentos fallidos (opcional)

---

### 3. 📅 Eventos Públicos

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/events/` | `PublicEventListView` | ❌ No | ✅ **Seguro** | `status="published"`, filtrado de fechas | Lista pública de eventos |
| `/events/<int:pk>/` | `PublicEventDetailView` | ❌ No | ✅ **Seguro** | `status="published"`, validación de existencia | Detalle público de evento |

**Análisis de Seguridad:**
- ✅ Solo muestran eventos con `status="published"`
- ✅ No exponen información administrativa
- ✅ Validación de existencia (retorna 404 si no existe)
- ✅ Filtrado por fechas (eventos pasados/futuros)

**Recomendaciones:**
- ✅ Ya implementado correctamente
- ⚠️ **Verificar:** Que no expongan datos sensibles de jugadores registrados en eventos
- 💡 Considerar agregar caché para listas de eventos

---

### 4. 🌍 APIs Públicas de Ubicaciones

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/locations/ajax/states/<int:country_id>/` | `get_states_by_country` | ❌ No | ✅ **Mejorado** | `is_active=True`, validación, **rate limiting**, **caché** | AJAX - Estados por país |
| `/locations/ajax/cities/<int:state_id>/` | `get_cities_by_state` | ❌ No | ✅ **Mejorado** | `is_active=True`, validación, **rate limiting**, **caché** | AJAX - Ciudades por estado |
| `/locations/api/countries/` | `countries_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, búsqueda, **rate limiting**, **caché** | API - Países |
| `/locations/api/states/` | `states_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, filtrado, **rate limiting**, **caché** | API - Estados |
| `/locations/api/cities/` | `cities_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, filtrado, **rate limiting**, **caché** | API - Ciudades |
| `/locations/api/seasons/` | `seasons_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, **rate limiting**, **caché** | API - Temporadas |
| `/locations/api/rules/` | `rules_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, **rate limiting**, **caché** | API - Reglas |
| `/locations/api/sites/` | `sites_api` | ❌ No | ✅ **Mejorado** | `is_active=True`, filtrado, **rate limiting**, **caché** | API - Sitios |

**Análisis de Seguridad:**
- ✅ Solo devuelven datos con `is_active=True`
- ✅ No exponen información sensible
- ✅ Filtran por parámetros GET de forma segura
- ✅ Usan `JsonResponse` correctamente
- ✅ Validación de tipos de parámetros (int)
- ✅ **Rate limiting implementado:** 150 requests/hora por IP
- ✅ **Caché implementado:** 30 minutos para todas las respuestas
- ✅ **Validación de tamaño:** Parámetros de búsqueda limitados a 100 caracteres
- ✅ **Headers informativos:** `X-RateLimit-Remaining` y `X-RateLimit-Limit`

**Protecciones Implementadas:**
1. ✅ **Rate Limiting:** 150 requests por hora por IP (más permisivo que Instagram)
2. ✅ **Caché:** 30 minutos para reducir carga en base de datos
3. ✅ **Validación de Parámetros:** IDs validados como enteros, búsquedas limitadas
4. ✅ **Headers de Rate Limit:** Información sobre límites en respuestas

**Recomendaciones:**
- ✅ Ya implementado correctamente
- 💡 Considerar logging de requests sospechosos (opcional)

---

### 5. 📸 APIs de Instagram

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/accounts/api/instagram/posts/` | `instagram_posts_api` | ❌ No | ✅ **Mejorado** | Rate limiting, validación, caché | API pública de Instagram |
| `/accounts/api/instagram/image-proxy/` | `instagram_image_proxy` | ❌ No | ✅ **Mejorado** | Rate limiting, validación URLs, caché | Proxy de imágenes |

**Análisis de Seguridad:**

#### `/accounts/api/instagram/posts/`
- ✅ **Rate limiting:** 100 requests/hora por IP
- ✅ **Validación de parámetros:** `limit` entre 1-12, validación de tipos
- ✅ **Caché:** 15 minutos para respuestas
- ✅ **Headers informativos:** `X-RateLimit-Remaining`, `X-RateLimit-Limit`
- ✅ **Manejo de errores:** Retorna lista vacía en caso de error

#### `/accounts/api/instagram/image-proxy/`
- ✅ **Rate limiting:** 200 requests/hora por IP
- ✅ **Validación de URLs:** Solo permite dominios de Instagram
- ✅ **Validación de dominios:** `instagram.com`, `cdninstagram.com`, `fbcdn.net`, `scontent`
- ✅ **Protección contra hotlinking:** Validación de referer (advertencia, no bloqueo)
- ✅ **Caché:** 1 hora para imágenes
- ✅ **Validación de tamaño:** Máximo 10MB por imagen
- ✅ **Validación de content-type:** Solo imágenes permitidas
- ✅ **Manejo de timeouts:** Respuesta 504 en caso de timeout
- ✅ **Headers informativos:** `X-RateLimit-Remaining`, `X-RateLimit-Limit`

**Recomendaciones:**
- ✅ Ya implementado correctamente
- 💡 Considerar logging de requests sospechosos
- 💡 Considerar métricas de uso

---

### 6. 🌐 Internacionalización

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `/i18n/setlang/` | `set_language` | ❌ No | ✅ **Seguro** | Validación de idiomas permitidos | Cambio de idioma |
| `/jsi18n/` | `CachedJavaScriptCatalog` | ❌ No | ✅ **Seguro** | Caché implementado (1 hora) | Catálogo JS i18n |

**Análisis de Seguridad:**
- ✅ Validación de idiomas permitidos (solo idiomas configurados)
- ✅ Caché implementado en JavaScriptCatalog (1 hora)
- ✅ Validación de parámetros GET
- ✅ Protección CSRF (para POST en setlang)

**Recomendaciones:**
- ✅ Ya implementado correctamente

---

### 7. 🎯 Páginas de Error

| URL | Vista | Requiere Auth | Estado | Protecciones | Notas |
|-----|-------|---------------|--------|--------------|-------|
| `404.html` | `handler404` | ❌ No | ✅ **Implementado** | Template personalizado | Página no encontrada |
| `403.html` | `PermissionDenied` | ❌ No | ✅ **Implementado** | Template personalizado | Acceso denegado |

**Análisis de Seguridad:**
- ✅ Templates personalizados con diseño consistente
- ✅ Enlaces a páginas principales
- ✅ Responsive design
- ✅ Mensajes informativos

**Recomendaciones:**
- ✅ Ya implementado correctamente

---

## 🔒 Problemas de Seguridad Identificados

### 🔴 Prioridad Alta

#### 1. APIs de Ubicaciones sin Rate Limiting

**Problema:** Las 8 APIs de ubicaciones no tienen rate limiting, lo que permite:
- Abuso de recursos del servidor
- Posibles ataques de denegación de servicio (DoS)
- Consumo excesivo de ancho de banda

**Impacto:** Alto - Puede afectar disponibilidad del servicio

**Solución Recomendada:**
```python
# Implementar función de rate limiting reutilizable
def _check_rate_limit(request, cache_key_prefix, max_requests=100, window_seconds=3600):
    # Ya implementada en views_public.py
    # Aplicar a todas las APIs de ubicaciones
```

**URLs Afectadas:**
- `/locations/ajax/states/<int:country_id>/`
- `/locations/ajax/cities/<int:state_id>/`
- `/locations/api/countries/`
- `/locations/api/states/`
- `/locations/api/cities/`
- `/locations/api/seasons/`
- `/locations/api/rules/`
- `/locations/api/sites/`

---

### 🟡 Prioridad Media

#### 2. Falta de Caché en APIs de Ubicaciones

**Problema:** Cada request ejecuta queries a la base de datos sin caché.

**Impacto:** Medio - Afecta rendimiento pero no seguridad

**Solución Recomendada:**
```python
from django.core.cache import cache

cache_key = f"locations_api_countries_{search_query}"
cached_data = cache.get(cache_key)
if cached_data:
    return JsonResponse(cached_data, safe=False)
# ... procesar y guardar en caché
cache.set(cache_key, data, 900)  # 15 minutos
```

#### 3. Validación de Tamaño de Parámetros

**Problema:** No se valida el tamaño de parámetros GET, permitiendo posibles ataques de buffer overflow.

**Impacto:** Bajo - Django maneja esto automáticamente, pero es buena práctica

**Solución Recomendada:**
```python
search_query = request.GET.get("q", "").strip()
if len(search_query) > 100:  # Limitar tamaño
    search_query = search_query[:100]
```

---

### 🟢 Prioridad Baja

#### 4. Logging de Requests Sospechosos

**Problema:** No se registran requests que exceden límites o tienen patrones anómalos.

**Impacto:** Bajo - Útil para monitoreo pero no crítico

**Solución Recomendada:**
```python
import logging
logger = logging.getLogger('security')

if not is_allowed:
    logger.warning(f"Rate limit exceeded for IP: {ip_address}")
```

---

## 🛡️ Protecciones Implementadas

### ✅ Implementado Correctamente

1. **CSRF Protection**
   - ✅ Todas las formas usan CSRF tokens
   - ✅ APIs públicas no requieren CSRF (solo GET)

2. **Filtrado de Datos**
   - ✅ Solo datos activos (`is_active=True`)
   - ✅ Solo eventos publicados (`status="published"`)
   - ✅ Solo jugadores activos

3. **Validación de Usuarios**
   - ✅ Login bloquea jugadores
   - ✅ Registro valida tipos de usuario
   - ✅ Validación de contraseñas seguras

4. **Rate Limiting (Parcial)**
   - ✅ APIs de Instagram: 100-200 requests/hora
   - ⚠️ APIs de ubicaciones: Pendiente

5. **Caché (Parcial)**
   - ✅ APIs de Instagram: 15 minutos - 1 hora
   - ✅ JavaScriptCatalog: 1 hora
   - ⚠️ APIs de ubicaciones: Pendiente

6. **Páginas de Error**
   - ✅ 404 personalizada
   - ✅ 403 personalizada

7. **Validación de Parámetros**
   - ✅ Validación de tipos (int, string)
   - ✅ Validación de rangos (limit 1-12)
   - ✅ Validación de URLs (dominios permitidos)
   - ✅ Validación de content-type (solo imágenes)

---

## 📝 Plan de Acción Recomendado

### Fase 1: Crítico (Implementar Inmediatamente)

1. **Rate Limiting en APIs de Ubicaciones**
   - Aplicar función `_check_rate_limit()` a todas las APIs
   - Límite: 100-200 requests/hora por IP
   - Tiempo estimado: 2-3 horas

### Fase 2: Importante (Próximas 2 Semanas)

2. **Caché en APIs de Ubicaciones**
   - Implementar caché de 15-30 minutos
   - Usar claves basadas en parámetros
   - Tiempo estimado: 3-4 horas

3. **Validación de Tamaño de Parámetros**
   - Limitar tamaño de búsquedas
   - Validar tamaño de IDs
   - Tiempo estimado: 1-2 horas

### Fase 3: Mejoras (Próximo Mes)

4. **Logging de Seguridad**
   - Registrar requests sospechosos
   - Alertas para patrones anómalos
   - Tiempo estimado: 4-5 horas

5. **Métricas y Monitoreo**
   - Dashboard de uso de APIs
   - Tracking de rate limits
   - Tiempo estimado: 6-8 horas

---

## ✅ Checklist de Seguridad Actualizado

### URLs Públicas
- [x] URLs públicas no exponen información sensible
- [x] Filtrado correcto de datos activos
- [x] Validación de existencia (404 si no existe)
- [x] Paginación en listas públicas

### Autenticación
- [x] CSRF protection en formularios
- [x] Validación de usuarios en login/registro
- [x] Bloqueo de jugadores en login
- [x] Validación de contraseñas seguras
- [x] Rate limiting en login (prevenir fuerza bruta)
- [x] Bloqueo temporal por intentos fallidos consecutivos

### APIs Públicas
- [x] Rate limiting en APIs de Instagram
- [x] Rate limiting en APIs de ubicaciones
- [x] Caché en APIs de Instagram
- [x] Caché en APIs de ubicaciones
- [x] Validación de parámetros en APIs de Instagram
- [x] Validación de URLs en image-proxy
- [x] Validación de tamaño de parámetros
- [x] Headers de rate limit en todas las APIs

### Protección de Datos
- [x] Solo datos activos expuestos
- [x] Solo eventos publicados
- [x] Validación de dominios permitidos
- [x] Validación de content-type

### Páginas de Error
- [x] Página 404 personalizada
- [x] Página 403 personalizada
- [x] Handler 404 configurado

### Monitoreo
- [ ] Logging de requests sospechosos
- [ ] Métricas de uso de APIs
- [ ] Alertas para patrones anómalos

---

## 📊 Estadísticas de Seguridad

### Por Categoría

| Categoría | Total | Seguras | Mejorables | Mejoradas |
|-----------|-------|---------|------------|-----------|
| Home/Navegación | 5 | 5 (100%) | 0 | 0 |
| Autenticación | 2 | 2 (100%) | 0 | 0 |
| Eventos | 2 | 2 (100%) | 0 | 0 |
| APIs Ubicaciones | 8 | 0 | 8 (100%) | 0 |
| APIs Instagram | 2 | 0 | 0 | 2 (100%) |
| Internacionalización | 2 | 2 (100%) | 0 | 0 |
| Páginas Error | 2 | 2 (100%) | 0 | 0 |
| **TOTAL** | **25** | **13 (52%)** | **0 (0%)** | **12 (48%)** |

### Por Prioridad de Mejora

- ✅ **Completado:** 8 URLs (APIs de ubicaciones - rate limiting y caché)
- 🟢 **Opcional:** 1 URL (Logging de seguridad)

---

## 🔍 URLs Detalladas con Estado

### ✅ Completamente Seguras (13 URLs)

1. `/` - Home público
2. `/teams/` - Lista de equipos
3. `/players/` - Lista de jugadores
4. `/players/<int:pk>/` - Perfil jugador (ID)
5. `/players/<slug:slug>/` - Perfil jugador (slug)
6. `/accounts/login/` - Login
7. `/accounts/register/` - Registro
8. `/events/` - Lista de eventos
9. `/events/<int:pk>/` - Detalle de evento
10. `/i18n/setlang/` - Cambio de idioma
11. `/jsi18n/` - Catálogo JS i18n
12. `404.html` - Página no encontrada
13. `403.html` - Acceso denegado

### ✅ Recientemente Mejoradas (11 URLs)

14. `/accounts/login/` - Login con rate limiting
15. `/accounts/api/instagram/posts/` - API Instagram posts
16. `/accounts/api/instagram/image-proxy/` - Proxy imágenes Instagram
17-24. APIs de ubicaciones (ver sección siguiente)

### ✅ Recientemente Mejoradas - APIs de Ubicaciones (8 URLs)

17. `/locations/ajax/states/<int:country_id>/` - Estados AJAX
18. `/locations/ajax/cities/<int:state_id>/` - Ciudades AJAX
19. `/locations/api/countries/` - API Países
20. `/locations/api/states/` - API Estados
21. `/locations/api/cities/` - API Ciudades
22. `/locations/api/seasons/` - API Temporadas
23. `/locations/api/rules/` - API Reglas
24. `/locations/api/sites/` - API Sitios

---

## 🎯 Resumen Final

**Estado General:** ✅ **Excelente** - Todas las mejoras críticas implementadas

**Fortalezas:**
- ✅ La mayoría de URLs públicas están bien protegidas
- ✅ Filtrado correcto de datos sensibles
- ✅ APIs de Instagram recientemente mejoradas
- ✅ **Login con rate limiting implementado (protección contra fuerza bruta)**
- ✅ Páginas de error personalizadas

**Áreas de Mejora:**
- 💡 Logging de seguridad (opcional)
- 💡 Métricas y monitoreo de APIs (opcional)

**Próximos Pasos:**
1. ✅ ~~Implementar rate limiting en APIs de ubicaciones~~ **COMPLETADO**
2. ✅ ~~Implementar caché en APIs de ubicaciones~~ **COMPLETADO**
3. Implementar logging de seguridad (opcional)
4. Considerar CAPTCHA opcional después de X intentos fallidos (opcional)

---

**Última actualización:** 2026-01-07
