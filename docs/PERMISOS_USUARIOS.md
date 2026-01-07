# Permisos y Roles de Usuarios

Este documento explica los permisos y capacidades de cada tipo de usuario en el sistema.

**Última actualización:** 2026-01-07

---

## 📋 Tipos de Usuario

El sistema tiene 4 tipos de usuarios definidos en `UserProfile`:

| Tipo | Código | Descripción | Puede Iniciar Sesión |
|------|--------|-------------|---------------------|
| **Jugador** | `player` | Jugador registrado | ❌ **NO** |
| **Padre/Acudiente** | `parent` | Padre o acudiente de jugador(es) | ✅ **SÍ** |
| **Manager de Equipo** | `team_manager` | Manager/entrenador de equipo | ✅ **SÍ** |
| **Administrador** | `admin` | Administrador del sistema | ✅ **SÍ** (si es staff/superuser) |

---

## 🔐 Permisos del Sistema Django

### Permisos Base de Django User

Todos los usuarios tienen estos campos de Django:

| Campo | Valor por Defecto | Descripción |
|-------|-------------------|-------------|
| `is_staff` | `False` | Acceso al Django Admin |
| `is_superuser` | `False` | Permisos completos del sistema |
| `is_active` | `True` | Cuenta activa (puede iniciar sesión) |

**⚠️ IMPORTANTE:** Los jugadores (`player`) tienen `is_active=False`, por lo que **NO pueden iniciar sesión**.

---

## 👤 Usuario Normal que se Registra

### Al Registrarse

Cuando un usuario se registra en `/accounts/register/`, puede elegir entre:

1. **Padre/Acudiente** (`parent`)
2. **Manager de Equipo** (`team_manager`)

**Nota:** Los jugadores NO se registran directamente. Son creados por padres o managers.

### Permisos por Defecto

Un usuario normal que se registra tiene:

```python
User:
  - is_staff = False
  - is_superuser = False
  - is_active = True  # Puede iniciar sesión

UserProfile:
  - user_type = "parent" o "team_manager" (según lo que elija)
  - is_active = True
```

---

## 🎯 Capacidades por Tipo de Usuario

### 1. 👨‍👩‍👧‍👦 Padre/Acudiente (`parent`)

**Permisos:**
- ✅ Iniciar sesión
- ✅ Ver su panel personal (`/panel/`)
- ✅ Editar su propio perfil
- ✅ Registrar hijos/jugadores
- ✅ Editar información de sus hijos
- ✅ Ver detalles de sus hijos
- ✅ Registrar hijos a eventos
- ✅ Ver documentos de verificación de edad de sus hijos
- ✅ Realizar pagos para eventos de sus hijos
- ✅ Ver facturas y confirmaciones de pago

**NO puede:**
- ❌ Ver otros jugadores (solo sus hijos)
- ❌ Ver lista completa de jugadores
- ❌ Aprobar verificaciones de edad
- ❌ Gestionar equipos
- ❌ Acceder al admin dashboard
- ❌ Ver otros usuarios

**URLs Accesibles:**
- `/panel/` - Panel personal
- `/accounts/profile/` - Ver perfil
- `/accounts/profile/edit/` - Editar perfil
- `/accounts/players/register-child/` - Registrar hijo
- `/accounts/players/<int:pk>/` - Ver hijo (solo sus hijos)
- `/accounts/players/<int:pk>/edit/` - Editar hijo (solo sus hijos)
- `/accounts/events/<int:pk>/` - Ver evento
- `/accounts/events/<int:pk>/register/` - Registrar hijo a evento
- `/accounts/events/<int:pk>/stripe/*` - Pagos Stripe

---

### 2. 🏃‍♂️ Manager de Equipo (`team_manager`)

