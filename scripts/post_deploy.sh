#!/bin/bash
# Script post-deploy para regenerar staticfiles
# Este script se puede ejecutar automáticamente después de hacer git pull
# Uso: ./scripts/post_deploy.sh

set -e

echo "🔄 Regenerando staticfiles después del pull..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Limpiar staticfiles antiguos
echo "🧹 Limpiando staticfiles antiguos..."
rm -rf staticfiles/*

# Recolectar staticfiles
echo "📦 Recolectando staticfiles..."
python manage.py collectstatic --noinput

echo "✅ Staticfiles regenerados exitosamente!"

