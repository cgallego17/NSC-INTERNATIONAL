# Pasos para Limpiar Divisiones en el Servidor

## Resumen
Este proceso eliminará todas las divisiones excepto las estándar (05U-18U) y actualizará automáticamente los jugadores y eventos afectados.

---

## Paso 1: Hacer Backup de la Base de Datos (MUY IMPORTANTE)

**En el servidor, antes de hacer cualquier cambio:**

```bash
# Si usas SQLite:
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# O si usas PostgreSQL:
pg_dump -U usuario -d nombre_bd > backup_$(date +%Y%m%d_%H%M%S).sql

# O si usas MySQL:
mysqldump -u usuario -p nombre_bd > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Paso 2: Acceder al Servidor

Conéctate al servidor donde está desplegada la aplicación:

```bash
ssh usuario@servidor.com
# O el método que uses para conectarte
```

Navega al directorio del proyecto:

```bash
cd /ruta/al/proyecto/NSC-INTERNATIONAL
```

---

## Paso 3: Activar el Entorno Virtual (si aplica)

Si usas un entorno virtual:

```bash
# Para venv:
source venv/bin/activate

# Para virtualenv:
source env/bin/activate

# Para conda:
conda activate nombre_entorno
```

---

## Paso 4: Ejecutar el Comando en Modo DRY-RUN (Prueba)

**IMPORTANTE:** Primero ejecuta el comando en modo `--dry-run` para ver qué cambios se harán SIN aplicar nada:

```bash
python manage.py cleanup_divisions --dry-run
```

Esto mostrará:
- Qué divisiones se mantendrán
- Qué divisiones se eliminarán
- Cuántos jugadores y eventos se verán afectados
- Cómo se mapearán las divisiones

**Revisa cuidadosamente la salida** para asegurarte de que todo está correcto.

---

## Paso 5: Verificar el Resumen del Dry-Run

El comando mostrará algo como:

```
=== LIMPIEZA DE DIVISIONES ===

Divisiones estándar a mantener: 05U, 06U, 07U, ..., 18U

Total divisiones en BD: XX

Divisiones a mantener: 14
  - 05U (ID: X): X jugadores, X eventos
  - 06U (ID: X): X jugadores, X eventos
  ...

Divisiones a eliminar: XX
  - [Nombre división]: X jugadores, X eventos
  ...

⚠ ADVERTENCIA: X jugadores tienen divisiones que serán eliminadas
  - [Detalles de mapeo]

⚠ ADVERTENCIA: X eventos tienen divisiones que serán eliminadas
  - [Detalles de eventos]

=== MODO DRY-RUN: No se realizaron cambios ===
```

**Si todo se ve bien**, continúa al siguiente paso.

**Si algo no se ve bien**, detente y revisa la configuración.

---

## Paso 6: Ejecutar el Comando Real (Aplicar Cambios)

Una vez que hayas verificado el dry-run y todo esté correcto, ejecuta el comando **SIN** `--dry-run`:

```bash
python manage.py cleanup_divisions
```

Este comando:
1. ✅ Actualizará automáticamente los jugadores con divisiones a eliminar, mapeándolos a divisiones estándar
2. ✅ Actualizará los eventos, removiendo divisiones no estándar
3. ✅ Eliminará todas las divisiones que no estén en la lista estándar (05U-18U)

---

## Paso 7: Verificar el Resultado

Después de ejecutar el comando, verifica que todo quedó correcto:

```bash
python manage.py cleanup_divisions --dry-run
```

Deberías ver:
- Solo 14 divisiones (05U-18U)
- Todos los jugadores y eventos mapeados correctamente
- No deberían quedar divisiones para eliminar

O verifica manualmente:

```bash
python manage.py shell
```

```python
from apps.events.models import Division
from apps.accounts.models import Player
from apps.events.models import Event

# Ver divisiones restantes
divisions = Division.objects.all().order_by('name')
print(f"Total divisiones: {divisions.count()}")
for div in divisions:
    print(f"  - {div.name}")

# Verificar que todos los jugadores tengan divisiones válidas
players_without_division = Player.objects.filter(division__isnull=True)
print(f"\nJugadores sin división: {players_without_division.count()}")

# Verificar eventos
for event in Event.objects.all():
    print(f"\n{event.title}: {[d.name for d in event.divisions.all()]}")
```

---

## Paso 8: Reiniciar el Servidor (si es necesario)

Si estás usando un servidor de aplicaciones (Gunicorn, uWSGI, etc.), reinícialo:

```bash
# Para systemd:
sudo systemctl restart gunicorn
# O el nombre de tu servicio

# O si usas supervisor:
sudo supervisorctl restart nombre_proceso
```

---

## Paso 9: Verificar en el Navegador

1. Accede a la página de administración de eventos
2. Verifica que las divisiones se muestren correctamente
3. Verifica que los jugadores estén asociados a las divisiones correctas
4. Verifica que los eventos tengan las divisiones correctas

---

## Notas Importantes

⚠️ **IMPORTANTE:**
- ✅ **SIEMPRE** haz backup antes de ejecutar el comando
- ✅ **SIEMPRE** ejecuta primero `--dry-run` para ver qué pasará
- ✅ **SIEMPRE** revisa cuidadosamente la salida del dry-run
- ✅ El comando actualiza automáticamente jugadores y eventos, pero es mejor tener un backup
- ✅ Si algo sale mal, puedes restaurar el backup

---

## Troubleshooting

### Si el comando falla:

1. **Revisa los logs:**
   ```bash
   tail -f logs/django.log
   ```

2. **Verifica que las migraciones estén aplicadas:**
   ```bash
   python manage.py showmigrations
   python manage.py migrate
   ```

3. **Verifica la conexión a la base de datos:**
   ```bash
   python manage.py dbshell
   ```

### Si necesitas revertir:

1. **Restaura el backup:**
   ```bash
   # Para SQLite:
   cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

   # Para PostgreSQL:
   psql -U usuario -d nombre_bd < backup_YYYYMMDD_HHMMSS.sql

   # Para MySQL:
   mysql -u usuario -p nombre_bd < backup_YYYYMMDD_HHMMSS.sql
   ```

---

## Comandos Resumidos (Copy-Paste)

```bash
# 1. Backup
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# 2. Dry-run
python manage.py cleanup_divisions --dry-run

# 3. Ejecutar (después de revisar el dry-run)
python manage.py cleanup_divisions

# 4. Verificar
python manage.py cleanup_divisions --dry-run
```
