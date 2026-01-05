# Guía para Subir Base de Datos y Migraciones al Servidor

## Resumen

Este documento explica cómo organizar y subir la base de datos SQLite y las migraciones al servidor de producción.

## Paso 1: Organizar la Base de Datos y Migraciones

### 1.1 Organizar Base de Datos

Ejecuta el script de organización:

```bash
python scripts/organize_database_for_upload.py
```

Este script:
- ✅ Crea un backup de seguridad
- ✅ Optimiza la base de datos (VACUUM, REINDEX, ANALYZE)
- ✅ Reduce el tamaño del archivo
- ✅ Crea un paquete listo para subir con timestamp

**Resultado:** Se crea un archivo `db_upload_YYYYMMDD_HHMMSS.sqlite3` listo para subir.

### 1.2 Organizar Migraciones

Ejecuta el script de organización de migraciones:

```bash
python scripts/organize_migrations_for_upload.py
```

Este script:
- ✅ Crea un backup de todas las migraciones
- ✅ Crea un paquete con todas las migraciones
- ✅ Genera un archivo .tar.gz comprimido
- ✅ Incluye un README con instrucciones

**Resultado:** Se crea:
- Directorio: `migrations_upload/migrations_upload_YYYYMMDD_HHMMSS/`
- Archivo comprimido: `migrations_upload/migrations_upload_YYYYMMDD_HHMMSS.tar.gz`

## Paso 2: Subir Migraciones al Servidor

### Opción A: Usando SCP con archivo comprimido

```bash
# Subir el archivo comprimido
scp migrations_upload/migrations_upload_YYYYMMDD_HHMMSS.tar.gz root@tu-servidor:/tmp/

# En el servidor, descomprimir
ssh root@tu-servidor
cd /var/www/NSC-INTERNATIONAL
tar -xzf /tmp/migrations_upload_YYYYMMDD_HHMMSS.tar.gz -C apps/accounts/
```

### Opción B: Usando RSYNC con directorio

```bash
# Subir el directorio completo
rsync -avz migrations_upload/migrations_upload_YYYYMMDD_HHMMSS/ root@tu-servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/
```

### Opción C: Reemplazar migraciones específicas (0036-0038)

Si solo necesitas subir las migraciones del slug:

```bash
# Subir solo las migraciones problemáticas
scp apps/accounts/migrations/0036_add_slug_to_player.py root@tu-servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/
scp apps/accounts/migrations/0037_alter_sitesettings_dashboard_welcome_banner.py root@tu-servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/
scp apps/accounts/migrations/0038_merge_slug_and_banner.py root@tu-servidor:/var/www/NSC-INTERNATIONAL/apps/accounts/migrations/
```

**En el servidor, verifica:**
```bash
ls -la apps/accounts/migrations/ | grep -E "003[678]"
```

## Paso 3: Preparar el Servidor

**⚠️ IMPORTANTE: Antes de subir la base de datos:**

1. **Detén el servidor Django:**
   ```bash
   # En el servidor
   sudo systemctl stop gunicorn
   # O si usas supervisor
   sudo supervisorctl stop nsc
   ```

2. **Haz backup de la base de datos actual del servidor:**
   ```bash
   # En el servidor
   cd /var/www/NSC-INTERNATIONAL
   cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
   ```

## Paso 4: Subir la Base de Datos

### Opción A: Usando SCP

```bash
# Desde tu máquina local
scp db_upload_YYYYMMDD_HHMMSS.sqlite3 root@tu-servidor:/var/www/NSC-INTERNATIONAL/
```

### Opción B: Usando RSYNC (recomendado)

```bash
# Desde tu máquina local
rsync -avz --progress db_upload_YYYYMMDD_HHMMSS.sqlite3 root@tu-servidor:/var/www/NSC-INTERNATIONAL/
```

### Opción C: Usando SFTP

