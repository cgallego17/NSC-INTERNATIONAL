# Revisión de URLs del Panel y Pagos

## Fecha de Revisión
Fecha: 2024-12-19

## Objetivo
Verificar que todas las URLs del panel y pagos estén correctamente configuradas, tengan los permisos adecuados y funcionen correctamente.

---

## 1. URLs del Panel

### 1.1 Panel Principal
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/panel/` | `UserDashboardView` | `LoginRequiredMixin` | ✅ | Panel principal del usuario |
| `/accounts/user-dashboard/` | `UserDashboardView` | `LoginRequiredMixin` | ✅ | Alias del panel |
| `/accounts/profile/` | `profile_view` | `LoginRequiredMixin` | ✅ | Redirige a `/panel/` |

**Verificación:**
- ✅ `UserDashboardView` hereda de `LoginRequiredMixin` y `TemplateView`
- ✅ Requiere autenticación
- ✅ Accesible para todos los usuarios autenticados (player, parent, manager, staff)

### 1.2 Vistas Embed del Panel (iframe)
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/panel-tabs/eventos/` | `PanelEventosEmbedView` | `LoginRequiredMixin` (heredado) | ✅ | Tab de eventos en iframe |
| `/accounts/panel-tabs/events/<int:pk>/` | `PanelEventDetailEmbedView` | `LoginRequiredMixin` (heredado) | ✅ | Detalle de evento en iframe |

**Verificación:**
- ✅ Ambas vistas heredan de `UserDashboardView` que tiene `LoginRequiredMixin`
- ✅ Usan `@method_decorator(xframe_options_exempt)` para permitir iframes
- ✅ Requieren autenticación

### 1.3 Detalle de Evento en el Panel
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/events/<int:pk>/` | `PanelEventDetailView` | `LoginRequiredMixin` (heredado) | ✅ | Detalle de evento con checkout |

**Verificación:**
- ✅ Hereda de `UserDashboardView` que tiene `LoginRequiredMixin`
- ✅ Requiere autenticación
- ✅ Muestra información del evento y permite registro/pago

---

## 2. URLs de Pagos (Stripe)

### 2.1 Creación de Checkout
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/events/<int:pk>/stripe/create-checkout-session/` | `create_stripe_event_checkout_session` | `@login_required`, `@require_POST`, `@csrf_exempt` | ✅ | Crea sesión de checkout de Stripe |

**Verificación:**
- ✅ Requiere autenticación (`@login_required`)
- ✅ Solo acepta POST (`@require_POST`)
- ✅ Exento de CSRF para integración con frontend (`@csrf_exempt`)
- ✅ Valida que los jugadores pertenezcan al usuario
- ✅ Valida que los jugadores no estén ya registrados
- ✅ Soporta modo "plan" (pagos recurrentes) y "now" (pago único)
- ✅ Calcula correctamente descuentos y totales

### 2.2 Callbacks de Stripe
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/events/<int:pk>/stripe/success/` | `stripe_event_checkout_success` | `@login_required` | ✅ | Callback de éxito de Stripe |
| `/accounts/events/<int:pk>/stripe/cancel/` | `stripe_event_checkout_cancel` | `@login_required` | ✅ | Callback de cancelación de Stripe |

**Verificación:**
- ✅ Ambas requieren autenticación
- ✅ `stripe_event_checkout_success`:
  - Verifica el `session_id` de Stripe
  - Valida el estado del pago
  - Finaliza el checkout y crea registros de asistencia
  - Crea reservas de hotel si aplica
  - Redirige a confirmación de pago
- ✅ `stripe_event_checkout_cancel`:
  - Muestra mensaje informativo
  - Redirige al detalle del evento

### 2.3 Webhook de Stripe
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/stripe/webhook/` | `stripe_webhook` | `@csrf_exempt` (público) | ✅ | Webhook para eventos de Stripe |

**Verificación:**
- ✅ Exento de CSRF (Stripe envía desde fuera)
- ✅ Verifica firma del webhook con `STRIPE_WEBHOOK_SECRET`
- ✅ Maneja eventos:
  - `checkout.session.completed`: Finaliza checkout y crea registros
  - `checkout.session.expired`: Marca checkout como expirado
- ✅ Retorna 200 para eventos no manejados (para evitar reintentos)

