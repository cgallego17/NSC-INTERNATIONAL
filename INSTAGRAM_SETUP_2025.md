# Configuración de Instagram Feed - 2025

## ⚠️ Cambios Importantes

**Instagram Basic Display API fue deprecada el 4 de diciembre de 2024.** Ya no está disponible para cuentas personales.

## Opciones Disponibles (2025)

### Opción 1: Instagram Graph API (Recomendado para cuentas Business/Creator)

**Requisitos:**
- Tu cuenta de Instagram debe ser **Business** o **Creator**
- Debe estar vinculada a una **página de Facebook**
- Necesitas crear una app en [Facebook Developers](https://developers.facebook.com/)

**Pasos:**

1. **Convertir cuenta a Business/Creator:**
   - Abre Instagram app → Perfil → Menú (☰) → Configuración
   - Ve a "Cuenta" → "Cambiar a cuenta profesional"
   - Selecciona "Negocio" o "Creador"

2. **Vincular a Facebook:**
   - En Configuración → "Cuenta" → "Páginas"
   - Vincula tu cuenta a una página de Facebook

3. **Crear App en Facebook Developers:**
   - Ve a https://developers.facebook.com/
   - Crea una nueva app
   - Agrega el producto "Instagram Graph API"
   - Obtén tu `App ID` y `App Secret`

4. **Obtener Access Token:**
   - Usa Facebook Graph API Explorer
   - Obtén permisos: `instagram_basic`, `pages_read_engagement`
   - Genera un token de larga duración

5. **Configurar en Django:**
   ```python
   INSTAGRAM_USERNAME = "ncs_international"
   INSTAGRAM_ACCESS_TOKEN = "tu_access_token_aqui"
   INSTAGRAM_APP_ID = "tu_app_id"
   INSTAGRAM_APP_SECRET = "tu_app_secret"
   ```

### Opción 2: Servicios de Terceros (Más Fácil)

#### A. RSS.app (Gratis con limitaciones)

1. Ve a https://rss.app/
2. Genera un RSS feed de Instagram:
   - URL: `https://www.instagram.com/ncs_international/`
   - Genera el feed
3. Obtén la URL del RSS feed
4. Configura en Django para parsear el RSS

#### B. SnapWidget (Gratis con limitaciones)

1. Ve a https://snapwidget.com/
2. Crea un widget de Instagram
3. Obtén el código de embed
4. Integra en tu template

#### C. Elfsight Instagram Feed (Gratis con marca de agua)

1. Ve a https://elfsight.com/instagram-feed/
2. Crea un widget
3. Obtén el código JavaScript
4. Integra en tu template

### Opción 3: Widget Embebido Directo

Puedes usar el widget embebido de Instagram directamente:

```html
<iframe src="https://www.instagram.com/ncs_international/embed/" 
        width="100%" 
        height="600" 
        frameborder="0" 
        scrolling="no">
</iframe>
```

## Implementación Actual

El código actual intenta (en orden):
1. **API oficial de Instagram Graph API** (si hay token configurado y cuenta Business/Creator)
2. **RSS Feed** (desde servicios como RSS.app)
3. **Scraping HTML** (puede no funcionar debido a restricciones de Instagram)

## Solución Rápida: Usar Widget de Terceros

### Opción A: RSS.app (Recomendado - Gratis)

1. Ve a https://rss.app/
2. Crea una cuenta gratuita
3. Genera un RSS feed:
   - URL del perfil: `https://www.instagram.com/ncs_international/`
   - Genera el feed
4. **IMPORTANTE: Configura el número de posts**
   - Ve a "Feed Output" → "Customize"
   - Aumenta "Number of posts" a **12 o más** (máximo según tu plan)
   - Guarda los cambios
5. Obtén la URL del RSS feed (ej: `https://rss.app/feeds/xxxxx.xml`)
6. Configura en `settings.py`:
   ```python
   INSTAGRAM_RSS_FEED_URL = "https://rss.app/feeds/tu-feed-id.xml"
   ```

**Nota**: El plan gratuito permite hasta 25 posts. Si solo ves 6 posts, necesitas aumentar el límite en la configuración del feed en RSS.app.

### Opción B: SnapWidget (Gratis con limitaciones)

1. Ve a https://snapwidget.com/
2. Crea un widget de Instagram
3. Obtén el código de embed
4. Reemplaza el grid actual con el widget

### Opción C: Elfsight (Gratis con marca de agua)

1. Ve a https://elfsight.com/instagram-feed/
2. Crea un widget
3. Obtén el código JavaScript
4. Integra en el template

## Recomendación

Para producción, te recomiendo:

1. **Convertir la cuenta a Business/Creator** y usar Instagram Graph API
2. O usar un **servicio de terceros** como RSS.app o SnapWidget
3. O usar un **widget embebido** directamente de Instagram

## Notas Importantes

- Instagram ha restringido mucho el acceso a datos públicos
- El scraping puede violar los términos de servicio
- Los servicios de terceros pueden tener limitaciones en planes gratuitos
- La API oficial es la única forma garantizada y legal de acceder a los datos









