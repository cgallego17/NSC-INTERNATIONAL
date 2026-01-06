#!/bin/bash
# Script para verificar el estado de los staticfiles
# Uso: ./scripts/check_staticfiles.sh

echo "🔍 Verificando estado de staticfiles..."

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Verificar configuración
echo ""
echo "📋 Configuración de staticfiles:"
python manage.py diffsettings | grep -E "STATIC|STATICFILES" || echo "No se encontraron configuraciones de staticfiles"

# Verificar si existe staticfiles.json
echo ""
if [ -f "staticfiles/staticfiles.json" ]; then
    echo "✅ staticfiles.json existe"
    echo "   Archivos mapeados: $(cat staticfiles/staticfiles.json | grep -o '"[^"]*"' | wc -l)"
else
    echo "⚠️  staticfiles.json NO existe - necesitas ejecutar collectstatic"
fi

# Verificar archivos principales
echo ""
echo "📁 Archivos en staticfiles/:"
if [ -d "staticfiles" ]; then
    echo "   JS: $(ls staticfiles/js/*.js 2>/dev/null | wc -l) archivos"
    echo "   CSS: $(ls staticfiles/css/*.css 2>/dev/null | wc -l) archivos"
    echo "   Imágenes: $(find staticfiles/images -type f 2>/dev/null | wc -l) archivos"
else
    echo "   ❌ Directorio staticfiles/ no existe"
fi

# Verificar archivos fuente
echo ""
echo "📁 Archivos fuente en static/:"
if [ -d "static" ]; then
    echo "   JS: $(ls static/js/*.js 2>/dev/null | wc -l) archivos"
    echo "   CSS: $(ls static/css/*.css 2>/dev/null | wc -l) archivos"
    echo "   Imágenes: $(find static/images -type f 2>/dev/null | wc -l) archivos"
else
    echo "   ❌ Directorio static/ no existe"
fi

# Verificar si hay diferencias
echo ""
echo "🔍 Verificando si staticfiles está actualizado..."
python manage.py collectstatic --dry-run --noinput 2>&1 | tail -5

echo ""
echo "✅ Verificación completada"