**Permisos:**
- ✅ Iniciar sesión
- ✅ Ver su panel personal (`/panel/`)
- ✅ Editar su propio perfil
- ✅ Crear y gestionar equipos
- ✅ Editar sus equipos
- ✅ Registrar jugadores para sus equipos
- ✅ Ver jugadores de sus equipos
- ✅ Editar jugadores de sus equipos
- ✅ Ver detalles de jugadores de sus equipos
- ✅ Ver documentos de verificación de edad de sus jugadores
- ✅ Ver lista de verificaciones de edad pendientes (solo de sus jugadores)

**NO puede:**
- ❌ Ver jugadores de otros equipos
- ❌ Ver lista completa de jugadores
- ❌ Aprobar verificaciones de edad (solo staff puede)
- ❌ Acceder al admin dashboard
- ❌ Ver otros usuarios
- ❌ Eliminar eventos o datos maestros

**URLs Accesibles:**
- `/panel/` - Panel personal
- `/accounts/profile/` - Ver perfil
- `/accounts/profile/edit/` - Editar perfil
- `/accounts/teams/` - Lista de equipos
- `/accounts/teams/create/` - Crear equipo
- `/accounts/teams/<int:pk>/` - Ver equipo
- `/accounts/teams/<int:pk>/edit/` - Editar equipo (solo sus equipos)
- `/accounts/players/register/` - Registrar jugador
- `/accounts/players/<int:pk>/` - Ver jugador (solo de sus equipos)
- `/accounts/players/<int:pk>/edit/` - Editar jugador (solo de sus equipos)
- `/accounts/age-verifications/` - Ver verificaciones pendientes (solo de sus jugadores)
- `/accounts/players/<int:player_id>/age-verification-document/` - Ver documento (solo de sus jugadores)

---

### 3. 👶 Jugador (`player`)

**Permisos:**
- ❌ **NO puede iniciar sesión** (`is_active=False`)
- ❌ No tiene acceso al sistema
- ✅ Tiene perfil público visible en `/players/<slug>/`
- ✅ Sus padres/managers pueden gestionar su información

**Nota:** Los jugadores son gestionados completamente por sus padres o managers. No tienen acceso directo al sistema.

---

### 4. 👨‍💼 Staff (`is_staff=True`)

**Permisos:**
- ✅ Todo lo que puede un Manager
- ✅ Acceso al admin dashboard
- ✅ Ver lista completa de jugadores
- ✅ Ver lista completa de usuarios
- ✅ Gestionar eventos (crear, editar, ver)
- ✅ Gestionar ubicaciones (países, estados, ciudades)
- ✅ Gestionar archivos multimedia
- ✅ Ver todas las verificaciones de edad
- ✅ Aprobar/rechazar verificaciones de edad
- ✅ Gestionar banners y sponsors

**NO puede:**
- ❌ Eliminar eventos (solo admin)
- ❌ Eliminar datos maestros (solo admin)
- ❌ Operaciones masivas (solo admin)
- ❌ Configuración del sistema (solo admin)
- ❌ Gestión de usuarios (solo admin)

**URLs Accesibles:**
- Todas las URLs de Manager
- `/dashboard/` - Dashboard admin
- `/accounts/players/manage/` - Lista completa de jugadores
- `/accounts/age-verifications/` - Todas las verificaciones
- `/events/*` - Gestión de eventos
- `/locations/*` - Gestión de ubicaciones
- `/files/*` - Gestión de archivos

---

### 5. 🔑 Superuser/Admin (`is_superuser=True`)

**Permisos:**
- ✅ **Todos los permisos del sistema**
- ✅ Todo lo que puede Staff
- ✅ Eliminar eventos
- ✅ Eliminar datos maestros (países, estados, ciudades, etc.)
- ✅ Operaciones masivas (bulk delete/update)
- ✅ Configuración del sistema
- ✅ Gestión completa de usuarios
- ✅ Publicar/despublicar eventos
- ✅ Acceso completo al Django Admin (`/admin/`)

**URLs Accesibles:**
- Todas las URLs del sistema
- `/admin/` - Django Admin completo
- `/accounts/users/` - Gestión de usuarios
- `/accounts/home-content/` - Configuración del sistema
- `/events/<int:pk>/delete/` - Eliminar eventos
- `/files/bulk-delete/` - Operaciones masivas

