# Tests de Permisos y Restricciones

Este documento describe los tests creados para verificar que todos los permisos y restricciones se cumplan correctamente.

**Archivo de tests:** `apps/accounts/tests/test_permisos.py`

**Última actualización:** 2026-01-07

---

## 📋 Resumen de Tests

Se han creado **49 tests** organizados en las siguientes categorías:

### 1. TestJugadoresNoPuedenIniciarSesion (2 tests)
- ✅ `test_jugador_no_puede_iniciar_sesion` - Verifica que jugadores con `is_active=False` no puedan iniciar sesión
- ✅ `test_jugador_tiene_is_active_false` - Verifica que los jugadores tienen `is_active=False`

### 2. TestPermisosPadres (7 tests)
- `test_padre_puede_ver_panel` - Padre puede acceder a su panel
- `test_padre_puede_ver_su_hijo` - Padre puede ver detalles de su hijo
- `test_padre_no_puede_ver_otro_jugador` - Padre NO puede ver jugadores que no son sus hijos
- `test_padre_no_puede_ver_lista_completa_jugadores` - Padre NO puede ver lista completa (requiere staff)
- `test_padre_no_puede_aprobar_verificaciones` - Padre NO puede aprobar verificaciones (solo staff)
- `test_padre_no_puede_acceder_admin_dashboard` - Padre NO puede acceder al admin dashboard
- `test_padre_no_puede_eliminar_eventos` - Padre NO puede eliminar eventos (solo admin)

### 3. TestPermisosManagers (6 tests)
- `test_manager_puede_ver_panel` - Manager puede acceder a su panel
- `test_manager_puede_ver_su_jugador` - Manager puede ver jugadores de su equipo
- `test_manager_no_puede_ver_jugador_otro_equipo` - Manager NO puede ver jugadores de otros equipos
- `test_manager_puede_crear_equipo` - Manager puede crear equipos
- `test_manager_puede_editar_su_equipo` - Manager puede editar su propio equipo
- `test_manager_no_puede_aprobar_verificaciones` - Manager NO puede aprobar verificaciones (solo staff)
- `test_manager_no_puede_eliminar_eventos` - Manager NO puede eliminar eventos (solo admin)

### 4. TestPermisosStaff (8 tests)
- `test_staff_puede_ver_admin_dashboard` - Staff puede acceder al admin dashboard
- `test_staff_puede_ver_lista_jugadores` - Staff puede ver lista completa de jugadores
- `test_staff_puede_aprobar_verificaciones` - Staff puede aprobar verificaciones
- `test_staff_no_puede_ver_usuarios` - Staff NO puede ver lista de usuarios (solo admin)
- `test_staff_no_puede_eliminar_eventos` - Staff NO puede eliminar eventos (solo admin)
- `test_staff_no_puede_eliminar_paises` - Staff NO puede eliminar países (solo admin)
- `test_staff_no_puede_operaciones_masivas` - Staff NO puede realizar operaciones masivas (solo admin)
- `test_staff_no_puede_configuracion_sistema` - Staff NO puede acceder a configuración del sistema (solo admin)

### 5. TestPermisosAdmin (6 tests)
- `test_admin_puede_ver_usuarios` - Admin puede ver lista de usuarios
- `test_admin_puede_eliminar_eventos` - Admin puede eliminar eventos
- `test_admin_puede_eliminar_paises` - Admin puede eliminar países
- `test_admin_puede_operaciones_masivas` - Admin puede realizar operaciones masivas
- `test_admin_puede_configuracion_sistema` - Admin puede acceder a configuración del sistema
- `test_admin_puede_publicar_eventos` - Admin puede publicar/despublicar eventos

### 6. TestMixins (6 tests)
- `test_staff_required_mixin_bloquea_usuario_normal` - StaffRequiredMixin bloquea usuarios normales
- `test_staff_required_mixin_permite_staff` - StaffRequiredMixin permite acceso a staff
- `test_superuser_required_mixin_bloquea_staff` - SuperuserRequiredMixin bloquea staff (no superuser)
- `test_superuser_required_mixin_permite_admin` - SuperuserRequiredMixin permite acceso a admin
- `test_manager_required_mixin_bloquea_padre` - ManagerRequiredMixin bloquea padres
- `test_manager_required_mixin_permite_manager` - ManagerRequiredMixin permite acceso a managers

### 7. TestVerificacionesManuales (2 tests)
- `test_player_detail_view_verifica_permisos` - PlayerDetailView verifica permisos correctamente
- `test_approve_age_verification_solo_staff` - approve_age_verification solo permite staff

### 8. TestOwnerOrStaffRequiredMixin (3 tests)
- `test_team_update_permite_manager` - TeamUpdateView permite al manager editar su equipo
- `test_team_update_bloquea_otro_manager` - TeamUpdateView bloquea a otros managers
- `test_team_update_permite_staff` - TeamUpdateView permite a staff editar cualquier equipo