1. Conecta con un cliente SFTP (FileZilla, WinSCP, etc.)
2. Navega a `/var/www/NSC-INTERNATIONAL/`
3. Sube el archivo `db_upload_YYYYMMDD_HHMMSS.sqlite3`

## Paso 5: Reemplazar en el Servidor

```bash
# En el servidor
cd /var/www/NSC-INTERNATIONAL

# Reemplazar la base de datos
mv db_upload_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# Asegurar permisos correctos
chown www-data:www-data db.sqlite3
chmod 644 db.sqlite3
```

## Paso 6: Aplicar Migraciones

**⚠️ IMPORTANTE: Aplica las migraciones ANTES de reiniciar el servidor**

```bash
# En el servidor
cd /var/www/NSC-INTERNATIONAL

# Si hay conflictos de migraciones, ejecuta primero:
python scripts/fix_migration_0036.py

# Aplicar migraciones
python manage.py migrate accounts

# Verificar estado
python manage.py showmigrations accounts | grep -E "003[5678]"
```

**Resultado esperado:**
```
[X] 0035_homebanner_mobile_image_alter_homebanner_image
[X] 0036_add_slug_to_player
[X] 0037_alter_sitesettings_dashboard_welcome_banner
[X] 0038_merge_slug_and_banner
```

## Paso 7: Verificar y Reiniciar

```bash
# Verificar que el archivo existe y tiene los permisos correctos
ls -lh db.sqlite3

# Reiniciar el servidor
sudo systemctl start gunicorn
# O
sudo supervisorctl start nsc

# Verificar que el servidor está funcionando
sudo systemctl status gunicorn
```

## Paso 8: Verificar la Aplicación

1. Accede a la aplicación en el navegador
2. Verifica que los datos se cargan correctamente
3. Revisa los logs por si hay errores:
   ```bash
   tail -f /var/log/gunicorn/error.log
   ```

## Solución de Problemas

### Error: "database is locked"
- Asegúrate de que el servidor Django está detenido
- Verifica que no hay otros procesos usando la base de datos

### Error: "Permission denied"
- Verifica los permisos: `chown www-data:www-data db.sqlite3`
- Verifica que el usuario `www-data` puede leer/escribir el archivo

### Error: "No such file or directory"
- Verifica que la ruta es correcta: `/var/www/NSC-INTERNATIONAL/`
- Verifica que el archivo se subió correctamente

### Restaurar Backup

Si algo sale mal, puedes restaurar el backup:

```bash
# En el servidor
cd /var/www/NSC-INTERNATIONAL
mv db.sqlite3 db.sqlite3.broken
mv db.sqlite3.backup_YYYYMMDD_HHMMSS db.sqlite3
chown www-data:www-data db.sqlite3
chmod 644 db.sqlite3
sudo systemctl start gunicorn
```

## Notas Importantes

- ⚠️ **Nunca subas la base de datos mientras el servidor está corriendo**
- ⚠️ **Siempre haz backup antes de reemplazar**
- ⚠️ **Verifica los permisos después de subir**
- ✅ El script optimiza la base de datos, reduciendo su tamaño
- ✅ Los backups se guardan en `database_backups/`

## Información de la Base de Datos

- **Tamaño original:** ~4.84 MB
- **Tamaño optimizado:** ~4.69 MB
- **Tablas:** 71-72
- **Migraciones aplicadas:** 118
- **Jugadores:** 24

## Información de las Migraciones

- **Total de migraciones:** 38
- **Migraciones relacionadas con slug:** 3 (0036, 0037, 0038)
- **Tamaño del paquete comprimido:** ~11.52 KB
- **Archivos incluidos:** Todas las migraciones de `apps/accounts/migrations/`

## Orden Recomendado de Actualización

1. ✅ Subir migraciones primero
2. ✅ Aplicar migraciones en el servidor
3. ✅ Subir base de datos
4. ✅ Reemplazar base de datos
5. ✅ Reiniciar servidor
6. ✅ Verificar funcionamiento

