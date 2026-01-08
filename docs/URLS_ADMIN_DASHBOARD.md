# URLs que usan el Layout de Admin Dashboard

Este documento lista todas las URLs que muestran el layout de admin dashboard (topbar y sidebar) según las condiciones definidas en `templates/base.html`.

**Condición principal:** El usuario debe ser `staff` o `superuser` para ver el layout de admin dashboard.

---

## 📋 Criterios de Inclusión

El layout de admin dashboard se muestra cuando se cumple **AL MENOS UNA** de las siguientes condiciones:

### 1. Por `url_name` (nombre de la ruta)
- `dashboard`
- `home_content_admin`
- `age_verification_list`
- `user_list`
- `player_list`
- `player_detail`
- `player_register`
- `player_edit`

### 2. Por `namespace` (espacio de nombres de la app)
- `events` - Todas las URLs que empiezan con `/events/`
- `locations` - Todas las URLs que empiezan con `/locations/`
- `media` - Todas las URLs que empiezan con `/files/`

### 3. Por `request.path` (contiene en la ruta)
- `/accounts/home-content`
- `/accounts/banner`
- `/accounts/sponsor`
- `/accounts/dashboard-banner`
- `/accounts/age-verifications`
- `/accounts/users`
- `/accounts/players`
- `/admin/` (primeros 8 caracteres)

---

## 🔴 URLs Críticas que NO Requieren Admin o Staff (Vulnerabilidades de Seguridad)

**Las siguientes URLs son críticas pero actualmente solo requieren Login (cualquier usuario autenticado) o no tienen verificación adecuada de permisos:**

### 📋 Resumen de URLs Críticas Sin Protección Adecuada

| Categoría | Cantidad | Estado Actual | Debería Requerir |
|-----------|----------|----------------|------------------|
| Visualización de Datos Sensibles | 1 URL | ⚠️ Solo Login | **Staff/Manager/Parent** |
| Aprobación de Verificaciones | 1 URL | ⚠️ Solo Login (verifica internamente) | **Staff/Manager** |
| Acceso a Documentos Sensibles | 1 URL | ⚠️ Solo Login (verifica internamente) | **Staff/Manager/Parent** |
| Edición de Jugadores | 1 URL | ⚠️ Solo Login (verifica internamente) | **Staff/Manager/Parent** |
| Edición de Equipos | 1 URL | ⚠️ Solo Login (verifica internamente) | **Staff/Manager** |
| **TOTAL** | **~5 URLs** | | |

---

### 🟡 1. Visualización de Datos Sensibles de Jugadores (Requiere Cambio)

**URL crítica que permite a cualquier usuario autenticado ver información de cualquier jugador:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:pk>/` | `accounts:player_detail` | Detalle de jugador | ⚠️ **Solo Login** | ✅ **Staff/Manager/Parent** |

**Razón:** Actualmente cualquier usuario autenticado puede ver el detalle de cualquier jugador, incluyendo información sensible. Debería restringirse a:
- Staff/Admin (pueden ver todos)
- Manager del equipo del jugador
- Padre/acudiente del jugador
- El propio jugador

**Estado:** ⚠️ Requiere modificación en `apps/accounts/views_private.py` - `PlayerDetailView` (agregar verificación de permisos en `dispatch` o `get_object`)

---

### 🔴 2. Aprobación de Verificaciones de Edad (DEBE REQUERIR SOLO STAFF)

**URL crítica que debería requerir SOLO Staff, no Manager:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:pk>/approve-verification/` | `accounts:approve_age_verification` | Aprobar/rechazar verificación | ⚠️ **Solo Login** (verifica Staff/Manager) | ✅ **SOLO Staff** |

**Razón:** La aprobación de verificaciones de edad es una operación administrativa crítica que afecta la elegibilidad de los jugadores. Solo el staff administrativo debería poder aprobar/rechazar verificaciones, no los managers de equipos.

**Estado:** ⚠️ Requiere modificación en `apps/accounts/views_private.py` - `approve_age_verification` (cambiar verificación para requerir solo `is_staff` o `is_superuser`, eliminar verificación de manager)

---

### 🟡 3. Acceso a Documentos de Verificación de Edad (Verificación Interna)

**URL que verifica permisos internamente pero solo requiere login:**

| URL | Nombre | Descripción | Requiere Actual | Verificación Interna |
|-----|--------|-------------|-----------------|----------------------|
| `/accounts/players/<int:player_id>/age-verification-document/` | `accounts:serve_age_verification_document` | Servir documento verificación | ⚠️ **Solo Login** | ✅ Verifica Staff/Manager/Parent |

**Razón:** La función verifica permisos internamente (staff, manager, o padre del jugador), pero debería usar un decorador o mixin más explícito.

**Estado:** ⚠️ Funciona correctamente pero debería usar un decorador personalizado para mayor claridad y seguridad

---

### 🟡 4. Edición de Jugadores (Verificación Interna)

**URL que verifica permisos internamente pero solo requiere login:**

| URL | Nombre | Descripción | Requiere Actual | Verificación Interna |
|-----|--------|-------------|-----------------|----------------------|
| `/accounts/players/<int:pk>/edit/` | `accounts:player_edit` | Editar jugador | ⚠️ **Solo Login** | ✅ Verifica Staff/Manager/Parent |

**Razón:** La vista verifica permisos en `dispatch` (staff, manager, o padre del jugador), pero debería usar un mixin más explícito como `OwnerOrStaffRequiredMixin`.

**Estado:** ⚠️ Funciona correctamente pero debería usar `OwnerOrStaffRequiredMixin` para mayor claridad y seguridad

---

### 🟡 5. Edición de Equipos (Verificación Interna)

**URL que verifica permisos internamente pero solo requiere login:**

| URL | Nombre | Descripción | Requiere Actual | Verificación Interna |
|-----|--------|-------------|-----------------|----------------------|
| `/accounts/teams/<int:pk>/edit/` | `accounts:team_edit` | Editar equipo | ⚠️ **Solo Login** | ✅ Verifica Staff/Manager |

**Razón:** La vista verifica permisos en `dispatch` (staff o manager del equipo), pero debería usar un mixin más explícito como `OwnerOrStaffRequiredMixin`.