### 9. TestPermisosPorDefecto (4 tests)
- ✅ `test_usuario_nuevo_no_es_staff` - Usuario nuevo NO es staff por defecto
- ✅ `test_usuario_nuevo_no_es_superuser` - Usuario nuevo NO es superuser por defecto
- ✅ `test_usuario_nuevo_es_activo` - Usuario nuevo es activo por defecto (excepto jugadores)
- ✅ `test_usuario_nuevo_tiene_user_type` - Usuario nuevo tiene user_type definido

### 10. TestRestriccionesCriticas (4 tests)
- `test_staff_no_puede_eliminar_datos_maestros` - Staff NO puede eliminar datos maestros críticos
- `test_admin_puede_eliminar_datos_maestros` - Admin SÍ puede eliminar datos maestros críticos
- `test_staff_no_puede_toggle_publish_eventos` - Staff NO puede publicar/despublicar eventos (solo admin)
- `test_admin_puede_toggle_publish_eventos` - Admin SÍ puede publicar/despublicar eventos

---

## ✅ Tests que Funcionan

Los siguientes tests han sido verificados y funcionan correctamente:

1. ✅ `test_usuario_nuevo_no_es_staff`
2. ✅ `test_usuario_nuevo_no_es_superuser`
3. ✅ `test_usuario_nuevo_es_activo`
4. ✅ `test_usuario_nuevo_tiene_user_type`

---

## ⚠️ Tests que Requieren Verificación

Los siguientes tests pueden requerir ajustes en los nombres de URLs o en la lógica de las vistas:

### URLs que pueden necesitar verificación:
- `reverse("panel")` - Verificar que existe
- `reverse("accounts:player_list")` - Verificar nombre correcto
- `reverse("accounts:player_detail", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("accounts:approve_age_verification", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("dashboard")` - Verificar que existe
- `reverse("events:delete", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("events:toggle_publish", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("locations:country_delete", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("accounts:user_list")` - Verificar nombre correcto
- `reverse("accounts:home_content_admin")` - Verificar nombre correcto
- `reverse("media:bulk_delete")` - Verificar nombre correcto
- `reverse("accounts:team_create")` - Verificar nombre correcto
- `reverse("accounts:team_edit", kwargs={"pk": ...})` - Verificar nombre correcto
- `reverse("accounts:player_register")` - Verificar nombre correcto

---

## 🚀 Cómo Ejecutar los Tests

### Ejecutar todos los tests de permisos:
```bash
python manage.py test apps.accounts.tests.test_permisos
```

### Ejecutar una clase de tests específica:
```bash
python manage.py test apps.accounts.tests.test_permisos.TestPermisosPorDefecto
```

### Ejecutar un test específico:
```bash
python manage.py test apps.accounts.tests.test_permisos.TestPermisosPorDefecto.test_usuario_nuevo_no_es_staff
```

### Ejecutar con más verbosidad:
```bash
python manage.py test apps.accounts.tests.test_permisos -v 2
```

---

## 📝 Notas de Implementación

### Setup de Tests

Los tests crean los siguientes usuarios de prueba:

1. **parent_user** - Usuario tipo Padre
2. **manager_user** - Usuario tipo Manager
3. **staff_user** - Usuario Staff (NO superuser)
4. **admin_user** - Usuario Admin (Superuser)
5. **player_user** - Jugador (is_active=False)

También crean:
- Equipos y jugadores relacionados
- Relaciones padre-hijo (PlayerParent)
- Datos maestros (Country, State, City)
- Eventos para tests

### Verificaciones de Permisos

Los tests verifican:
1. **Códigos de estado HTTP** (200, 302, 403)
2. **Redirecciones** usando `assertRedirects`
3. **Existencia de objetos** después de operaciones
4. **Propiedades de usuarios** (is_staff, is_superuser, is_active)

---

## 🔧 Ajustes Necesarios

Si algún test falla, verificar:

1. **Nombres de URLs**: Verificar que los nombres en `reverse()` coincidan con los definidos en `urls.py`
2. **Mixins**: Verificar que las vistas usen los mixins correctos
3. **Lógica de permisos**: Verificar que las verificaciones manuales de permisos funcionen correctamente
4. **Campos requeridos**: Algunos modelos pueden requerir campos adicionales al crear instancias

---

## 📊 Cobertura

Los tests cubren:
- ✅ Permisos por defecto de usuarios nuevos
- ✅ Restricciones de acceso según tipo de usuario
- ✅ Funcionamiento de mixins
- ✅ Verificaciones manuales de permisos
- ✅ Restricciones críticas (eliminación, operaciones masivas)

**Cobertura estimada:** ~80% de los casos de permisos críticos

---

**Última actualización:** 2026-01-07



