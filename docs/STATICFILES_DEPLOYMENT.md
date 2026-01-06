# Guía de Despliegue de Staticfiles

## Problema

Cuando haces `git pull` en el servidor, los staticfiles no se actualizan automáticamente porque:
- Los archivos fuente en `/static` cambian
- Los staticfiles en `/staticfiles` están en `.gitignore` (correcto)
- El `CompressedManifestStaticFilesStorage` genera archivos con hashes que deben regenerarse
- El archivo `staticfiles.json` tiene referencias a archivos viejos

## Solución

### Opción 1: Script Automático (Recomendado)

Después de hacer `git pull`, ejecuta:

```bash
./scripts/post_deploy.sh
```

O el script completo de despliegue:

```bash
./scripts/deploy.sh
```

### Opción 2: Manual

Después de cada `git pull` en el servidor:

```bash
# Limpiar staticfiles antiguos
rm -rf staticfiles/*

# Recolectar staticfiles
python manage.py collectstatic --noinput
```

### Opción 3: Git Hook (Automático)

Crea un hook post-merge en `.git/hooks/post-merge`:

```bash
#!/bin/bash
# Ejecutar después de git pull/merge
cd "$(git rev-parse --show-toplevel)"
./scripts/post_deploy.sh
```

Hacerlo ejecutable:
```bash
chmod +x .git/hooks/post-merge
```

### Opción 4: Docker Compose (Si usas Docker)

Agrega al `docker-compose.yml`:

```yaml
services:
  web:
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate &&
             gunicorn nsc_admin.wsgi:application --bind 0.0.0.0:8000"
```

## Configuración Actual

### Local (settings.py)
- `STATICFILES_STORAGE`: No configurado (usa el default)
- Los archivos se sirven directamente desde `/static`

### Producción (settings_prod.py)
- `STATICFILES_STORAGE`: `whitenoise.storage.CompressedManifestStaticFilesStorage`
- Genera archivos con hashes: `admin.js` → `admin.abc123.js`
- Crea `staticfiles.json` con el mapeo de nombres

## Por qué es necesario

El `CompressedManifestStaticFilesStorage`:
1. Comprime los archivos (gzip)
2. Agrega hashes a los nombres para cache busting
3. Genera un archivo `staticfiles.json` que mapea nombres originales → hasheados
4. Si los archivos fuente cambian pero no se regenera, los hashes no coinciden

## Verificación

Para verificar que los staticfiles están actualizados:

```bash
# Ver el contenido de staticfiles.json
cat staticfiles/staticfiles.json | head -20

# Verificar que los archivos existen
ls -la staticfiles/js/admin.js*
ls -la staticfiles/css/admin.css*
```

## Troubleshooting

### Los archivos no se actualizan
1. Verifica que `STATICFILES_DIRS` apunta a `/static`
2. Verifica que `STATIC_ROOT` apunta a `/staticfiles`
3. Asegúrate de ejecutar `collectstatic` después de cada pull

### Errores de 404 en archivos estáticos
1. Verifica que `collectstatic` se ejecutó correctamente
2. Verifica que el servidor web (nginx/apache) apunta a `/staticfiles`
3. Verifica los permisos de la carpeta `staticfiles`

### Archivos con hashes no encontrados
1. Limpia completamente `staticfiles/`
2. Ejecuta `collectstatic` de nuevo
3. Verifica que `staticfiles.json` existe y está actualizado