**Estado:** ⚠️ Funciona correctamente pero debería usar `OwnerOrStaffRequiredMixin` para mayor claridad y seguridad

---

### 📝 Notas de Implementación

**Para mejorar la seguridad de estas URLs:**

1. **PlayerDetailView** - Agregar verificación de permisos:
   ```python
   def dispatch(self, request, *args, **kwargs):
       player = self.get_object()
       user = request.user

       # Verificar permisos
       is_staff = user.is_staff or user.is_superuser
       is_manager = player.team and player.team.manager == user
       is_parent = PlayerParent.objects.filter(parent=user, player=player).exists()
       is_owner = player.user == user

       if not (is_staff or is_manager or is_parent or is_owner):
           raise PermissionDenied("No tienes permisos para ver este jugador.")

       return super().dispatch(request, *args, **kwargs)
   ```

2. **Aprobar Verificación** - Usar `UserPassesTestMixin`:
   ```python
   class ApproveAgeVerificationView(UserPassesTestMixin, View):
       def test_func(self):
           player = get_object_or_404(Player, pk=self.kwargs['pk'])
           user = self.request.user
           is_staff = user.is_staff or user.is_superuser
           is_manager = player.team and player.team.manager == user
           return is_staff or is_manager
   ```

3. **Servir Documento** - Usar decorador personalizado:
   ```python
   @user_passes_test(lambda u: u.is_authenticated)
   def serve_age_verification_document(request, player_id):
       # Verificación de permisos existente...
   ```

4. **PlayerUpdateView y TeamUpdateView** - Cambiar a `OwnerOrStaffRequiredMixin`:
   ```python
   class PlayerUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
       # ...
   ```

**Nota:** Aunque algunas de estas URLs verifican permisos internamente, es mejor práctica usar mixins o decoradores explícitos para mayor claridad y seguridad.

---

## ⚠️ IMPORTANTE: URLs Críticas que Requieren Admin (Superuser)

**Las siguientes URLs son críticas y deberían requerir SOLO superuser (admin), no solo staff:**

### 📋 Resumen de URLs Críticas por Categoría

| Categoría | Cantidad | Estado Actual | Debería Requerir |
|-----------|----------|----------------|------------------|
| Django Admin | Todas las URLs | ✅ Admin | ✅ Admin |
| Gestión de Usuarios | 1 URL | ⚠️ Staff/Admin | ✅ Admin |
| Configuración del Sistema | 4 URLs | ⚠️ Staff/Admin | ✅ Admin |
| Eliminación Masiva (Bulk) | 2 URLs | ⚠️ Staff | ✅ Admin |
| Publicación/Despublicación | 1 URL | ⚠️ Staff | ✅ Admin |
| Eliminación de Datos Maestros | ~15 URLs | ⚠️ Staff | ✅ Admin |
| Eliminación de Eventos | 1 URL | ⚠️ Staff | ✅ Admin |
| **TOTAL** | **~25+ URLs** | | |

---

### 🔴 1. Django Admin (Ya Requiere Admin)

**Todas las URLs bajo `/admin/` ya requieren superuser:**

| URL | Descripción | Requiere Actual | Requiere Ideal |
|-----|-------------|-----------------|----------------|
| `/admin/` | Django Admin principal | ✅ **Admin** | ✅ **Admin** |
| `/admin/login/` | Login Django Admin | **Público** | **Público** |
| `/admin/*` | Todas las URLs del Django Admin | ✅ **Admin** | ✅ **Admin** |

**Estado:** ✅ Ya implementado correctamente

---

### 🟠 2. Gestión de Usuarios (Requiere Cambio)

**URLs críticas para la seguridad del sistema:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/users/` | `accounts:user_list` | Lista de usuarios | ⚠️ **Staff/Admin** | ✅ **Admin** |

**Razón:** La gestión de usuarios es crítica para la seguridad. Solo los superusuarios deberían poder ver y gestionar todos los usuarios del sistema.

**Estado:** ⚠️ Requiere modificación en `apps/accounts/views_private.py` - `UserListView`

---

### 🟠 3. Configuración del Sistema (Requiere Cambio)

**URLs críticas para la configuración del sitio:**

#### 3.1. Contenido del Home
| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/home-content/` | `accounts:home_content_admin` | Administración contenido home | ⚠️ **Staff/Admin** | ✅ **Admin** |

#### 3.2. Configuración del Sitio
| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/edit-schedule-settings/` | `accounts:edit_schedule_settings` | Editar schedule | ⚠️ **Staff/Admin** | ✅ **Admin** |
| `/accounts/edit-showcase-settings/` | `accounts:edit_showcase_settings` | Editar showcase | ⚠️ **Staff/Admin** | ✅ **Admin** |
| `/accounts/edit-contact-settings/` | `accounts:edit_contact_settings` | Editar contacto | ⚠️ **Staff/Admin** | ✅ **Admin** |

**Razón:** La configuración del sistema afecta a todo el sitio. Solo los superusuarios deberían poder modificar estas configuraciones críticas.

**Estado:** ⚠️ Requiere modificación en `apps/accounts/views_banners.py` - Vistas de configuración

---

### 🟠 4. Operaciones de Eliminación Masiva (Bulk) (Requiere Cambio)

**URLs críticas para operaciones masivas que pueden afectar múltiples registros:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/files/bulk-delete/` | `media:bulk_delete` | Eliminar múltiples archivos | ⚠️ **Staff** | ✅ **Admin** |
| `/files/bulk-update/` | `media:bulk_update` | Actualizar múltiples archivos | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Las operaciones masivas pueden eliminar o modificar grandes cantidades de datos. Solo los superusuarios deberían poder realizar estas operaciones críticas.

**Estado:** ⚠️ Requiere modificación en `apps/media/views.py` - Funciones `media_file_bulk_delete` y `media_file_bulk_update`

---

### 🟠 5. Publicación/Despublicación de Eventos (Requiere Cambio)

