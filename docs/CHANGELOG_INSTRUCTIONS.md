# Instrucciones para el Changelog Automático

## ¿Cómo funciona ahora?

El hook `post-commit` actualiza automáticamente `CHANGELOG.md` **SOLO** cuando:

1. ✅ Haces un commit que **NO incluye** `CHANGELOG.md`
2. ✅ El commit incluye otros archivos (código, templates, etc.)

## ¿Qué pasa cuando haces commit?

### Escenario 1: Commit normal (sin CHANGELOG.md)
```bash
git add apps/accounts/views.py templates/events/public_detail.html
git commit -m "Agregar nueva funcionalidad"
```
**Resultado:**
- ✅ El hook actualiza automáticamente `CHANGELOG.md`
- ⚠️ `CHANGELOG.md` queda modificado (no en staging)
- 📝 Puedes incluirlo en el siguiente commit o hacer un commit separado

### Escenario 2: Commit que incluye CHANGELOG.md
```bash
git add CHANGELOG.md apps/accounts/views.py
git commit -m "Actualizar changelog y agregar funcionalidad"
```
**Resultado:**
- ✅ El hook **NO** actualiza `CHANGELOG.md` (evita ciclo infinito)
- ✅ El commit se completa normalmente

### Escenario 3: Commit solo de CHANGELOG.md
```bash
git add CHANGELOG.md
git commit -m "Update CHANGELOG.md"
```
**Resultado:**
- ✅ El hook **NO** actualiza `CHANGELOG.md` (evita ciclo infinito)
- ✅ Útil cuando quieres actualizar el changelog manualmente

## Flujo de trabajo recomendado

### Opción A: Commits separados (Recomendado)
```bash
# 1. Hacer cambios en el código
git add apps/accounts/views.py
git commit -m "Agregar nueva funcionalidad"
# El hook actualiza CHANGELOG.md automáticamente

# 2. (Opcional) Hacer commit del changelog por separado
git add CHANGELOG.md
git commit -m "Update CHANGELOG.md"
```

### Opción B: Incluir CHANGELOG.md manualmente
```bash
# 1. Hacer cambios en el código
git add apps/accounts/views.py
git commit -m "Agregar nueva funcionalidad"
# El hook actualiza CHANGELOG.md automáticamente

# 2. Actualizar CHANGELOG.md manualmente si lo deseas
# ... editar CHANGELOG.md ...

# 3. Incluir CHANGELOG.md en el siguiente commit
git add CHANGELOG.md otros_archivos.py
git commit -m "Agregar más cambios y actualizar changelog"
# El hook NO actualiza porque CHANGELOG.md ya está incluido
```

## ¿Cómo evitar el ciclo infinito?

El hook está diseñado para **evitar el ciclo infinito** de la siguiente manera:

- Si `CHANGELOG.md` está en el commit → **NO actualiza** (evita ciclo)
- Si `CHANGELOG.md` NO está en el commit → **SÍ actualiza** (funcionamiento normal)

## Resolución de problemas

### Problema: CHANGELOG.md queda modificado después de cada commit

**Solución:** Esto es normal. El hook actualiza el changelog pero no lo agrega al staging automáticamente. Puedes:
1. Ignorarlo y seguir trabajando (se incluirá en el siguiente commit si lo agregas)
2. Hacer un commit separado del changelog cuando estés listo
3. Usar `git stash` para guardar temporalmente los cambios

### Problema: El changelog no se actualiza

**Posibles causas:**
1. `CHANGELOG.md` está incluido en el commit → Esto es correcto, evita ciclo
2. El hook tiene un error → Verifica con `python .git/hooks/post-commit`
3. Python no está en el PATH → Verifica con `python --version`

### Problema: Quiero desactivar el hook temporalmente

```bash
# Renombrar el hook
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Para reactivarlo
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

## Ejemplo completo de flujo de trabajo

```bash
# 1. Hacer cambios en varios archivos
vim apps/accounts/views.py
vim templates/accounts/profile.html

# 2. Hacer commit (sin CHANGELOG.md)
git add apps/accounts/views.py templates/accounts/profile.html
git commit -m "Mejorar perfil de usuario

- Agregar validación de email
- Mejorar diseño responsive
- Corregir bug en actualización de perfil"

# 3. El hook se ejecuta automáticamente y actualiza CHANGELOG.md
# Verás: [OK] CHANGELOG.md actualizado con el commit abc1234

# 4. (Opcional) Ver los cambios en el changelog
git diff CHANGELOG.md

# 5. (Opcional) Hacer commit del changelog
git add CHANGELOG.md
git commit -m "Update CHANGELOG.md"

# O simplemente dejarlo para el siguiente commit que incluya otros cambios
```

## Notas importantes

- ⚠️ El hook **NO puede** agregar `CHANGELOG.md` al staging automáticamente porque eso podría interferir con tu flujo de trabajo
- ✅ El hook **NO interrumpe** el commit si hay errores (usa `sys.exit(0)`)
- ✅ El hook **SÍ evita** el ciclo infinito detectando si `CHANGELOG.md` está en el commit
- 📝 Puedes editar manualmente el `CHANGELOG.md` en cualquier momento
- 📝 El formato del changelog sigue el estándar [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