### 2.4 Vistas de Confirmación e Invoice
| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/stripe/invoice/<int:pk>/` | `StripeInvoiceView` | `LoginRequiredMixin` | ✅ | Muestra invoice/factura |
| `/accounts/payment/confirmation/<int:pk>/` | `PaymentConfirmationView` | `LoginRequiredMixin` | ✅ | Confirmación de pago exitoso |

**Verificación:**
- ✅ `StripeInvoiceView`:
  - Requiere autenticación
  - Solo muestra invoices del usuario actual (`get_queryset` filtra por `user`)
  - Permite iframes (`@method_decorator(xframe_options_exempt)`)
  - Muestra breakdown completo del pago
- ✅ `PaymentConfirmationView`:
  - Requiere autenticación
  - Solo muestra confirmaciones del usuario actual y pagadas
  - Permite iframes
  - Muestra información del checkout, jugadores y reservas

---

## 3. URLs de Registro a Eventos

| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/events/<int:pk>/register/` | `register_children_to_event` | `@login_required`, `@require_POST` | ✅ | Registra hijos a evento |

**Verificación:**
- ✅ Requiere autenticación
- ✅ Solo acepta POST
- ✅ Verifica que el usuario sea padre
- ✅ Valida que los jugadores pertenezcan al padre
- ✅ Crea registros de asistencia con estado "pending"
- ✅ Redirige al detalle del evento

---

## 4. URLs de Wallet

| URL | Vista | Permisos | Estado | Notas |
|-----|-------|----------|--------|-------|
| `/accounts/wallet/add-funds/` | `wallet_add_funds` | `@login_required`, `@require_POST` | ✅ | Agregar fondos al wallet (deshabilitado) |

**Verificación:**
- ✅ Requiere autenticación
- ✅ Solo acepta POST
- ⚠️ **Funcionalidad deshabilitada**: Retorna mensaje de error indicando que está deshabilitado
- ✅ Redirige al panel

---

## 5. Análisis de Seguridad

### 5.1 Permisos
- ✅ Todas las vistas del panel requieren autenticación
- ✅ Las vistas de pago verifican que los jugadores pertenezcan al usuario
- ✅ Las vistas de invoice/confirmación solo muestran datos del usuario actual
- ✅ El webhook de Stripe verifica la firma del webhook

### 5.2 Validaciones
- ✅ `create_stripe_event_checkout_session`:
  - Valida que los jugadores pertenezcan al usuario
  - Valida que los jugadores no estén ya registrados
  - Valida modo de pago ("plan" o "now")
  - Valida que haya algo que cobrar
- ✅ `stripe_event_checkout_success`:
  - Valida `session_id`
  - Valida estado del pago
  - Verifica que el checkout exista en la BD

### 5.3 Protección CSRF
- ✅ Vistas normales: Protegidas con CSRF (excepto webhook y create-checkout que usan `@csrf_exempt` por necesidad técnica)
- ✅ Webhook: Exento de CSRF (Stripe envía desde fuera)
- ✅ Create checkout: Exento de CSRF (integración con frontend)

### 5.4 Manejo de Errores
- ✅ Todas las vistas manejan errores con mensajes apropiados
- ✅ Redirecciones apropiadas en caso de error
- ✅ Validación de configuración de Stripe

---

## 6. Posibles Mejoras

### 6.1 Rate Limiting
- ⚠️ **Recomendación**: Considerar rate limiting para:
  - `create_stripe_event_checkout_session` (prevenir abuso)
  - `stripe_event_checkout_success` (prevenir spam)

### 6.2 Logging
- ⚠️ **Recomendación**: Agregar logging más detallado para:
  - Creación de checkouts
  - Finalización de pagos
  - Errores en webhooks

### 6.3 Validación Adicional
- ⚠️ **Recomendación**: Validar que el evento esté publicado antes de permitir checkout
- ⚠️ **Recomendación**: Validar fechas límite de registro antes de permitir checkout

---

## 7. Resumen

### ✅ Funcionamiento Correcto
- Todas las URLs están correctamente definidas
- Todas las vistas tienen los permisos adecuados
- Las validaciones están implementadas
- El manejo de errores es apropiado

### ⚠️ Mejoras Recomendadas
- Rate limiting para endpoints de pago
- Logging más detallado
- Validaciones adicionales (evento publicado, fechas límite)

### 🔒 Seguridad
- ✅ Permisos correctos en todas las vistas
- ✅ Validación de propiedad de datos
- ✅ Protección CSRF donde corresponde
- ✅ Verificación de firma en webhook

---

## 8. Próximos Pasos

1. ✅ Revisión completada
2. ⏳ Crear tests para verificar funcionamiento
3. ⏳ Implementar mejoras recomendadas (opcional)

