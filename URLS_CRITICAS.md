# URLs Críticas - Requieren Cambios de Seguridad

Este documento lista todas las URLs críticas que requieren cambios de seguridad, organizadas por nivel de criticidad y tipo de acceso requerido.

**Última actualización:** 2026-01-07

---

## 📋 Resumen Ejecutivo

| Categoría | Cantidad | Prioridad | Estado |
|-----------|----------|-----------|--------|
| **URLs que requieren SOLO Admin (Superuser)** | ~22 URLs | 🔴 **ALTA** | ⚠️ Requiere cambio |
| **URLs que requieren SOLO Staff** | 1 URL | 🔴 **ALTA** | ⚠️ Requiere cambio |
| **URLs que requieren Staff/Manager/Parent** | 3 URLs | 🟡 **MEDIA** | ⚠️ Requiere cambio |
| **URLs que requieren Staff/Manager** | 1 URL | 🟡 **MEDIA** | ⚠️ Requiere cambio |
| **TOTAL** | **~27 URLs** | | |

---

## 🔴 PRIORIDAD ALTA: URLs que Requieren SOLO Admin (Superuser)

**Estas URLs son críticas y deberían requerir SOLO superuser (admin), no solo staff:**

### 1. Gestión de Usuarios

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/users/` | `accounts:user_list` | Lista de usuarios | ⚠️ **Staff/Admin** | ✅ **Admin** |

**Razón:** La gestión de usuarios es crítica para la seguridad. Solo los superusuarios deberían poder ver y gestionar todos los usuarios del sistema.

**Archivo:** `apps/accounts/views_private.py` - `UserListView`

---

### 2. Configuración del Sistema

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/home-content/` | `accounts:home_content_admin` | Administración contenido home | ⚠️ **Staff/Admin** | ✅ **Admin** |
| `/accounts/edit-schedule-settings/` | `accounts:edit_schedule_settings` | Editar schedule | ⚠️ **Staff/Admin** | ✅ **Admin** |
| `/accounts/edit-showcase-settings/` | `accounts:edit_showcase_settings` | Editar showcase | ⚠️ **Staff/Admin** | ✅ **Admin** |
| `/accounts/edit-contact-settings/` | `accounts:edit_contact_settings` | Editar contacto | ⚠️ **Staff/Admin** | ✅ **Admin** |

**Razón:** La configuración del sistema afecta a todo el sitio. Solo los superusuarios deberían poder modificar estas configuraciones críticas.

**Archivo:** `apps/accounts/views_banners.py` - Vistas de configuración

---

### 3. Operaciones Masivas (Bulk)

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/files/bulk-delete/` | `media:bulk_delete` | Eliminar múltiples archivos | ⚠️ **Staff** | ✅ **Admin** |
| `/files/bulk-update/` | `media:bulk_update` | Actualizar múltiples archivos | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Las operaciones masivas pueden eliminar o modificar grandes cantidades de datos. Solo los superusuarios deberían poder realizar estas operaciones críticas.

**Archivo:** `apps/media/views.py` - Funciones `media_file_bulk_delete` y `media_file_bulk_update`

---

### 4. Publicación/Despublicación de Eventos

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/<int:pk>/toggle-publish/` | `events:toggle_publish` | Publicar/despublicar evento | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** La publicación/despublicación de eventos afecta directamente la visibilidad pública del sitio. Solo los superusuarios deberían poder controlar qué eventos son visibles públicamente.

**Archivo:** `apps/events/views.py` - `EventTogglePublishView`

---

### 5. Eliminación de Datos Maestros Críticos

