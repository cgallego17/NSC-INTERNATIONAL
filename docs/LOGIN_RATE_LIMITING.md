# Sistema de Rate Limiting para Login

Este documento explica el sistema de protección contra ataques de fuerza bruta implementado en el login.

**Fecha de implementación:** 2026-01-07

---

## 🛡️ Protecciones Implementadas

### 1. Rate Limiting General

**Límite:** 10 intentos de login por hora por IP

- Cada intento de login (exitoso o fallido) cuenta hacia el límite
- El contador se resetea después de 1 hora
- Si se excede el límite, se bloquea el acceso temporalmente

### 2. Bloqueo por Intentos Fallidos Consecutivos

**Límite:** 5 intentos fallidos consecutivos

- Después de 5 intentos fallidos consecutivos, el IP se bloquea por 15 minutos
- El bloqueo se aplica automáticamente
- El contador de intentos fallidos se resetea después del bloqueo o en login exitoso

### 3. Tracking por IP

- Se rastrea la IP del cliente (considerando proxies con `X-Forwarded-For`)
- Cada IP tiene sus propios contadores independientes
- Los contadores se almacenan en caché de Django

---

## 🔧 Funcionamiento Técnico

### Funciones Implementadas

#### `_get_client_ip(request)`
Obtiene la IP real del cliente, considerando proxies y headers `X-Forwarded-For`.

#### `_check_login_rate_limit(request)`
Verifica si el IP puede realizar un intento de login.

**Retorna:**
- `is_allowed`: Si se permite el intento
- `remaining_attempts`: Intentos restantes en la hora
- `is_blocked`: Si el IP está bloqueado
- `block_seconds_remaining`: Segundos restantes del bloqueo

#### `_increment_login_attempts(request, is_successful=False)`
Incrementa los contadores de intentos.

**Comportamiento:**
- Si `is_successful=True`: Limpia contadores de intentos fallidos
- Si `is_successful=False`: Incrementa contadores y aplica bloqueo si es necesario

---

## 📊 Flujo de Protección

### 1. Usuario Intenta Login

```
Usuario → dispatch() → Verificar rate limit
```

**En `dispatch()`:**
- Verifica si el IP está bloqueado
- Verifica si se excedió el límite de 10 intentos/hora
- Si está bloqueado o excedido, redirige con mensaje de error

### 2. Login Exitoso

```
form_valid() → _increment_login_attempts(success=True) → Limpiar contadores fallidos
```

**Acciones:**
- Limpia contadores de intentos fallidos consecutivos
- Mantiene el rate limit general (para prevenir abuso)

### 3. Login Fallido

```
form_invalid() → _increment_login_attempts(success=False) → Verificar bloqueo
```

**Acciones:**
- Incrementa contador de intentos por hora
- Incrementa contador de intentos fallidos consecutivos
- Si alcanza 5 fallidos consecutivos, aplica bloqueo de 15 minutos
- Verifica si ahora está bloqueado y muestra mensaje apropiado

---

## ⚙️ Configuración

### Parámetros Ajustables

```python
# En _check_login_rate_limit() y _increment_login_attempts()

MAX_ATTEMPTS_PER_HOUR = 10  # Máximo 10 intentos por hora
MAX_FAILED_ATTEMPTS = 5     # Máximo 5 intentos fallidos consecutivos
BLOCK_DURATION = 900        # Bloqueo de 15 minutos (900 segundos)
RATE_LIMIT_WINDOW = 3600    # Ventana de rate limit: 1 hora
```

### Claves de Caché

- `login_rate_limit_{ip}`: Contador de intentos por hora
- `login_failed_attempts_{ip}`: Contador de intentos fallidos consecutivos
- `login_blocked_{ip}`: Timestamp de cuando expira el bloqueo

---

## 🚨 Mensajes de Error

### Bloqueo por Intentos Fallidos

```
"Too many failed login attempts. Your IP has been temporarily blocked.
Please try again in X minutes."
```

### Rate Limit Excedido

```
"Too many login attempts. Please try again later. (Remaining attempts: X)"
```

### Bloqueo Detectado en dispatch()

```
"Too many failed login attempts. Please try again in X minutes."
```

---

## 📈 Ejemplo de Uso

### Escenario 1: Usuario Normal

1. Usuario intenta login con credenciales incorrectas (1-4 veces)
   - ✅ Se permite el intento
   - ⚠️ Mensaje de error genérico
   - 📊 Contador de fallidos: 1-4

2. Usuario intenta login con credenciales correctas (5to intento)
   - ✅ Login exitoso
   - ✅ Contadores de fallidos se limpian
   - ✅ Usuario accede al sistema

