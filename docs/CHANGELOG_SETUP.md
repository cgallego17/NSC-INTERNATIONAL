# Configuración del Changelog Automático

Este repositorio tiene configurado un sistema automático de changelog que actualiza `CHANGELOG.md` cada vez que se hace un commit.

## ¿Cómo funciona?

El hook `post-commit` se ejecuta automáticamente después de cada commit y:
1. Obtiene la información del último commit (hash, mensaje, autor, fecha, archivos modificados)
2. Formatea una entrada en el changelog con esta información
3. Actualiza el archivo `CHANGELOG.md` con la nueva entrada

## Archivos relacionados

- `.git/hooks/post-commit` - Hook de git que se ejecuta automáticamente
- `CHANGELOG.md` - Archivo que se actualiza automáticamente
- `scripts/test_changelog_hook.py` - Script para probar el hook manualmente

## Requisitos

- Python 3.x instalado y disponible en el PATH
- Git configurado correctamente

## Verificar que funciona

Para verificar que el hook está funcionando correctamente, puedes:

1. **Probar manualmente el hook:**
   ```bash
   python scripts/test_changelog_hook.py
   ```

2. **Hacer un commit de prueba:**
   ```bash
   git add .
   git commit -m "Test: Verificar hook de changelog"
   ```
   Después del commit, deberías ver un mensaje como:
   ```
   ✓ CHANGELOG.md actualizado con el commit abc1234
   ```

3. **Verificar el CHANGELOG.md:**
   ```bash
   cat CHANGELOG.md
   ```

## Formato de las entradas

Cada entrada en el changelog incluye:
- **Hash corto del commit** (como referencia) - ejemplo: `[abc1234]`
- **Mensaje del commit** - primera línea del mensaje
- **Fecha y hora** - fecha y hora del commit
- **Autor** - nombre del autor del commit
- **Archivos modificados** - lista de archivos (máximo 10 mostrados)
- **Detalles** - líneas adicionales del mensaje del commit si existen

### Ejemplo de entrada:

```markdown
- **[abc1234]** Agregar modal de login a teams y players
  - *Fecha:* 2026-01-10 15:30:45
  - *Autor:* Usuario
  - *Archivos modificados:* 2 archivo(s)
    - `templates/accounts/public_team_list.html`
    - `templates/accounts/public_player_list.html`
```

## Desactivar el hook temporalmente

Si necesitas desactivar el hook temporalmente (por ejemplo, para commits masivos):

**En Windows (PowerShell):**
```powershell
Rename-Item .git\hooks\post-commit .git\hooks\post-commit.disabled
```

**En Linux/Mac/Git Bash:**
```bash
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

**Para reactivarlo:**
```bash
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

## Problemas comunes

### El hook no se ejecuta

1. Verifica que Python está instalado:
   ```bash
   python --version
   ```

2. Verifica que el hook existe:
   ```bash
   # Windows
   Test-Path .git\hooks\post-commit

   # Linux/Mac
   ls -la .git/hooks/post-commit
   ```

3. Verifica que Git puede ejecutar scripts:
   ```bash
   git config core.hooksPath
   ```

### El hook falla silenciosamente

El hook `post-commit` no puede impedir que un commit se realice, pero debería mostrar un mensaje si hay un error. Si no ves ningún mensaje:

1. Ejecuta el hook manualmente:
   ```bash
   python .git/hooks/post-commit
   ```

2. O usa el script de prueba:
   ```bash
   python scripts/test_changelog_hook.py
   ```

### Errores de encoding

Si ves errores relacionados con encoding, asegúrate de que tu terminal esté configurada para UTF-8. En Windows, esto generalmente no es un problema, pero si lo es:

```bash
chcp 65001  # Cambiar a UTF-8 en Windows CMD
```

## Notas importantes

- El hook solo se ejecuta en commits locales (no afecta a clones del repositorio)
- Si el hook falla, el commit igual se realiza (los hooks post-commit no pueden impedir commits)
- El changelog se actualiza automáticamente, no necesitas hacer nada manualmente
- El hook funciona mejor con mensajes de commit descriptivos
- Los archivos modificados se limitan a 10 en la entrada para mantener el changelog legible

## Personalización

Si necesitas modificar el formato del changelog, edita el archivo `.git/hooks/post-commit` y modifica la función `format_changelog_entry()`.

## Ejemplo de uso completo

```bash
# 1. Hacer cambios en el código
# ... editar archivos ...

# 2. Agregar cambios al staging
git add .

# 3. Hacer commit con mensaje descriptivo
git commit -m "Agregar paginación al modal de selección de medios

- Agregar paginación al endpoint media_file_list_ajax
- Actualizar función loadMedia para manejar paginación
- Agregar controles de paginación al modal
- Limitar resultados a 24 por página"

# 4. El hook se ejecuta automáticamente y actualiza CHANGELOG.md
# Deberías ver: ✓ CHANGELOG.md actualizado con el commit abc1234

# 5. Verificar el changelog
cat CHANGELOG.md
```

## Mantenimiento

El `CHANGELOG.md` puede crecer mucho con el tiempo. Es recomendable:

1. Periodicamente organizar las entradas por versiones o fechas
2. Limpiar entradas antiguas si es necesario
3. Crear secciones para diferentes tipos de cambios (Features, Fixes, etc.)

Para organizar el changelog manualmente, simplemente edita el archivo `CHANGELOG.md` directamente. El hook seguirá agregando nuevas entradas al principio de la sección `[Sin versión]`.
