# 🔗 Guía: Cómo Crear el Webhook de Stripe

## 📋 Paso a Paso

### 1. **Acceder al Dashboard de Stripe**

1. Ve a [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Inicia sesión con tu cuenta de Stripe
3. Asegúrate de estar en el **modo correcto**:
   - **Test mode** (para desarrollo/pruebas) - botón en la esquina superior derecha
   - **Live mode** (para producción)

### 2. **Navegar a Webhooks**

1. En el menú lateral izquierdo, busca **"Developers"**
2. Haz clic en **"Webhooks"**
3. Verás una lista de webhooks existentes (si hay alguno)

### 3. **Crear Nuevo Endpoint**

1. Haz clic en el botón **"+ Add endpoint"** (o "Add endpoint" en español)
2. Se abrirá un formulario para crear el webhook

### 4. **Configurar el Endpoint**

#### a) **Endpoint URL**
Ingresa la URL completa de tu webhook:

**Para desarrollo local (usando Stripe CLI):**
```
http://localhost:8000/accounts/stripe/webhook/
```

**Para producción:**
```
https://tudominio.com/accounts/stripe/webhook/
```

**⚠️ IMPORTANTE:**
- La URL debe ser **HTTPS** en producción
- Debe terminar con `/accounts/stripe/webhook/`
- No debe tener espacios ni caracteres especiales

#### b) **Description (Opcional)**
Puedes agregar una descripción:
```
NSC International - Event Checkout Webhook
```

#### c) **Events to send**
Selecciona los eventos que quieres recibir. Para este sistema, necesitas:

**Eventos requeridos:**
- ✅ `checkout.session.completed` - Cuando un pago se completa
- ✅ `checkout.session.expired` - Cuando una sesión de checkout expira

**Cómo seleccionar:**
1. Haz clic en **"Select events"** o **"Seleccionar eventos"**
2. Busca en la lista o expande la sección **"Checkout"**
3. Marca las casillas:
   - ☑ `checkout.session.completed`
   - ☑ `checkout.session.expired`
4. Haz clic en **"Add events"** o **"Agregar eventos"**

### 5. **Crear el Endpoint**

1. Revisa que la URL y los eventos estén correctos
2. Haz clic en **"Add endpoint"** o **"Agregar endpoint"**
3. Stripe creará el webhook y te mostrará la página de detalles

### 6. **Obtener el Signing Secret**

**⚠️ CRÍTICO: Este paso es muy importante**

1. En la página de detalles del webhook, busca la sección **"Signing secret"**
2. Verás algo como:
   ```
   whsec_1234567890abcdef...
   ```
3. Haz clic en **"Reveal"** o **"Revelar"** para ver el secreto completo
4. **Copia el secreto completo** (empieza con `whsec_`)

### 7. **Configurar en tu Aplicación**

Agrega el secreto a tus variables de entorno:

**En desarrollo (.env o variables de entorno):**
```bash
STRIPE_WEBHOOK_SECRET=whsec_tu_secreto_aqui
```

**En producción (servidor):**
```bash
export STRIPE_WEBHOOK_SECRET=whsec_tu_secreto_aqui
```

O en tu archivo de configuración del servidor (Docker, systemd, etc.)

### 8. **Verificar el Webhook**

#### Opción A: Usar Stripe CLI (Recomendado para desarrollo)

1. **Instalar Stripe CLI:**
   - Windows: Descargar de [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)
   - Mac: `brew install stripe/stripe-cli/stripe`
   - Linux: Ver instrucciones en la documentación

2. **Autenticarse:**
   ```bash
   stripe login
   ```

3. **Escuchar eventos localmente:**
   ```bash
   stripe listen --forward-to http://localhost:8000/accounts/stripe/webhook/
   ```

   Esto te dará un nuevo `whsec_...` para usar en desarrollo local.

4. **Probar el webhook:**
   ```bash
   stripe trigger checkout.session.completed
   ```

#### Opción B: Probar desde el Dashboard

1. En la página de detalles del webhook
2. Haz clic en **"Send test webhook"** o **"Enviar webhook de prueba"**
3. Selecciona el evento `checkout.session.completed`
4. Haz clic en **"Send test webhook"**
5. Revisa los logs de tu servidor para verificar que se recibió

---

## 🔍 Verificar que Funciona

### 1. **Revisar Logs del Servidor**

Cuando se reciba un webhook, deberías ver en los logs:
- Request POST a `/accounts/stripe/webhook/`
- Status 200 (si todo está bien)
- O errores si hay problemas

### 2. **Revisar en Stripe Dashboard**

1. Ve a **Developers > Webhooks**
2. Haz clic en tu webhook
3. Ve a la pestaña **"Events"** o **"Eventos"**
4. Verás todos los eventos enviados y sus respuestas:
   - ✅ Verde = Éxito (200)
   - ❌ Rojo = Error (400, 500, etc.)

### 3. **Probar con un Pago Real (Test Mode)**

1. Configura claves de **test** en tu aplicación
2. Crea un evento de prueba
3. Intenta hacer un pago con tarjeta de prueba: `4242 4242 4242 4242`
4. Completa el pago
5. Verifica que:
   - El webhook recibió el evento `checkout.session.completed`
   - Se creó el `StripeEventCheckout` con status `"paid"`
   - Se crearon las reservas y asistencias

---

## 🛠️ Solución de Problemas

### Error: "No signatures found matching the expected signature"

**Causa:** El `STRIPE_WEBHOOK_SECRET` no coincide con el secreto del webhook.

**Solución:**
1. Verifica que copiaste el secreto completo (empieza con `whsec_`)
2. Asegúrate de que no hay espacios extra
3. Si usas Stripe CLI, usa el secreto que te da el comando `stripe listen`

### Error: 400 Bad Request

**Causa:** El payload o la firma no son válidos.

**Solución:**
1. Verifica que la URL del webhook es correcta
2. Asegúrate de que `STRIPE_WEBHOOK_SECRET` está configurado
3. Revisa los logs del servidor para más detalles

### El webhook no se recibe

**Posibles causas:**
1. **Firewall/Proxy:** Bloquea las peticiones de Stripe
2. **URL incorrecta:** Verifica que la URL sea accesible públicamente
3. **HTTPS requerido:** En producción, Stripe solo envía a URLs HTTPS
4. **Servidor caído:** Verifica que tu servidor esté funcionando

**Solución:**
- Usa `stripe listen` para desarrollo local
- Verifica que tu servidor esté accesible desde internet
- Revisa los logs de Stripe Dashboard para ver qué error devuelve

### Webhook recibido pero no procesa el pago

**Causa:** El `StripeEventCheckout` no existe o hay un error en el código.

**Solución:**
1. Verifica que se creó el checkout antes del pago
2. Revisa los logs del servidor para ver errores
3. Verifica que el `stripe_session_id` coincide

---

## 📝 Notas Importantes

1. **Test vs Live:**
   - Los webhooks de **test mode** solo funcionan con claves de test
   - Los webhooks de **live mode** solo funcionan con claves de producción
   - Cada modo tiene su propio secreto de webhook

2. **Múltiples Entornos:**
   - Puedes crear webhooks separados para desarrollo, staging y producción
   - Cada uno tendrá su propio `whsec_...`

3. **Seguridad:**
   - **NUNCA** compartas el `STRIPE_WEBHOOK_SECRET` públicamente
   - No lo commitees al repositorio
   - Úsalo solo en variables de entorno

4. **Timeout:**
   - Stripe espera una respuesta en menos de 20 segundos
   - Si tu servidor tarda más, Stripe reintentará automáticamente

---

## ✅ Checklist Final

- [ ] Webhook creado en Stripe Dashboard
- [ ] URL configurada correctamente (HTTPS en producción)
- [ ] Eventos seleccionados: `checkout.session.completed` y `checkout.session.expired`
- [ ] Signing secret copiado
- [ ] `STRIPE_WEBHOOK_SECRET` configurado en variables de entorno
- [ ] Webhook probado con evento de prueba
- [ ] Verificado que los pagos se procesan correctamente

---

## 🔗 Enlaces Útiles

- [Documentación de Webhooks de Stripe](https://stripe.com/docs/webhooks)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Dashboard de Stripe](https://dashboard.stripe.com/webhooks)
- [Eventos de Checkout](https://stripe.com/docs/api/events/types#event_types-checkout.session.completed)