**URL crítica para controlar la visibilidad pública de eventos:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/<int:pk>/toggle-publish/` | `events:toggle_publish` | Publicar/despublicar evento | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** La publicación/despublicación de eventos afecta directamente la visibilidad pública del sitio. Solo los superusuarios deberían poder controlar qué eventos son visibles públicamente.

**Estado:** ⚠️ Requiere modificación en `apps/events/views.py` - `EventTogglePublishView`

---

### 🟠 6. Eliminación de Datos Maestros Críticos (Requiere Cambio)

**URLs críticas para eliminar datos maestros que afectan toda la estructura del sistema:**

#### 6.1. Ubicaciones Base (Países, Estados, Ciudades)
| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/locations/countries/<int:pk>/delete/` | `locations:country_delete` | Eliminar país | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/states/<int:pk>/delete/` | `locations:state_delete` | Eliminar estado | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/cities/<int:pk>/delete/` | `locations:city_delete` | Eliminar ciudad | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/countries/<int:pk>/delete/` | `locations:admin_country_delete` | Eliminar país (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/states/<int:pk>/delete/` | `locations:admin_state_delete` | Eliminar estado (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/cities/<int:pk>/delete/` | `locations:admin_city_delete` | Eliminar ciudad (admin) | ⚠️ **Staff** | ✅ **Admin** |

#### 6.2. Configuración del Sistema (Temporadas, Reglas, Sitios)
| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/locations/seasons/<int:pk>/delete/` | `locations:season_delete` | Eliminar temporada | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/rules/<int:pk>/delete/` | `locations:rule_delete` | Eliminar regla | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/sites/<int:pk>/delete/` | `locations:site_delete` | Eliminar sitio | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/seasons/<int:pk>/delete/` | `locations:admin_season_delete` | Eliminar temporada (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/rules/<int:pk>/delete/` | `locations:admin_rule_delete` | Eliminar regla (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/sites/<int:pk>/delete/` | `locations:admin_site_delete` | Eliminar sitio (admin) | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** La eliminación de datos maestros (países, estados, ciudades, temporadas, reglas, sitios) puede afectar cascada a múltiples registros relacionados (eventos, jugadores, hoteles, etc.). Solo los superusuarios deberían poder eliminar estos datos críticos.

**Estado:** ⚠️ Requiere modificación en `apps/locations/views.py` y `apps/locations/views_admin.py` - Vistas DeleteView

---

### 🟠 7. Eliminación de Eventos (Requiere Cambio)

**URL crítica para eliminar eventos que pueden tener datos importantes asociados:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/<int:pk>/delete/` | `events:delete` | Eliminar evento | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Los eventos pueden tener múltiples relaciones (asistencias, pagos, reservas de hotel, etc.). La eliminación de eventos puede causar pérdida de datos importantes. Solo los superusuarios deberían poder eliminar eventos.

**Estado:** ⚠️ Requiere modificación en `apps/events/views.py` - `EventDeleteView`

---

### 🟠 8. Eliminación de Divisiones (Requiere Cambio)

**URL crítica para eliminar divisiones que afectan la estructura de eventos:**

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/divisions/<int:pk>/delete/` | `events:division_delete` | Eliminar división | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Las divisiones son parte fundamental de la estructura de eventos. Su eliminación puede afectar múltiples eventos y jugadores. Solo los superusuarios deberían poder eliminar divisiones.

**Estado:** ⚠️ Requiere modificación en `apps/events/views.py` - `DivisionDeleteView`

---

### 📝 Notas de Implementación

**Para implementar estos cambios, se necesita:**

1. **Crear un nuevo mixin `SuperuserRequiredMixin`** en `apps/core/mixins.py`:
   ```python
   class SuperuserRequiredMixin(LoginRequiredMixin):
       """Mixin que requiere que el usuario sea superuser."""
       def dispatch(self, request, *args, **kwargs):
           if not request.user.is_authenticated:
               return redirect("accounts:login")
           if not request.user.is_superuser:
               messages.error(request, "Solo los administradores pueden acceder a esta sección.")
               return redirect("panel")
           return super().dispatch(request, *args, **kwargs)
   ```

2. **Aplicar el mixin a las vistas críticas:**

   **Gestión de Usuarios:**
   - `UserListView` en `apps/accounts/views_private.py`

   **Configuración del Sistema:**
   - `HomeContentAdminView` en `apps/accounts/views_banners.py`
   - `ScheduleSettingsUpdateView` en `apps/accounts/views_banners.py`
   - `ShowcaseSettingsUpdateView` en `apps/accounts/views_banners.py`
   - `ContactSettingsUpdateView` en `apps/accounts/views_banners.py`

   **Operaciones Masivas:**
   - `media_file_bulk_delete` en `apps/media/views.py` (función, requiere decorador)
   - `media_file_bulk_update` en `apps/media/views.py` (función, requiere decorador)

   **Publicación/Despublicación:**
   - `EventTogglePublishView` en `apps/events/views.py`

   **Eliminación de Datos Maestros:**
   - `CountryDeleteView`, `StateDeleteView`, `CityDeleteView` en `apps/locations/views.py`
   - `SeasonDeleteView`, `RuleDeleteView`, `SiteDeleteView` en `apps/locations/views.py`
   - `AdminCountryDeleteView`, `AdminStateDeleteView`, `AdminCityDeleteView` en `apps/locations/views_admin.py`
   - `AdminSeasonDeleteView`, `AdminRuleDeleteView`, `AdminSiteDeleteView` en `apps/locations/views_admin.py`

   **Eliminación de Eventos y Divisiones:**
   - `EventDeleteView` en `apps/events/views.py`
   - `DivisionDeleteView` en `apps/events/views.py`

3. **Para funciones (no clases), usar decorador:**
   ```python
   from django.contrib.auth.decorators import user_passes_test

   @user_passes_test(lambda u: u.is_superuser)
   @require_http_methods(["POST"])
   def media_file_bulk_delete(request):
       # ...
   ```

**Nota:** Actualmente en el código, estas URLs aceptan tanto `staff` como `superuser`, pero por seguridad deberían requerir solo `superuser`.

---

## 📍 URLs por Categoría

### 1. Dashboard Principal

| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/dashboard/` | `dashboard` | Dashboard principal del sistema | **Staff** |

---

### 2. Events (namespace: `events`)

**Todas las URLs bajo `/events/` usan el layout de admin dashboard:**

| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/events/dashboard/` | `events:dashboard` | Dashboard de eventos | **Staff** |
| `/events/list/` | `events:list` | Lista de eventos (admin) | **Staff** |
| `/events/create/` | `events:create` | Crear evento | **Staff** |
| `/events/admin/<int:pk>/` | `events:admin_detail` | Detalle evento (admin) | **Staff** |
| `/events/<int:pk>/edit/` | `events:update` | Editar evento | **Staff** |
| `/events/<int:pk>/delete/` | `events:delete` | Eliminar evento | **Admin** ⚠️ |
| `/events/<int:pk>/toggle-publish/` | `events:toggle_publish` | Publicar/despublicar evento | **Admin** ⚠️ |
| `/events/calendar/` | `events:calendar` | Calendario de eventos | **Staff** |
| `/events/<int:event_id>/attend/` | `events:attend` | Asistir a evento | **Login** |
| `/events/api/detail/<int:pk>/` | `events:api_detail` | API detalle evento | **Staff** |
| `/events/divisions/` | `events:division_list` | Lista de divisiones | **Staff** |
| `/events/divisions/create/` | `events:division_create` | Crear división | **Staff** |
| `/events/divisions/<int:pk>/` | `events:division_detail` | Detalle división | **Staff** |
| `/events/divisions/<int:pk>/edit/` | `events:division_update` | Editar división | **Staff** |
| `/events/divisions/<int:pk>/delete/` | `events:division_delete` | Eliminar división | **Admin** ⚠️ |
| `/events/event-contacts/` | `events:eventcontact_list` | Lista de contactos | **Staff** |
| `/events/event-contacts/create/` | `events:eventcontact_create` | Crear contacto | **Staff** |
| `/events/event-contacts/<int:pk>/` | `events:eventcontact_detail` | Detalle contacto | **Staff** |
| `/events/event-contacts/<int:pk>/edit/` | `events:eventcontact_update` | Editar contacto | **Staff** |
| `/events/event-contacts/<int:pk>/delete/` | `events:eventcontact_delete` | Eliminar contacto | **Staff** |
| `/events/event-types/` | `events:eventtype_list` | Lista tipos de evento | **Staff** |
| `/events/event-types/create/` | `events:eventtype_create` | Crear tipo evento | **Staff** |
| `/events/event-types/<int:pk>/` | `events:eventtype_detail` | Detalle tipo evento | **Staff** |
| `/events/event-types/<int:pk>/edit/` | `events:eventtype_update` | Editar tipo evento | **Staff** |
| `/events/event-types/<int:pk>/delete/` | `events:eventtype_delete` | Eliminar tipo evento | **Staff** |
| `/events/gate-fee-types/` | `events:gatefeetype_list` | Lista gate fee types | **Staff** |
| `/events/gate-fee-types/create/` | `events:gatefeetype_create` | Crear gate fee type | **Staff** |
| `/events/gate-fee-types/<int:pk>/` | `events:gatefeetype_detail` | Detalle gate fee type | **Staff** |
| `/events/gate-fee-types/<int:pk>/edit/` | `events:gatefeetype_update` | Editar gate fee type | **Staff** |
| `/events/gate-fee-types/<int:pk>/delete/` | `events:gatefeetype_delete` | Eliminar gate fee type | **Staff** |

**Nota:** Las URLs públicas (`/events/` y `/events/<int:pk>/`) NO usan el layout de admin dashboard porque tienen `url_name` diferente (`public_list`, `public_detail`).

---

### 3. Locations (namespace: `locations`)

**Todas las URLs bajo `/locations/` usan el layout de admin dashboard:**

#### 3.1. Países, Estados, Ciudades
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/locations/countries/` | `locations:country_list` | Lista de países | **Staff** |
| `/locations/countries/<int:pk>/` | `locations:country_detail` | Detalle país | **Staff** |
| `/locations/countries/create/` | `locations:country_create` | Crear país | **Staff** |
| `/locations/countries/<int:pk>/edit/` | `locations:country_update` | Editar país | **Staff** |
| `/locations/countries/<int:pk>/delete/` | `locations:country_delete` | Eliminar país | **Admin** ⚠️ |
| `/locations/states/` | `locations:state_list` | Lista de estados | **Staff** |
| `/locations/states/<int:pk>/` | `locations:state_detail` | Detalle estado | **Staff** |
| `/locations/states/create/` | `locations:state_create` | Crear estado | **Staff** |
| `/locations/states/<int:pk>/edit/` | `locations:state_update` | Editar estado | **Staff** |
| `/locations/states/<int:pk>/delete/` | `locations:state_delete` | Eliminar estado | **Admin** ⚠️ |
| `/locations/cities/` | `locations:city_list` | Lista de ciudades | **Staff** |
| `/locations/cities/<int:pk>/` | `locations:city_detail` | Detalle ciudad | **Staff** |
| `/locations/cities/create/` | `locations:city_create` | Crear ciudad | **Staff** |
| `/locations/cities/<int:pk>/edit/` | `locations:city_update` | Editar ciudad | **Staff** |
| `/locations/cities/<int:pk>/delete/` | `locations:city_delete` | Eliminar ciudad | **Admin** ⚠️ |

#### 3.2. Temporadas, Reglas, Sitios
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/locations/seasons/` | `locations:season_list` | Lista de temporadas | **Staff** |
| `/locations/seasons/<int:pk>/` | `locations:season_detail` | Detalle temporada | **Staff** |
| `/locations/seasons/create/` | `locations:season_create` | Crear temporada | **Staff** |
| `/locations/seasons/<int:pk>/edit/` | `locations:season_update` | Editar temporada | **Staff** |
| `/locations/seasons/<int:pk>/delete/` | `locations:season_delete` | Eliminar temporada | **Staff** |
| `/locations/rules/` | `locations:rule_list` | Lista de reglas | **Staff** |
| `/locations/rules/<int:pk>/` | `locations:rule_detail` | Detalle regla | **Staff** |
| `/locations/rules/create/` | `locations:rule_create` | Crear regla | **Staff** |
| `/locations/rules/<int:pk>/edit/` | `locations:rule_update` | Editar regla | **Staff** |
| `/locations/rules/<int:pk>/delete/` | `locations:rule_delete` | Eliminar regla | **Staff** |
| `/locations/sites/` | `locations:site_list` | Lista de sitios | **Staff** |
| `/locations/sites/<int:pk>/` | `locations:site_detail` | Detalle sitio | **Staff** |
| `/locations/sites/create/` | `locations:site_create` | Crear sitio | **Staff** |
| `/locations/sites/<int:pk>/edit/` | `locations:site_update` | Editar sitio | **Staff** |
| `/locations/sites/<int:pk>/delete/` | `locations:site_delete` | Eliminar sitio | **Staff** |

#### 3.3. URLs Admin (Hoteles)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/locations/admin/countries/` | `locations:admin_country_list` | Lista admin países | **Staff** |
| `/locations/admin/countries/<int:pk>/` | `locations:admin_country_detail` | Detalle admin país | **Staff** |
| `/locations/admin/countries/create/` | `locations:admin_country_create` | Crear admin país | **Staff** |
| `/locations/admin/countries/<int:pk>/edit/` | `locations:admin_country_update` | Editar admin país | **Staff** |
| `/locations/admin/countries/<int:pk>/delete/` | `locations:admin_country_delete` | Eliminar admin país | **Staff** |
| `/locations/admin/states/` | `locations:admin_state_list` | Lista admin estados | **Staff** |
| `/locations/admin/states/<int:pk>/` | `locations:admin_state_detail` | Detalle admin estado | **Staff** |
| `/locations/admin/states/create/` | `locations:admin_state_create` | Crear admin estado | **Staff** |
| `/locations/admin/states/<int:pk>/edit/` | `locations:admin_state_update` | Editar admin estado | **Staff** |
| `/locations/admin/states/<int:pk>/delete/` | `locations:admin_state_delete` | Eliminar admin estado | **Staff** |
| `/locations/admin/cities/` | `locations:admin_city_list` | Lista admin ciudades | **Staff** |
| `/locations/admin/cities/<int:pk>/` | `locations:admin_city_detail` | Detalle admin ciudad | **Staff** |
| `/locations/admin/cities/create/` | `locations:admin_city_create` | Crear admin ciudad | **Staff** |
| `/locations/admin/cities/<int:pk>/edit/` | `locations:admin_city_update` | Editar admin ciudad | **Staff** |
| `/locations/admin/cities/<int:pk>/delete/` | `locations:admin_city_delete` | Eliminar admin ciudad | **Staff** |
| `/locations/admin/seasons/` | `locations:admin_season_list` | Lista admin temporadas | **Staff** |
| `/locations/admin/seasons/<int:pk>/` | `locations:admin_season_detail` | Detalle admin temporada | **Staff** |
| `/locations/admin/seasons/create/` | `locations:admin_season_create` | Crear admin temporada | **Staff** |
| `/locations/admin/seasons/<int:pk>/edit/` | `locations:admin_season_update` | Editar admin temporada | **Staff** |
| `/locations/admin/seasons/<int:pk>/delete/` | `locations:admin_season_delete` | Eliminar admin temporada | **Staff** |
| `/locations/admin/rules/` | `locations:admin_rule_list` | Lista admin reglas | **Staff** |
| `/locations/admin/rules/<int:pk>/` | `locations:admin_rule_detail` | Detalle admin regla | **Staff** |
| `/locations/admin/rules/create/` | `locations:admin_rule_create` | Crear admin regla | **Staff** |
| `/locations/admin/rules/<int:pk>/edit/` | `locations:admin_rule_update` | Editar admin regla | **Staff** |
| `/locations/admin/rules/<int:pk>/delete/` | `locations:admin_rule_delete` | Eliminar admin regla | **Staff** |
| `/locations/admin/sites/` | `locations:admin_site_list` | Lista admin sitios | **Staff** |
| `/locations/admin/sites/<int:pk>/` | `locations:admin_site_detail` | Detalle admin sitio | **Staff** |
| `/locations/admin/sites/create/` | `locations:admin_site_create` | Crear admin sitio | **Staff** |
| `/locations/admin/sites/<int:pk>/edit/` | `locations:admin_site_update` | Editar admin sitio | **Staff** |
| `/locations/admin/sites/<int:pk>/delete/` | `locations:admin_site_delete` | Eliminar admin sitio | **Staff** |
| `/locations/admin/hotels/` | `locations:admin_hotel_list` | Lista admin hoteles | **Staff** |
| `/locations/admin/hotels/<int:pk>/` | `locations:admin_hotel_detail` | Detalle admin hotel | **Staff** |
| `/locations/admin/hotels/create/` | `locations:admin_hotel_create` | Crear admin hotel | **Staff** |
| `/locations/admin/hotels/<int:pk>/edit/` | `locations:admin_hotel_update` | Editar admin hotel | **Staff** |
| `/locations/admin/hotels/<int:pk>/delete/` | `locations:admin_hotel_delete` | Eliminar admin hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/images/` | `locations:admin_hotel_image_list` | Lista imágenes hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/images/create/` | `locations:admin_hotel_image_create` | Crear imagen hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/images/<int:pk>/edit/` | `locations:admin_hotel_image_update` | Editar imagen hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/images/<int:pk>/delete/` | `locations:admin_hotel_image_delete` | Eliminar imagen hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/` | `locations:admin_hotel_amenity_list` | Lista amenidades hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/create/` | `locations:admin_hotel_amenity_create` | Crear amenidad hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/<int:pk>/edit/` | `locations:admin_hotel_amenity_update` | Editar amenidad hotel | **Staff** |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/<int:pk>/delete/` | `locations:admin_hotel_amenity_delete` | Eliminar amenidad hotel | **Staff** |
| `/locations/admin/hotel-rooms/` | `locations:admin_hotel_room_list` | Lista habitaciones | **Staff** |
| `/locations/admin/hotel-rooms/create/` | `locations:admin_hotel_room_create` | Crear habitación | **Staff** |
| `/locations/admin/hotel-rooms/<int:pk>/edit/` | `locations:admin_hotel_room_update` | Editar habitación | **Staff** |
| `/locations/admin/hotel-rooms/<int:pk>/delete/` | `locations:admin_hotel_room_delete` | Eliminar habitación | **Staff** |
| `/locations/admin/hotel-rooms/images/<int:pk>/delete/` | `locations:admin_hotel_room_image_delete` | Eliminar imagen habitación | **Staff** |
| `/locations/admin/hotel-rooms/taxes/create/` | `locations:admin_hotel_room_tax_create_ajax` | Crear impuesto habitación | **Staff** |
| `/locations/admin/hotel-rooms/<int:room_id>/taxes/<int:tax_id>/delete/` | `locations:admin_hotel_room_tax_delete_ajax` | Eliminar impuesto habitación | **Staff** |
| `/locations/admin/hotel-services/` | `locations:admin_hotel_service_list` | Lista servicios hotel | **Staff** |
| `/locations/admin/hotel-services/create/` | `locations:admin_hotel_service_create` | Crear servicio hotel | **Staff** |
| `/locations/admin/hotel-services/<int:pk>/edit/` | `locations:admin_hotel_service_update` | Editar servicio hotel | **Staff** |
| `/locations/admin/hotel-services/<int:pk>/delete/` | `locations:admin_hotel_service_delete` | Eliminar servicio hotel | **Staff** |
| `/locations/admin/hotel-reservations/` | `locations:admin_hotel_reservation_list` | Lista reservas hotel | **Staff** |
| `/locations/admin/hotel-reservations/<int:pk>/` | `locations:admin_hotel_reservation_detail` | Detalle reserva hotel | **Staff** |
| `/locations/admin/hotel-reservations/create/` | `locations:admin_hotel_reservation_create` | Crear reserva hotel | **Staff** |
| `/locations/admin/hotel-reservations/<int:pk>/edit/` | `locations:admin_hotel_reservation_update` | Editar reserva hotel | **Staff** |
| `/locations/admin/hotel-reservations/<int:pk>/delete/` | `locations:admin_hotel_reservation_delete` | Eliminar reserva hotel | **Staff** |

#### 3.4. URLs AJAX y API
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/locations/ajax/states/<int:country_id>/` | `locations:get_states_by_country` | Estados por país (AJAX) | **Público** |
| `/locations/ajax/cities/<int:state_id>/` | `locations:get_cities_by_state` | Ciudades por estado (AJAX) | **Público** |
| `/locations/api/countries/` | `locations:countries_api` | API países | **Público** |
| `/locations/api/states/` | `locations:states_api` | API estados | **Público** |
| `/locations/api/cities/` | `locations:cities_api` | API ciudades | **Público** |
| `/locations/api/seasons/` | `locations:seasons_api` | API temporadas | **Público** |
| `/locations/api/rules/` | `locations:rules_api` | API reglas | **Público** |
| `/locations/api/sites/` | `locations:sites_api` | API sitios | **Público** |
| `/locations/api/hotels/` | `locations:hotels_api` | API hoteles | **Público** |

**Nota:** Las URLs front de hoteles (`/locations/hotels/`) también usan el layout de admin dashboard porque están bajo el namespace `locations`.

---

### 4. Media (namespace: `media`)

**Todas las URLs bajo `/files/` usan el layout de admin dashboard:**

| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/files/` | `media:list` | Lista de archivos multimedia | **Staff** |
| `/files/create/` | `media:create` | Crear archivo multimedia | **Staff** |
| `/files/<int:pk>/` | `media:detail` | Detalle archivo multimedia | **Staff** |
| `/files/<int:pk>/edit/` | `media:update` | Editar archivo multimedia | **Staff** |
| `/files/<int:pk>/delete/` | `media:delete` | Eliminar archivo multimedia | **Staff** |
| `/files/upload/` | `media:upload_ajax` | Subir archivo (AJAX) | **Staff** |
| `/files/bulk-delete/` | `media:bulk_delete` | Eliminar múltiples archivos | **Admin** ⚠️ |
| `/files/bulk-update/` | `media:bulk_update` | Actualizar múltiples archivos | **Admin** ⚠️ |
| `/files/<int:pk>/update-ajax/` | `media:update_ajax` | Actualizar archivo (AJAX) | **Staff** |
| `/files/list-ajax/` | `media:list_ajax` | Listar archivos (AJAX) | **Staff** |

---

### 5. Accounts - Por `url_name` específico

| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/home-content/` | `accounts:home_content_admin` | Administración contenido home | **Admin** ⚠️ |
| `/accounts/age-verifications/` | `accounts:age_verification_list` | Lista verificaciones de edad | **Staff/Manager** |
| `/accounts/users/` | `accounts:user_list` | Lista de usuarios | **Admin** ⚠️ |
| `/accounts/players/manage/` | `accounts:player_list` | Lista de jugadores | **Staff** |
| `/accounts/players/<int:pk>/` | `accounts:player_detail` | Detalle jugador | **Login** ⚠️ |
| `/accounts/players/register/` | `accounts:player_register` | Registrar jugador | **Manager** |
| `/accounts/players/<int:pk>/edit/` | `accounts:player_edit` | Editar jugador | **Login** ⚠️ |

**⚠️ Nota:** Las URLs marcadas con ⚠️ deberían requerir **Admin (Superuser)** por seguridad, pero actualmente aceptan staff.

---

### 6. Accounts - Por `request.path` (contiene)

**Todas las URLs que contienen estos paths usan el layout de admin dashboard:**

#### 6.1. Banners del Home (`/accounts/banner`)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/banners/` | `accounts:banner_list` | Lista de banners | **Staff** |
| `/accounts/banners/create/` | `accounts:banner_create` | Crear banner | **Staff** |
| `/accounts/banners/<int:pk>/` | `accounts:banner_detail` | Detalle banner | **Staff** |
| `/accounts/banners/<int:pk>/edit/` | `accounts:banner_update` | Editar banner | **Staff** |
| `/accounts/banners/<int:pk>/delete/` | `accounts:banner_delete` | Eliminar banner | **Staff** |

#### 6.2. Sponsors (`/accounts/sponsor`)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/sponsors/` | `accounts:sponsor_list` | Lista de sponsors | **Staff** |
| `/accounts/sponsors/create/` | `accounts:sponsor_create` | Crear sponsor | **Staff** |
| `/accounts/sponsors/<int:pk>/` | `accounts:sponsor_detail` | Detalle sponsor | **Staff** |
| `/accounts/sponsors/<int:pk>/edit/` | `accounts:sponsor_update` | Editar sponsor | **Staff** |
| `/accounts/sponsors/<int:pk>/delete/` | `accounts:sponsor_delete` | Eliminar sponsor | **Staff** |

#### 6.3. Banners del Dashboard (`/accounts/dashboard-banner`)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/dashboard-banners/` | `accounts:dashboard_banner_list` | Lista banners dashboard | **Staff** |
| `/accounts/dashboard-banners/create/` | `accounts:dashboard_banner_create` | Crear banner dashboard | **Staff** |
| `/accounts/dashboard-banners/<int:pk>/` | `accounts:dashboard_banner_detail` | Detalle banner dashboard | **Staff** |
| `/accounts/dashboard-banners/<int:pk>/edit/` | `accounts:dashboard_banner_update` | Editar banner dashboard | **Staff** |
| `/accounts/dashboard-banners/<int:pk>/delete/` | `accounts:dashboard_banner_delete` | Eliminar banner dashboard | **Staff** |

#### 6.4. Hoteles (`/accounts/hotels`)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/hotels/` | `accounts:hotel_list` | Lista de hoteles | **Staff** |
| `/accounts/hotels/create/` | `accounts:hotel_create` | Crear hotel | **Staff** |
| `/accounts/hotels/<int:pk>/` | `accounts:hotel_detail` | Detalle hotel | **Staff** |
| `/accounts/hotels/<int:pk>/edit/` | `accounts:hotel_update` | Editar hotel | **Staff** |
| `/accounts/hotels/<int:pk>/delete/` | `accounts:hotel_delete` | Eliminar hotel | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/images/` | `accounts:hotel_image_list` | Lista imágenes hotel | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/images/create/` | `accounts:hotel_image_create` | Crear imagen hotel | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/images/<int:pk>/edit/` | `accounts:hotel_image_update` | Editar imagen hotel | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/images/<int:pk>/delete/` | `accounts:hotel_image_delete` | Eliminar imagen hotel | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/amenities/` | `accounts:hotel_amenity_list` | Lista amenidades | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/amenities/create/` | `accounts:hotel_amenity_create` | Crear amenidad | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/amenities/<int:pk>/edit/` | `accounts:hotel_amenity_update` | Editar amenidad | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/amenities/<int:pk>/delete/` | `accounts:hotel_amenity_delete` | Eliminar amenidad | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/rooms/` | `accounts:hotel_room_list` | Lista habitaciones | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/rooms/create/` | `accounts:hotel_room_create` | Crear habitación | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/rooms/<int:pk>/edit/` | `accounts:hotel_room_update` | Editar habitación | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/rooms/<int:pk>/delete/` | `accounts:hotel_room_delete` | Eliminar habitación | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/services/` | `accounts:hotel_service_list` | Lista servicios | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/services/create/` | `accounts:hotel_service_create` | Crear servicio | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/services/<int:pk>/edit/` | `accounts:hotel_service_update` | Editar servicio | **Staff** |
| `/accounts/hotels/<int:hotel_pk>/services/<int:pk>/delete/` | `accounts:hotel_service_delete` | Eliminar servicio | **Staff** |

#### 6.5. Configuración del Sitio (`/accounts/home-content`)
| URL | Nombre | Descripción | Requiere |
|-----|--------|-------------|----------|
| `/accounts/home-content/` | `accounts:home_content_admin` | Administración contenido home | **Admin** ⚠️ |
| `/accounts/edit-schedule-settings/` | `accounts:edit_schedule_settings` | Editar schedule | **Admin** ⚠️ |
| `/accounts/edit-showcase-settings/` | `accounts:edit_showcase_settings` | Editar showcase | **Admin** ⚠️ |
| `/accounts/edit-contact-settings/` | `accounts:edit_contact_settings` | Editar contacto | **Admin** ⚠️ |

**⚠️ Nota:** Las URLs de configuración del sitio deberían requerir **Admin (Superuser)** por seguridad, pero actualmente aceptan staff.

---

### 7. Django Admin

**Todas las URLs que empiezan con `/admin/` usan el layout de admin dashboard:**

| URL | Descripción | Requiere |
|-----|-------------|----------|
| `/admin/` | Django Admin principal | **Admin** |
| `/admin/login/` | Login Django Admin | **Público** |
| `/admin/*` | Todas las URLs del Django Admin | **Admin** |

---

## 📊 Resumen por Categoría

| Categoría | Cantidad Aprox. | Requisitos |
|-----------|----------------|------------|
| Dashboard Principal | 1 | Staff |
| Events | ~30 URLs | Staff (1 URL: Login) |
| Locations | ~80 URLs | Staff (APIs: Público) |
| Media | ~10 URLs | Staff |
| Accounts (por url_name) | 7 URLs | Staff/Manager/Admin ⚠️ |
| Accounts (por path) | ~40 URLs | Staff (algunas: Admin ⚠️) |
| Django Admin | Todas | Admin (login: Público) |
| **TOTAL** | **~170+ URLs** | Mayoría: Staff |

### Desglose de Requisitos

- **Staff**: ~155 URLs (requieren staff o superuser)
- **Admin**:
  - ✅ Django Admin - Ya implementado correctamente
  - ⚠️ ~22 URLs críticas que deberían requerir solo superuser (ver sección "URLs Críticas" arriba):
    - Gestión de Usuarios: 1 URL
    - Configuración del Sistema: 4 URLs
    - Operaciones Masivas: 2 URLs
    - Publicación/Despublicación: 1 URL
    - Eliminación de Datos Maestros: ~12 URLs
    - Eliminación de Eventos: 1 URL
    - Eliminación de Divisiones: 1 URL
- **Manager**: 1 URL (`/accounts/players/register/`)
- **Staff/Manager**: 1 URL (`/accounts/age-verifications/`)
- **Login**: 1 URL (`/events/<int:event_id>/attend/`)
- **Público**: APIs de locations y login de Django Admin

### URLs Críticas que Requieren Cambio

**URLs que deberían requerir Admin:**
- **Gestión de Usuarios**: 1 URL (`/accounts/users/`)
- **Configuración del Sistema**: 4 URLs (`/accounts/home-content/`, `/accounts/edit-*-settings/`)
- **Operaciones Masivas**: 2 URLs (`/files/bulk-delete/`, `/files/bulk-update/`)
- **Publicación/Despublicación**: 1 URL (`/events/<int:pk>/toggle-publish/`)
- **Eliminación de Datos Maestros**: ~12 URLs (países, estados, ciudades, temporadas, reglas, sitios)
- **Eliminación de Eventos**: 1 URL (`/events/<int:pk>/delete/`)
- **Eliminación de Divisiones**: 1 URL (`/events/divisions/<int:pk>/delete/`)
- **Total a modificar (Admin)**: ~22 URLs

**URLs que NO requieren Admin/Staff (Vulnerabilidades):**

**URLs que deberían requerir SOLO Staff:**
- **Aprobación de Verificaciones**: 1 URL (`/accounts/players/<int:pk>/approve-verification/`) - **CRÍTICO** - Operación administrativa que solo staff debería realizar
- **Total a modificar (Solo Staff)**: 1 URL

**URLs que deberían requerir Staff/Manager/Parent (con verificación adecuada):**
- **Visualización de Datos Sensibles**: 1 URL (`/accounts/players/<int:pk>/`) - **CRÍTICO** - Actualmente sin verificación de permisos
- **Acceso a Documentos**: 1 URL (`/accounts/players/<int:player_id>/age-verification-document/`) - Verifica internamente pero debería usar decorador explícito
- **Edición de Jugadores**: 1 URL (`/accounts/players/<int:pk>/edit/`) - Verifica internamente pero debería usar `OwnerOrStaffRequiredMixin`
- **Total a modificar (Staff/Manager/Parent)**: 3 URLs

**URLs que deberían requerir Staff/Manager (con verificación adecuada):**
- **Edición de Equipos**: 1 URL (`/accounts/teams/<int:pk>/edit/`) - Verifica internamente pero debería usar `OwnerOrStaffRequiredMixin`
- **Total a modificar (Staff/Manager)**: 1 URL

**Total a modificar (Seguridad)**: ~5 URLs

---

## 🔐 Leyenda de Requisitos

- **Staff**: Requiere que el usuario sea `staff` o `superuser` (StaffRequiredMixin)
- **Admin**: Requiere que el usuario sea `superuser` (solo admin)
- **Manager**: Requiere que el usuario sea `manager` de equipo o `staff` (ManagerRequiredMixin)
- **Staff/Manager**: Requiere que el usuario sea `staff` o `manager` de equipo (UserPassesTestMixin)
- **Login**: Solo requiere que el usuario esté autenticado (LoginRequiredMixin)
- **Público**: No requiere autenticación
- **⚠️**: URLs que actualmente aceptan staff pero deberían requerir solo admin por seguridad

---

## ⚠️ Notas Importantes

1. **URLs Críticas que Deberían Requerir Admin (ver sección detallada arriba):**
   - **Django Admin** (`/admin/*`) - ✅ Ya implementado correctamente
   - **Gestión de Usuarios** (`/accounts/users/`) - ⚠️ Requiere cambio
   - **Configuración del Sistema** (`/accounts/home-content/`, `/accounts/edit-*-settings/`) - ⚠️ Requiere cambio
   - **Operaciones Masivas** (`/files/bulk-delete/`, `/files/bulk-update/`) - ⚠️ Requiere cambio
   - **Publicación/Despublicación** (`/events/<int:pk>/toggle-publish/`) - ⚠️ Requiere cambio
   - **Eliminación de Datos Maestros** (países, estados, ciudades, temporadas, reglas, sitios) - ⚠️ Requiere cambio
   - **Eliminación de Eventos** (`/events/<int:pk>/delete/`) - ⚠️ Requiere cambio
   - **Eliminación de Divisiones** (`/events/divisions/<int:pk>/delete/`) - ⚠️ Requiere cambio

2. **La mayoría de estas URLs requieren que el usuario sea `staff` o `superuser`** para ver el layout de admin dashboard.

3. **Excepciones:**
   - `/events/<int:event_id>/attend/` solo requiere **Login** (cualquier usuario autenticado)
   - `/accounts/age-verifications/` requiere **Staff/Manager** (staff o manager de equipo)
   - `/accounts/players/register/` requiere **Manager** (manager de equipo o staff)
   - Las APIs públicas de locations no requieren autenticación

4. **Las URLs públicas NO usan el layout de admin dashboard:**
   - `/events/` (lista pública)
   - `/events/<int:pk>/` (detalle público)
   - `/locations/api/*` (APIs públicas)
   - Cualquier otra URL que no cumpla los criterios

5. **El layout de admin dashboard incluye:**
   - Topbar (barra superior con búsqueda, notificaciones, menú de usuario)
   - Sidebar (menú lateral con navegación)

6. **Si una URL no está en esta lista pero debería usar el layout de admin dashboard**, debe agregarse a las condiciones en `templates/base.html` (líneas 146 y 298).

7. **Recomendación de Seguridad:** Las URLs marcadas con ⚠️ deberían modificarse para requerir solo `superuser` en lugar de `staff or superuser`.

8. **URLs Críticas Sin Protección Adecuada (ver sección detallada arriba):**
   - `/accounts/players/<int:pk>/` - **CRÍTICO**: Cualquier usuario autenticado puede ver cualquier jugador (sin verificación de permisos)
   - `/accounts/players/<int:pk>/approve-verification/` - Verifica permisos internamente pero debería usar mixin explícito
   - `/accounts/players/<int:player_id>/age-verification-document/` - Verifica permisos internamente pero debería usar decorador explícito
   - `/accounts/players/<int:pk>/edit/` - Verifica permisos internamente pero debería usar `OwnerOrStaffRequiredMixin`
   - `/accounts/teams/<int:pk>/edit/` - Verifica permisos internamente pero debería usar `OwnerOrStaffRequiredMixin`

---

**Última actualización:** 2026-01-07
