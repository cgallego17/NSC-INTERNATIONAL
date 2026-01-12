# 🔒 AUDITORÍA DE SEGURIDAD - FORMULARIO DE REGISTRO PÚBLICO

**Fecha:** 2026-01-09
**Sistema:** NSC International - Formulario de Registro Público
**Nivel de Riesgo Actual:** MEDIO-ALTO ⚠️

---

## ✅ MEDIDAS DE SEGURIDAD ACTUALES (Implementadas)

### 1. **Protección CSRF** ✓
- **Estado:** IMPLEMENTADO
- **Ubicación:** `templates/accounts/public_register.html` (línea 1826, 2427)
- **Descripción:** Token CSRF presente en formularios
```django
{% csrf_token %}
```

### 2. **Validación de Contraseñas Robusta** ✓
- **Estado:** IMPLEMENTADO
- **Ubicación:** `apps/accounts/forms.py` (línea 466-523)
- **Requisitos:**
  - Mínimo 8 caracteres
  - Al menos 1 mayúscula
  - Al menos 1 minúscula
  - Al menos 1 número
  - Al menos 1 carácter especial
  - No similar al email, nombre o apellido

### 3. **Validación de Email Único** ✓
- **Estado:** IMPLEMENTADO
- **Ubicación:** `apps/accounts/forms.py` (línea 436-443)
- **Descripción:** Previene registros duplicados

### 4. **Sanitización de Inputs** ✓
- **Estado:** IMPLEMENTADO
- **Descripción:** Django ORM previene SQL Injection automáticamente
- **Validaciones:** `.strip()` en nombres y apellidos

### 5. **Rate Limiting en Login** ✓
- **Estado:** IMPLEMENTADO SOLO EN LOGIN
- **Ubicación:** `apps/accounts/views_public.py` (línea 412-500)
- **Configuración:**
  - Máximo 10 intentos por hora por IP
  - Bloqueo de 15 minutos después de 5 intentos fallidos

---

## ❌ VULNERABILIDADES Y RIESGOS IDENTIFICADOS

### 1. **SIN PROTECCIÓN CAPTCHA** ❌ CRÍTICO
- **Riesgo:** Registro masivo automatizado (bots)
- **Impacto:**
  - Spam de cuentas falsas
  - Consumo de recursos
  - Contaminación de base de datos
- **Recomendación:** Implementar reCAPTCHA v3 o hCaptcha

### 2. **SIN RATE LIMITING EN REGISTRO** ❌ ALTO
- **Riesgo:** Abuso del endpoint de registro
- **Impacto:**
  - Ataques DoS
  - Registro masivo automatizado
  - Saturación de emails
- **Recomendación:** Limitar registros por IP (ej: 3 por hora)

### 3. **VALIDACIÓN DE ARCHIVOS INSUFICIENTE** ❌ ALTO
- **Riesgo:** Carga de archivos maliciosos
- **Problemas Actuales:**
  - No se valida el tamaño máximo del archivo
  - No se valida el tipo MIME real (solo extensión)
  - No se escanea contenido malicioso
  - Falta validación de dimensiones de imagen
- **Recomendación:**
  - Validar tipo MIME real con `python-magic`
  - Limitar tamaño (max 5MB como indica la UI)
  - Validar dimensiones de imagen
  - Renombrar archivos para prevenir path traversal

### 4. **SIN VERIFICACIÓN DE EMAIL** ⚠️ MEDIO
- **Riesgo:** Cuentas con emails falsos o no verificados
- **Impacto:**
  - Dificultad de recuperación de cuenta
  - Emails temporales/desechables
- **Recomendación:** Implementar verificación de email por token

### 5. **INFORMACIÓN SENSIBLE EN ERRORES** ⚠️ MEDIO
- **Riesgo:** Enumeración de usuarios
- **Problema:** Los mensajes de error revelan si un email existe
- **Recomendación:** Usar mensajes genéricos

### 6. **SIN HONEYPOT ANTI-BOT** ⚠️ MEDIO
- **Riesgo:** Bots simples pueden completar el formulario
- **Recomendación:** Agregar campo honeypot invisible

### 7. **SIN LOGGING DE SEGURIDAD** ⚠️ MEDIO
- **Riesgo:** No se registran intentos sospechosos
- **Recomendación:** Log de:
  - Intentos de registro fallidos
  - IPs bloqueadas
  - Archivos rechazados

### 8. **SIN PROTECCIÓN CONTRA CLICKJACKING** ⚠️ BAJO
- **Riesgo:** Formulario puede ser embebido en iframe malicioso
- **Recomendación:** X-Frame-Options header

### 9. **SIN VALIDACIÓN DE TELÉFONO** ⚠️ BAJO
- **Riesgo:** Números de teléfono inválidos
- **Recomendación:** Validar formato internacional

### 10. **SIN LÍMITE DE INTENTOS DE REGISTRO POR EMAIL** ⚠️ BAJO
- **Riesgo:** Spam a una dirección de email específica
- **Recomendación:** Limitar intentos por email (ej: 3 por día)

---

## 🛡️ PLAN DE MEJORAS RECOMENDADO

### PRIORIDAD CRÍTICA (Implementar inmediatamente)

#### 1. reCAPTCHA v3 o hCaptcha
```python
# En forms.py
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class PublicRegistrationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3())
```

