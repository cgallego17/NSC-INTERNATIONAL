#!/bin/bash
# Script de despliegue que regenera staticfiles después de hacer pull
# Uso: ./scripts/deploy.sh

set -e  # Salir si hay errores

echo "🚀 Iniciando despliegue..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Hacer pull de los cambios
echo "📥 Haciendo pull de los cambios..."
git pull origin main || git pull origin master

# Instalar/actualizar dependencias si es necesario
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt --quiet
fi

# Limpiar staticfiles antiguos
echo "🧹 Limpiando staticfiles antiguos..."
rm -rf staticfiles/*

# Recolectar staticfiles
echo "📦 Recolectando staticfiles..."
python manage.py collectstatic --noinput

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Reiniciar servicios si es necesario (ajustar según tu configuración)
# systemctl restart gunicorn  # Descomentar si usas systemd
# docker-compose restart web   # Descomentar si usas Docker

echo "✅ Despliegue completado exitosamente!"

