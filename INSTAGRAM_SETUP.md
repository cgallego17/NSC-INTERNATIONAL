# Configuración de Instagram Feed

Esta guía te ayudará a configurar la integración de Instagram para mostrar tus últimos posts en el home.

## Opciones de Integración

### Opción 1: Instagram Basic Display API (Recomendado)

1. **Crear una App en Facebook Developers:**
   - Ve a https://developers.facebook.com/
   - Crea una nueva app
   - Agrega el producto "Instagram Basic Display"

2. **Configurar OAuth:**
   - Agrega tu dominio en "Valid OAuth Redirect URIs"
   - Obtén tu `App ID` y `App Secret`

3. **Obtener Access Token:**
   - Sigue el proceso de autenticación OAuth
   - Obtén un token de acceso de larga duración

4. **Configurar en Django:**
   Agrega estas variables a tu archivo `.env` o `settings.py`:
   ```python
   INSTAGRAM_USERNAME = "tu_username"
   INSTAGRAM_ACCESS_TOKEN = "tu_access_token"
   INSTAGRAM_APP_ID = "tu_app_id"
   INSTAGRAM_APP_SECRET = "tu_app_secret"
   ```

### Opción 2: Instagram Graph API (Para cuentas de negocio)

1. **Conectar Instagram Business Account a Facebook:**
   - Tu cuenta de Instagram debe ser una cuenta de negocio
   - Conéctala a una página de Facebook

2. **Obtener Access Token:**
   - Usa Facebook Graph API Explorer
   - Obtén un token con permisos `instagram_basic` y `pages_read_engagement`

3. **Configurar en Django:**
   ```python
   INSTAGRAM_USERNAME = "tu_username"
   INSTAGRAM_ACCESS_TOKEN = "tu_access_token"
   ```

### Opción 3: Usar un servicio de terceros

Puedes usar servicios como:
- **Instagram Feed** (https://elfsight.com/instagram-feed/)
- **SnapWidget** (https://snapwidget.com/)
- **Juicer** (https://www.juicer.io/)

Estos servicios proporcionan widgets que puedes integrar fácilmente.

## Instalación de dependencias

Si usas la API directamente, necesitarás `requests`:

```bash
pip install requests
```

## Verificación

1. Asegúrate de que las variables estén configuradas en `settings.py`
2. Visita `/accounts/api/instagram/posts/` para verificar que la API funciona
3. Recarga la página del home para ver los posts de Instagram

## Notas

- Los tokens de Instagram tienen una duración limitada
- Necesitarás renovar el token periódicamente
- Para producción, considera usar un servicio de caché para los posts
- El feed mostrará eventos como fallback si no hay posts de Instagram disponibles

## Solución de problemas

Si no ves los posts de Instagram:
1. Verifica que el token sea válido
2. Revisa la consola del navegador para errores
3. Verifica que la API esté respondiendo en `/accounts/api/instagram/posts/`
4. Asegúrate de que `INSTAGRAM_USERNAME` esté configurado correctamente