#### 2. Rate Limiting para Registro
```python
# En views_public.py
from django.core.cache import cache
from django.http import HttpResponseForbidden

class PublicRegistrationView(CreateView):
    def dispatch(self, request, *args, **kwargs):
        ip_address = self.get_client_ip(request)
        cache_key = f"register_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 3:  # Máximo 3 registros por hora
            return HttpResponseForbidden("Too many registration attempts. Please try again later.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        ip_address = self.get_client_ip(self.request)
        cache_key = f"register_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, 3600)  # 1 hora
        return super().form_valid(form)
```

#### 3. Validación Robusta de Archivos
```python
# En forms.py
import magic
from PIL import Image
from django.core.exceptions import ValidationError

def clean_profile_picture(self):
    file = self.cleaned_data.get('profile_picture')
    if not file:
        return file

    # Validar tamaño (5MB máximo)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("File size must not exceed 5MB.")

    # Validar tipo MIME real
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer

    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file_type not in allowed_types:
        raise ValidationError("Invalid file type. Only JPG, PNG, GIF, and WEBP are allowed.")

    # Validar que sea una imagen válida
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)

        # Validar dimensiones (opcional)
        if img.width > 4000 or img.height > 4000:
            raise ValidationError("Image dimensions too large. Maximum 4000x4000 pixels.")

    except Exception:
        raise ValidationError("Invalid or corrupted image file.")

    return file
```

### PRIORIDAD ALTA (Implementar en 1-2 semanas)

#### 4. Verificación de Email
```python
# Enviar email con token de verificación
# Bloquear acceso completo hasta verificar
# Token expira en 24 horas
```

#### 5. Honeypot Anti-Bot
```html
<!-- Campo oculto que los bots llenarán -->
<input type="text" name="website" style="display:none" tabindex="-1" autocomplete="off">
```

```python
# En forms.py
def clean(self):
    cleaned_data = super().clean()
    # Si el honeypot tiene valor, es un bot
    if cleaned_data.get('website'):
        raise ValidationError("Bot detected")
    return cleaned_data
```

#### 6. Logging de Seguridad
```python
import logging
logger = logging.getLogger('security')

# Log intentos sospechosos
logger.warning(f"Registration attempt blocked - IP: {ip_address}")
```

### PRIORIDAD MEDIA (Implementar en 1 mes)

#### 7. Headers de Seguridad
```python
# En settings.py
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True  # En producción
SESSION_COOKIE_SECURE = True  # En producción
CSRF_COOKIE_SECURE = True  # En producción
```

#### 8. Validación de Teléfono
```python
# Usar phonenumbers library
import phonenumbers

def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    prefix = self.cleaned_data.get('phone_prefix')
    try:
        parsed = phonenumbers.parse(prefix + phone)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError("Invalid phone number")
    except:
        raise ValidationError("Invalid phone number format")
    return phone
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Inmediato (Esta semana)
- [ ] Implementar reCAPTCHA v3
- [ ] Agregar rate limiting para registro
- [ ] Mejorar validación de archivos

### Corto Plazo (1-2 semanas)
- [ ] Implementar verificación de email
- [ ] Agregar honeypot anti-bot
- [ ] Configurar logging de seguridad
- [ ] Agregar headers de seguridad

### Mediano Plazo (1 mes)
- [ ] Validación robusta de teléfonos
- [ ] Implementar 2FA opcional
- [ ] Auditoría de logs automatizada
- [ ] Monitoreo de patrones sospechosos

### Largo Plazo (2-3 meses)
- [ ] Implementar WAF (Web Application Firewall)
- [ ] Penetration testing profesional
- [ ] Bug bounty program
- [ ] Certificación de seguridad

---

## 🔧 DEPENDENCIAS REQUERIDAS

```bash
# Para implementar las mejoras
pip install django-recaptcha==4.0.0
pip install python-magic==0.4.27
pip install phonenumbers==8.13.27
pip install Pillow==10.1.0
pip install django-ratelimit==4.1.0
```

---

## 📊 MATRIZ DE RIESGO

| Vulnerabilidad | Probabilidad | Impacto | Riesgo Total | Prioridad |
|----------------|-------------|---------|--------------|-----------|
| Sin CAPTCHA | ALTA | ALTO | CRÍTICO | 1 |
| Sin Rate Limiting | ALTA | ALTO | CRÍTICO | 1 |
| Validación de Archivos | MEDIA | ALTO | ALTO | 1 |
| Sin Verificación Email | ALTA | MEDIO | ALTO | 2 |
| Enumeración de Usuarios | MEDIA | MEDIO | MEDIO | 2 |
| Sin Honeypot | MEDIA | BAJO | MEDIO | 3 |
| Sin Logging | BAJA | MEDIO | MEDIO | 3 |

---

## 📝 NOTAS ADICIONALES

1. **Entorno de Producción:** Asegurarse de que `DEBUG = False`
2. **HTTPS:** Todo el sitio debe servirse sobre HTTPS
3. **Backups:** Implementar backups automáticos de la base de datos
4. **Monitoreo:** Configurar alertas para actividad sospechosa
5. **Actualizaciones:** Mantener Django y dependencias actualizadas

---

**Revisado por:** Sistema de Auditoría Automatizado
**Próxima revisión:** 2026-02-09