---

## 📊 Comparativa de Permisos

| Acción | Jugador | Padre | Manager | Staff | Admin |
|--------|---------|-------|---------|-------|-------|
| Iniciar sesión | ❌ | ✅ | ✅ | ✅ | ✅ |
| Ver panel | ❌ | ✅ | ✅ | ✅ | ✅ |
| Editar perfil propio | ❌ | ✅ | ✅ | ✅ | ✅ |
| Registrar hijos | ❌ | ✅ | ❌ | ✅ | ✅ |
| Registrar jugadores | ❌ | ❌ | ✅ | ✅ | ✅ |
| Crear equipos | ❌ | ❌ | ✅ | ✅ | ✅ |
| Ver jugadores propios | ❌ | ✅ | ✅ | ✅ | ✅ |
| Ver todos los jugadores | ❌ | ❌ | ❌ | ✅ | ✅ |
| Aprobar verificaciones | ❌ | ❌ | ❌ | ✅ | ✅ |
| Gestionar eventos | ❌ | ❌ | ❌ | ✅ | ✅ |
| Eliminar eventos | ❌ | ❌ | ❌ | ❌ | ✅ |
| Configuración sistema | ❌ | ❌ | ❌ | ❌ | ✅ |
| Django Admin | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔒 Restricciones Importantes

### Jugadores NO Pueden Iniciar Sesión

Los jugadores tienen `is_active=False` y el sistema bloquea explícitamente su login:

```python
# En PublicLoginView
if user.profile.is_player:
    logout(request)
    messages.error(request, "Players cannot log in...")
    return redirect("accounts:login")
```

### Padres Solo Ven Sus Hijos

Los padres solo pueden ver/editar jugadores que están relacionados con ellos a través de `PlayerParent`.

### Managers Solo Ven Sus Equipos

Los managers solo pueden ver/editar jugadores que pertenecen a equipos donde son managers.

### Staff NO Puede Eliminar Datos Críticos

Aunque staff puede ver y editar, NO puede:
- Eliminar eventos
- Eliminar datos maestros
- Realizar operaciones masivas
- Cambiar configuración del sistema

Solo los **superusers** pueden realizar estas operaciones críticas.

---

## 📝 Notas de Implementación

### Verificación de Permisos

El sistema usa mixins para verificar permisos:

- `LoginRequiredMixin` - Solo requiere estar autenticado
- `ManagerRequiredMixin` - Requiere ser manager
- `StaffRequiredMixin` - Requiere ser staff o superuser
- `SuperuserRequiredMixin` - Requiere ser superuser
- `OwnerOrStaffRequiredMixin` - Requiere ser dueño o staff

### Verificaciones Manuales

Algunas vistas verifican permisos manualmente:

```python
# Ejemplo: PlayerDetailView
is_staff = user.is_staff or user.is_superuser
is_manager = player.team and player.team.manager == user
is_parent = PlayerParent.objects.filter(parent=user, player=player).exists()
is_owner = player.user == user

if not (is_staff or is_manager or is_parent or is_owner):
    raise PermissionDenied("No tienes permisos...")
```

---

## 🎯 Resumen

**Usuario Normal que se Registra:**
- Puede elegir ser **Padre** o **Manager**
- Por defecto: `is_staff=False`, `is_superuser=False`, `is_active=True`
- Tiene acceso limitado según su tipo
- NO puede acceder al admin dashboard
- NO puede ver todos los jugadores
- NO puede realizar operaciones administrativas críticas

**Para más detalles sobre URLs específicas, consultar:**
- `URLS_ADMIN_DASHBOARD.md` - URLs del admin dashboard
- `URLS_CRITICAS.md` - URLs que requieren permisos especiales
- `URLS_BACKEND_COMPLETO.md` - Todas las URLs del sistema

---

**Última actualización:** 2026-01-07