### Escenario 2: Ataque de Fuerza Bruta

1. Atacante intenta login 5 veces con credenciales incorrectas
   - ✅ Intentos 1-4: Se permiten con mensaje de error
   - 🚫 Intento 5: Se bloquea el IP por 15 minutos
   - 📊 Contador de fallidos: 5 → Bloqueo activado

2. Atacante intenta login durante el bloqueo
   - 🚫 Se rechaza inmediatamente
   - ⚠️ Mensaje: "Too many failed login attempts. Please try again in X minutes."

3. Después de 15 minutos
   - ✅ Bloqueo expira automáticamente
   - ✅ Contadores se limpian
   - ✅ Puede intentar de nuevo

### Escenario 3: Rate Limit General

1. Usuario/Atacante intenta login 10 veces en una hora
   - ✅ Intentos 1-9: Se permiten
   - 🚫 Intento 10: Se bloquea por rate limit
   - ⚠️ Mensaje: "Too many login attempts. Please try again later."

2. Después de 1 hora
   - ✅ Rate limit se resetea
   - ✅ Puede intentar de nuevo

---

## 🔍 Monitoreo y Logging

### Información Registrada

Actualmente el sistema:
- ✅ Muestra mensajes al usuario sobre bloqueos
- ✅ Almacena información en caché para tracking
- ⚠️ No registra en logs (se puede agregar)

### Recomendaciones de Logging

```python
import logging
logger = logging.getLogger('security')

# En _increment_login_attempts cuando se bloquea
if failed_attempts >= MAX_FAILED_ATTEMPTS:
    logger.warning(
        f"IP {ip_address} blocked for {BLOCK_DURATION}s after "
        f"{failed_attempts} failed login attempts"
    )

# En dispatch cuando se detecta bloqueo
if is_blocked:
    logger.warning(
        f"Blocked IP {ip_address} attempted login. "
        f"Block expires in {seconds_remaining}s"
    )
```

---

## ✅ Ventajas del Sistema

1. **Protección Efectiva**
   - Previene ataques de fuerza bruta
   - Bloqueo automático sin intervención manual

2. **Experiencia de Usuario**
   - Mensajes informativos
   - No bloquea usuarios legítimos con uso normal

3. **Flexibilidad**
   - Parámetros fácilmente ajustables
   - Limpieza automática de contadores

4. **Rendimiento**
   - Usa caché de Django (rápido)
   - No requiere base de datos adicional

---

## ⚠️ Limitaciones y Consideraciones

### 1. IPs Compartidas

**Problema:** Varios usuarios detrás de la misma IP (NAT, proxy) comparten contadores.

**Solución:** Los límites son generosos (10/hora, 5 fallidos) para no afectar usuarios legítimos.

### 2. IPs Dinámicas

**Problema:** Usuarios con IPs que cambian pueden evitar bloqueos.

**Solución:** El rate limiting general (10/hora) aún protege contra abuso.

### 3. VPNs y Proxies

**Problema:** Atacantes pueden usar VPNs para cambiar IPs.

**Solución:** Considerar implementar bloqueo por email/usuario además de IP (futuro).

---

## 🔄 Mejoras Futuras Recomendadas

### Prioridad Media

1. **Bloqueo por Email/Usuario**
   - Rastrear intentos fallidos por email además de IP
   - Bloquear cuenta después de X intentos fallidos

2. **CAPTCHA Después de 3 Intentos**
   - Mostrar CAPTCHA después de 3 intentos fallidos
   - Agregar capa adicional de protección

3. **Logging de Seguridad**
   - Registrar todos los bloqueos
   - Alertas para patrones anómalos

### Prioridad Baja

4. **Whitelist de IPs**
   - Permitir IPs confiables (oficinas, admins)
   - Límites más altos para IPs whitelisted

5. **Notificaciones de Bloqueo**
   - Email al usuario cuando su cuenta es bloqueada
   - Notificación a admins de bloqueos sospechosos

---

## 📝 Resumen

**Estado:** ✅ **Implementado y Funcional**

**Protecciones:**
- ✅ Rate limiting: 10 intentos/hora por IP
- ✅ Bloqueo temporal: 15 minutos después de 5 fallidos
- ✅ Tracking por IP con soporte para proxies
- ✅ Limpieza automática de contadores

**Configuración Actual:**
- Máximo 10 intentos por hora
- Bloqueo de 15 minutos después de 5 fallidos
- Mensajes informativos al usuario

**Próximos Pasos:**
- Considerar bloqueo por email/usuario
- Implementar logging de seguridad
- Considerar CAPTCHA opcional

---

**Última actualización:** 2026-01-07