#### 5.1. Ubicaciones Base (Países, Estados, Ciudades)

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/locations/countries/<int:pk>/delete/` | `locations:country_delete` | Eliminar país | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/states/<int:pk>/delete/` | `locations:state_delete` | Eliminar estado | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/cities/<int:pk>/delete/` | `locations:city_delete` | Eliminar ciudad | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/countries/<int:pk>/delete/` | `locations:admin_country_delete` | Eliminar país (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/states/<int:pk>/delete/` | `locations:admin_state_delete` | Eliminar estado (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/cities/<int:pk>/delete/` | `locations:admin_city_delete` | Eliminar ciudad (admin) | ⚠️ **Staff** | ✅ **Admin** |

#### 5.2. Configuración del Sistema (Temporadas, Reglas, Sitios)

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/locations/seasons/<int:pk>/delete/` | `locations:season_delete` | Eliminar temporada | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/rules/<int:pk>/delete/` | `locations:rule_delete` | Eliminar regla | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/sites/<int:pk>/delete/` | `locations:site_delete` | Eliminar sitio | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/seasons/<int:pk>/delete/` | `locations:admin_season_delete` | Eliminar temporada (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/rules/<int:pk>/delete/` | `locations:admin_rule_delete` | Eliminar regla (admin) | ⚠️ **Staff** | ✅ **Admin** |
| `/locations/admin/sites/<int:pk>/delete/` | `locations:admin_site_delete` | Eliminar sitio (admin) | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** La eliminación de datos maestros puede afectar cascada a múltiples registros relacionados (eventos, jugadores, hoteles, etc.). Solo los superusuarios deberían poder eliminar estos datos críticos.

**Archivos:**
- `apps/locations/views.py` - Vistas DeleteView
- `apps/locations/views_admin.py` - Vistas Admin DeleteView

---

### 6. Eliminación de Eventos

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/<int:pk>/delete/` | `events:delete` | Eliminar evento | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Los eventos pueden tener múltiples relaciones (asistencias, pagos, reservas de hotel, etc.). La eliminación de eventos puede causar pérdida de datos importantes. Solo los superusuarios deberían poder eliminar eventos.

**Archivo:** `apps/events/views.py` - `EventDeleteView`

---

### 7. Eliminación de Divisiones

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/events/divisions/<int:pk>/delete/` | `events:division_delete` | Eliminar división | ⚠️ **Staff** | ✅ **Admin** |

**Razón:** Las divisiones son parte fundamental de la estructura de eventos. Su eliminación puede afectar múltiples eventos y jugadores. Solo los superusuarios deberían poder eliminar divisiones.

**Archivo:** `apps/events/views.py` - `DivisionDeleteView`

---

## 🔴 PRIORIDAD ALTA: URLs que Requieren SOLO Staff

**Estas URLs son críticas y deberían requerir SOLO staff (no manager ni parent):**

### 1. Aprobación de Verificaciones de Edad

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:pk>/approve-verification/` | `accounts:approve_age_verification` | Aprobar/rechazar verificación | ⚠️ **Solo Login** (verifica Staff/Manager) | ✅ **SOLO Staff** |

**Razón:** La aprobación de verificaciones de edad es una operación administrativa crítica que afecta la elegibilidad de los jugadores. Solo el staff administrativo debería poder aprobar/rechazar verificaciones, no los managers de equipos.

**Archivo:** `apps/accounts/views_private.py` - `approve_age_verification`

**Cambio requerido:** Eliminar verificación de manager, requerir solo `is_staff` o `is_superuser`

---

## 🟡 PRIORIDAD MEDIA: URLs que Requieren Staff/Manager/Parent

**Estas URLs son críticas pero pueden ser accesibles para staff, managers y padres con verificación adecuada:**

### 1. Visualización de Datos Sensibles de Jugadores

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:pk>/` | `accounts:player_detail` | Detalle de jugador | ⚠️ **Solo Login** | ✅ **Staff/Manager/Parent/Owner** |

**Razón:** Actualmente cualquier usuario autenticado puede ver el detalle de cualquier jugador, incluyendo información sensible. Debería restringirse a:
- Staff/Admin (pueden ver todos)
- Manager del equipo del jugador
- Padre/acudiente del jugador
- El propio jugador

**Archivo:** `apps/accounts/views_private.py` - `PlayerDetailView`

**Cambio requerido:** Agregar verificación de permisos en `dispatch` o `get_object`

---

### 2. Acceso a Documentos de Verificación de Edad

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:player_id>/age-verification-document/` | `accounts:serve_age_verification_document` | Servir documento verificación | ⚠️ **Solo Login** (verifica internamente) | ✅ **Staff/Manager/Parent** |

**Razón:** La función verifica permisos internamente (staff, manager, o padre del jugador), pero debería usar un decorador o mixin más explícito.

**Archivo:** `apps/accounts/views_private.py` - `serve_age_verification_document`

**Cambio requerido:** Usar decorador personalizado para mayor claridad y seguridad

---

### 3. Edición de Jugadores

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/players/<int:pk>/edit/` | `accounts:player_edit` | Editar jugador | ⚠️ **Solo Login** (verifica internamente) | ✅ **Staff/Manager/Parent** |

**Razón:** La vista verifica permisos en `dispatch` (staff, manager, o padre del jugador), pero debería usar un mixin más explícito como `OwnerOrStaffRequiredMixin`.

**Archivo:** `apps/accounts/views_private.py` - `PlayerUpdateView`

**Cambio requerido:** Cambiar a `OwnerOrStaffRequiredMixin` para mayor claridad y seguridad

---

## 🟡 PRIORIDAD MEDIA: URLs que Requieren Staff/Manager

**Estas URLs son críticas pero pueden ser accesibles para staff y managers con verificación adecuada:**

### 1. Edición de Equipos

| URL | Nombre | Descripción | Requiere Actual | Requiere Ideal |
|-----|--------|-------------|-----------------|----------------|
| `/accounts/teams/<int:pk>/edit/` | `accounts:team_edit` | Editar equipo | ⚠️ **Solo Login** (verifica internamente) | ✅ **Staff/Manager** |

**Razón:** La vista verifica permisos en `dispatch` (staff o manager del equipo), pero debería usar un mixin más explícito como `OwnerOrStaffRequiredMixin`.

**Archivo:** `apps/accounts/views_private.py` - `TeamUpdateView`

**Cambio requerido:** Cambiar a `OwnerOrStaffRequiredMixin` para mayor claridad y seguridad

---

## 📝 Notas de Implementación

### Para URLs que requieren SOLO Admin (Superuser)

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
   - `UserListView` en `apps/accounts/views_private.py`
   - `HomeContentAdminView` en `apps/accounts/views_banners.py`
   - `ScheduleSettingsUpdateView` en `apps/accounts/views_banners.py`
   - `ShowcaseSettingsUpdateView` en `apps/accounts/views_banners.py`
   - `ContactSettingsUpdateView` en `apps/accounts/views_banners.py`
   - `EventTogglePublishView` en `apps/events/views.py`
   - `EventDeleteView` en `apps/events/views.py`
   - `DivisionDeleteView` en `apps/events/views.py`
   - Todas las vistas DeleteView en `apps/locations/views.py` y `apps/locations/views_admin.py`

3. **Para funciones (no clases), usar decorador:**
   ```python
   from django.contrib.auth.decorators import user_passes_test

   @user_passes_test(lambda u: u.is_superuser)
   @require_http_methods(["POST"])
   def media_file_bulk_delete(request):
       # ...
   ```

### Para URLs que requieren SOLO Staff

1. **Modificar `approve_age_verification`** en `apps/accounts/views_private.py`:
   ```python
   @login_required
   @require_POST
   def approve_age_verification(request, pk):
       player = get_object_or_404(Player, pk=pk)
       user = request.user

       # SOLO staff puede aprobar verificaciones
       if not (user.is_staff or user.is_superuser):
           messages.error(request, _("Solo el staff puede aprobar verificaciones."))
           return redirect("accounts:age_verification_list")

       # ... resto del código
   ```

### Para URLs que requieren Staff/Manager/Parent

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

2. **PlayerUpdateView** - Cambiar a `OwnerOrStaffRequiredMixin`:
   ```python
   class PlayerUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
       # ...
   ```

3. **serve_age_verification_document** - Usar decorador personalizado:
   ```python
   @user_passes_test(lambda u: u.is_authenticated)
   def serve_age_verification_document(request, player_id):
       # Verificación de permisos existente...
   ```

### Para URLs que requieren Staff/Manager

1. **TeamUpdateView** - Cambiar a `OwnerOrStaffRequiredMixin`:
   ```python
   class TeamUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
       # ...
   ```

---

## 🎯 Priorización de Cambios

### Fase 1 - Crítico (Implementar Inmediatamente)
1. ✅ `/accounts/players/<int:pk>/` - Visualización de datos sensibles sin verificación
2. ✅ `/accounts/players/<int:pk>/approve-verification/` - Aprobación solo para staff
3. ✅ `/accounts/users/` - Gestión de usuarios solo para admin
4. ✅ `/events/<int:pk>/delete/` - Eliminación de eventos solo para admin
5. ✅ `/files/bulk-delete/` y `/files/bulk-update/` - Operaciones masivas solo para admin

### Fase 2 - Alto (Implementar Pronto)
1. ✅ Configuración del sistema (4 URLs) - Solo admin
2. ✅ Eliminación de datos maestros (~12 URLs) - Solo admin
3. ✅ Publicación/despublicación de eventos - Solo admin
4. ✅ Eliminación de divisiones - Solo admin

### Fase 3 - Medio (Mejoras de Seguridad)
1. ✅ Edición de jugadores - Usar `OwnerOrStaffRequiredMixin`
2. ✅ Edición de equipos - Usar `OwnerOrStaffRequiredMixin`
3. ✅ Acceso a documentos - Usar decorador explícito

---

## 📊 Estadísticas

- **Total de URLs críticas:** ~27 URLs
- **URLs que requieren Admin:** ~22 URLs
- **URLs que requieren Staff:** 1 URL
- **URLs que requieren Staff/Manager/Parent:** 3 URLs
- **URLs que requieren Staff/Manager:** 1 URL

---

**Nota:** Este documento se actualiza automáticamente cuando se identifican nuevas URLs críticas. Para más detalles sobre todas las URLs del sistema, consultar `URLS_ADMIN_DASHBOARD.md` y `URLS_BACKEND_COMPLETO.md`.



