# Mejoras Implementadas en APIs de Instagram

**Fecha:** 2026-01-07

---

## 📋 Resumen

Se han implementado mejoras de seguridad y rendimiento en las APIs públicas de Instagram:

1. **Rate Limiting** - Limita el número de requests por IP
2. **Validación de Parámetros** - Valida y sanitiza parámetros de entrada
3. **Caché** - Almacena respuestas para mejorar rendimiento

---

## 🔒 API: `/accounts/api/instagram/posts/`

### Mejoras Implementadas

#### 1. Rate Limiting
- **Límite:** 100 requests por hora por IP
- **Implementación:** Usando caché de Django
- **Headers de respuesta:**
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Limit`: Límite total (100)
- **Respuesta cuando se excede:** HTTP 429 con mensaje de error

#### 2. Validación de Parámetros
- **Parámetro `limit`:**
  - Validado como entero
  - Rango permitido: 1-12
  - Valor por defecto: 6
  - Si es inválido, usa el valor por defecto

#### 3. Caché
- **Duración:** 15 minutos (900 segundos)
- **Clave:** `instagram_posts_api_{limit}`
- **Beneficio:** Reduce carga en el servidor y mejora tiempos de respuesta

### Código de Ejemplo

```python
# Rate limiting automático
# Validación de parámetros
limit = request.GET.get("limit", "6")
limit = max(1, min(12, int(limit)))  # Entre 1 y 12

# Caché automático
cache_key = f"instagram_posts_api_{limit}"
cached_posts = cache.get(cache_key)
if cached_posts:
    return JsonResponse(cached_posts, safe=False)
```

---

## 🖼️ API: `/accounts/api/instagram/image-proxy/`

### Mejoras Implementadas

#### 1. Rate Limiting
- **Límite:** 200 requests por hora por IP (más permisivo para imágenes)
- **Implementación:** Usando caché de Django
- **Headers de respuesta:**
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Limit`: Límite total (200)
- **Respuesta cuando se excede:** HTTP 429 con mensaje de error

#### 2. Validación de URLs
- **Dominios permitidos:**
  - `instagram.com`
  - `cdninstagram.com`
  - `fbcdn.net`
  - `scontent` (cualquier subdominio)
  - `scontent.cdninstagram.com`
- **Validación de formato:** Verifica que sea una URL válida
- **Respuesta cuando es inválida:** HTTP 400 o 403 según el caso

#### 3. Protección contra Hotlinking
- **Validación de Referer:** Verifica el header `Referer`
- **Comportamiento:** Registra advertencia si el referer no es de nuestro dominio
- **No bloquea:** Solo registra para monitoreo

#### 4. Validación de Contenido
- **Content-Type:** Solo permite imágenes (`image/*`)
- **Tamaño máximo:** 10MB por imagen
- **Respuestas de error:**
  - HTTP 400: No es una imagen
  - HTTP 413: Imagen demasiado grande

#### 5. Caché
- **Duración:** 1 hora (3600 segundos)
- **Clave:** Hash MD5 de la URL de la imagen
- **Beneficio:** Reduce ancho de banda y mejora tiempos de respuesta

### Código de Ejemplo

```python
# Validación de dominio
allowed_domains = [
    'instagram.com',
    'cdninstagram.com',
    'fbcdn.net',
    'scontent',
    'scontent.cdninstagram.com',
]

domain_valid = any(
    allowed_domain in parsed_url.netloc.lower()
    for allowed_domain in allowed_domains
)

# Validación de tamaño
if len(content) > 10 * 1024 * 1024:  # 10MB
    return HttpResponse("Image too large", status=413)
```

---

## 🛡️ Función de Rate Limiting

Se creó una función reutilizable `_check_rate_limit()`:

```python
def _check_rate_limit(request, cache_key_prefix, max_requests=100, window_seconds=3600):
    """
    Verifica rate limiting usando caché de Django.

    Args:
        request: HttpRequest object
        cache_key_prefix: Prefijo para la clave de caché
        max_requests: Número máximo de requests permitidos
        window_seconds: Ventana de tiempo en segundos

    Returns:
        tuple: (is_allowed, remaining_requests)
    """
```

### Características:
- Usa IP del cliente (soporta `X-Forwarded-For` para proxies)
- Almacena contador en caché de Django
- Retorna si está permitido y requests restantes
- Configurable por endpoint

---

## 📊 Métricas y Monitoreo

### Headers de Respuesta

Ambas APIs incluyen headers de rate limiting:

```
X-RateLimit-Remaining: 95
X-RateLimit-Limit: 100
```

### Códigos de Estado HTTP

- **200:** Request exitoso
- **400:** Parámetros inválidos o URL inválida
- **403:** URL no permitida (dominio no válido)
- **413:** Imagen demasiado grande
- **429:** Rate limit excedido
- **500:** Error interno del servidor
- **502:** Error al obtener imagen de Instagram
- **504:** Timeout al obtener imagen

---

## ✅ Checklist de Seguridad

- [x] Rate limiting implementado
- [x] Validación de parámetros
- [x] Validación de URLs
- [x] Validación de dominios permitidos
- [x] Validación de content-type
- [x] Validación de tamaño de archivo
- [x] Caché implementado
- [x] Headers de rate limit en respuestas
- [x] Manejo de errores mejorado
- [x] Logging de advertencias

---

## 🔄 Próximas Mejoras Recomendadas

1. **Logging de Requests Sospechosos**
   - Registrar IPs que exceden límites frecuentemente
   - Alertas automáticas para patrones anómalos

2. **Rate Limiting por Usuario Autenticado**
   - Límites más altos para usuarios autenticados
   - Tracking por usuario además de IP

3. **Caché Distribuido**
   - Usar Redis para caché en producción
   - Mejor rendimiento en múltiples servidores

4. **Métricas y Analytics**
   - Tracking de uso de APIs
   - Dashboard de monitoreo

---

**Última actualización:** 2026-01-07



