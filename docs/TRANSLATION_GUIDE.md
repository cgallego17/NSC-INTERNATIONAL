# Guía de Traducción - NSC International

## Estado Actual

✅ Configuración básica de i18n completada
✅ Archivos de traducción creados (locale/en y locale/es)
✅ Selector de idiomas implementado con banderas
✅ Idioma predeterminado: Inglés

## Estructura de Archivos

```
locale/
├── en/
│   └── LC_MESSAGES/
│       └── django.po (traducciones en inglés)
└── es/
    └── LC_MESSAGES/
        └── django.po (traducciones en español)
```

## Cómo Agregar Traducciones

### 1. En Templates HTML

Usa el tag `{% trans %}` para textos simples:

```django
{% load i18n %}

<!-- Antes -->
<h1>Bienvenido</h1>

<!-- Después -->
<h1>{% trans "Welcome" %}</h1>
```

Para textos con variables, usa `{% blocktrans %}`:

```django
{% blocktrans with name=user.name %}
Hello, {{ name }}!
{% endblocktrans %}
```

### 2. Actualizar Archivos .po

Después de agregar `{% trans %}` en los templates:

1. **Si tienes gettext instalado:**
   ```bash
   python manage.py makemessages -l en -l es
   ```

2. **Si NO tienes gettext:**
   - Edita manualmente los archivos `locale/en/LC_MESSAGES/django.po` y `locale/es/LC_MESSAGES/django.po`
   - Agrega las nuevas entradas siguiendo el formato:
     ```
     msgid "Texto en inglés"
     msgstr "Texto en español"
     ```

### 3. Compilar Mensajes

Después de actualizar los archivos .po:

**Opción A: Usar el script (recomendado)**
```powershell
.\compile_translations.ps1
```

**Opción B: Compilar todos los mensajes (incluyendo Django)**
```powershell
# Asegúrate de que gettext moderno esté en el PATH
$env:Path = "C:\Program Files\gettext-iconv\bin;" + $env:Path
python manage.py compilemessages
```

**Opción C: Compilar solo nuestros archivos manualmente**
```powershell
& "C:\Program Files\gettext-iconv\bin\msgfmt.exe" "locale\en\LC_MESSAGES\django.po" -o "locale\en\LC_MESSAGES\django.mo"
& "C:\Program Files\gettext-iconv\bin\msgfmt.exe" "locale\es\LC_MESSAGES\django.po" -o "locale\es\LC_MESSAGES\django.mo"
```

**Nota:** Se recomienda usar gettext versión 0.26 o superior (instalado con `winget install --id=MicheleLocati.GettextIconv`). La versión antigua (0.14.4) puede tener problemas con algunos archivos de Django.

Esto genera los archivos `.mo` que Django usa para las traducciones.

## Textos que Necesitan Traducción

### Prioridad Alta (Top Bar y Navegación)
- ✅ "My Account" / "Mi Cuenta"
- ✅ "Log In" / "Iniciar Sesión"
- ✅ "Log Out" / "Cerrar Sesión"
- ✅ "Sign Up" / "Registrarse"
- ✅ "Home" / "Inicio"
- ✅ "Events" / "Eventos"
- ✅ "Teams" / "Equipos"
- ✅ "Players" / "Jugadores"
- ✅ "Panel" / "Panel"

### Prioridad Media (Contenido Principal)
- [ ] Títulos de secciones
- [ ] Textos de botones
- [ ] Mensajes de formularios
- [ ] Textos del footer

### Prioridad Baja (Contenido Dinámico)
- [ ] Contenido de banners (desde base de datos)
- [ ] Descripciones de eventos
- [ ] Textos de noticias

## Ejemplos de Uso

### Texto Simple
```django
{% trans "Welcome" %}
```

### Texto con Contexto
```django
{% trans "Events" context "Navigation menu" %}
```

### Texto con Pluralización
```django
{% blocktrans count counter=events.count %}
{{ counter }} event
{% plural %}
{{ counter }} events
{% endblocktrans %}
```

### Texto con Variables
```django
{% blocktrans with name=user.get_full_name %}
Hello, {{ name }}!
{% endblocktrans %}
```

## Comandos Útiles

```bash
# Crear/actualizar archivos de traducción
python manage.py makemessages -l en -l es

# Compilar traducciones
python manage.py compilemessages

# Verificar traducciones faltantes
python manage.py makemessages --dry-run -l es
```

## Notas Importantes

1. **Idioma Predeterminado**: Inglés (configurado en `settings.py`)
2. **Selector de Idioma**: Usa banderas y está en el top-bar
3. **Persistencia**: El idioma se guarda en la sesión del usuario
4. **Formato de Archivos**: Los archivos .po usan UTF-8

## Próximos Pasos

1. Continuar agregando `{% trans %}` a más textos en `public_home.html`
2. Actualizar otros templates importantes (navbar, footer, etc.)
3. Traducir mensajes de formularios y validaciones
4. Agregar traducciones para contenido dinámico desde la base de datos

