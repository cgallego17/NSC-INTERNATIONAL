# Sistema de Permisos y Acceso Denegado

Este documento explica cómo funciona el sistema de permisos y qué sucede cuando un usuario no tiene acceso a una URL.

## 📋 Cómo Funciona el Sistema de Permisos

### 1. **Mixins de Permisos**

El sistema usa mixins en `apps/core/mixins.py` que verifican permisos antes de permitir el acceso:

#### **StaffRequiredMixin**
- **Qué hace:** Verifica si el usuario es `staff` o `superuser`
- **Si no tiene acceso:** Redirige al panel (`/panel/`) con un mensaje de error
- **Mensaje:** "No tienes permisos para acceder a esta sección. Se requieren permisos de administrador."

#### **SuperuserRequiredMixin**
- **Qué hace:** Verifica si el usuario es `superuser` (solo admin)
- **Si no tiene acceso:** Redirige al panel (`/panel/`) con un mensaje de error
- **Mensaje:** "Solo los administradores pueden acceder a esta sección."

#### **ManagerRequiredMixin**
- **Qué hace:** Verifica si el usuario es manager de equipo
- **Si no tiene acceso:** Redirige al panel con mensaje de error
- **Mensaje:** "Solo los managers de equipo pueden acceder a esta sección."

#### **OwnerOrStaffRequiredMixin**
- **Qué hace:** Verifica si el usuario es el dueño del objeto o es staff
- **Si no tiene acceso:** Redirige al panel con mensaje de error
- **Mensaje:** "No tienes permisos para acceder a este recurso."

### 2. **Verificación Manual con PermissionDenied**

Algunas vistas (como `PlayerDetailView`) verifican permisos manualmente y lanzan `PermissionDenied`:

```python
from django.core.exceptions import PermissionDenied

if not (is_staff or is_manager or is_parent or is_owner):
    raise PermissionDenied(_("No tienes permisos para ver este jugador."))
```

**Qué sucede:** Django busca automáticamente una plantilla `403.html` en el directorio `templates/` y la muestra al usuario.

## 🎨 Plantilla 403.html

He creado una plantilla personalizada `templates/403.html` que se muestra cuando se lanza `PermissionDenied`.

### Características:
- ✅ Diseño moderno y profesional
- ✅ Muestra el mensaje de error personalizado
- ✅ Botones para volver al panel o volver atrás
- ✅ Responsive (se adapta a móviles)
- ✅ Soporte para múltiples idiomas (i18n)

### Ubicación:
```
templates/403.html
```

## 🔄 Flujo de Acceso Denegado

### Caso 1: Usando Mixins (Redirección)
```
Usuario sin permisos → Mixin detecta → Redirige a /panel/ → Muestra mensaje de error
```

**Ejemplo:**
- Usuario intenta acceder a `/accounts/users/`
- `SuperuserRequiredMixin` detecta que no es superuser
- Redirige a `/panel/`
- Muestra mensaje: "Solo los administradores pueden acceder a esta sección."

### Caso 2: PermissionDenied (Página 403)
```
Usuario sin permisos → Vista lanza PermissionDenied → Django muestra 403.html
```

**Ejemplo:**
- Usuario intenta acceder a `/accounts/players/123/`
- `PlayerDetailView` verifica permisos
- No tiene permisos → Lanza `PermissionDenied`
- Django muestra `templates/403.html` con el mensaje personalizado

## 📝 Mensajes de Error por Tipo

| Tipo de Acceso | Mixin | Mensaje |
|----------------|-------|---------|
| **Solo Staff** | `StaffRequiredMixin` | "No tienes permisos para acceder a esta sección. Se requieren permisos de administrador." |
| **Solo Admin** | `SuperuserRequiredMixin` | "Solo los administradores pueden acceder a esta sección." |
| **Solo Manager** | `ManagerRequiredMixin` | "Solo los managers de equipo pueden acceder a esta sección." |
| **Owner o Staff** | `OwnerOrStaffRequiredMixin` | "No tienes permisos para acceder a este recurso." |
| **PermissionDenied** | Manual | Muestra el mensaje pasado a `PermissionDenied()` |

## 🎯 Dónde se Muestran los Mensajes

### 1. **Mensajes de Django (messages framework)**
Los mixins usan `messages.error()` que se muestran en:
- El panel del usuario (`/panel/`)
- Cualquier página que use `{% if messages %}` en el template

### 2. **Plantilla 403.html**
Se muestra cuando:
- Una vista lanza `PermissionDenied`
- Django detecta automáticamente la plantilla `403.html`

## 🔧 Personalización

### Cambiar Mensajes de Error

Edita los mixins en `apps/core/mixins.py`:

```python
messages.error(
    request,
    "Tu mensaje personalizado aquí",
)
```

### Personalizar Plantilla 403

Edita `templates/403.html` para cambiar:
- Colores y estilos
- Mensajes
- Botones y acciones
- Layout

### Agregar Más Verificaciones

Puedes crear nuevos mixins o agregar verificaciones manuales en las vistas:

```python
def dispatch(self, request, *args, **kwargs):
    if not self.tiene_permiso(request):
        raise PermissionDenied("Mensaje personalizado")
    return super().dispatch(request, *args, **kwargs)
```

## 📊 Resumen

| Método | Cuándo se Usa | Dónde se Muestra |
|--------|---------------|------------------|
| **Mixins con redirect** | Mayoría de vistas | Panel con mensaje de error |
| **PermissionDenied** | Verificaciones complejas | Plantilla 403.html |

## ✅ Ventajas del Sistema Actual

1. **Consistencia:** Todos los mixins usan el mismo patrón
2. **UX Mejorada:** Los usuarios son redirigidos a un lugar seguro (panel)
3. **Mensajes Claros:** Cada tipo de error tiene su mensaje específico
4. **Flexibilidad:** Puedes usar `PermissionDenied` para casos especiales
5. **Plantilla Personalizada:** 403.html es moderna y profesional

---

**Última actualización:** 2026-01-07



