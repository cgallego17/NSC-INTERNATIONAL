# Configuración de ClamAV para Escaneo de Virus

## Instalación

### Linux (Ubuntu/Debian)

```bash
# Instalar ClamAV
sudo apt-get update
sudo apt-get install clamav clamav-daemon

# Actualizar base de datos de virus
sudo freshclam

# Iniciar servicio
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon

# Verificar que esté funcionando
sudo systemctl status clamav-daemon
```

### Linux (CentOS/RHEL)

```bash
# Instalar EPEL repository
sudo yum install epel-release

# Instalar ClamAV
sudo yum install clamav clamd

# Actualizar base de datos
sudo freshclam

# Iniciar servicio
sudo systemctl start clamd
sudo systemctl enable clamd
```

### Windows

1. Descargar ClamAV desde: https://www.clamav.net/downloads
2. Instalar ClamAV
3. Configurar el servicio de Windows
4. Actualizar base de datos: `freshclam.exe`

### Docker

```dockerfile
# En tu Dockerfile o docker-compose.yml
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y clamav clamav-daemon
RUN freshclam
```

## Configuración de Python

```bash
# Instalar pyclamd
pip install pyclamd
```

## Configuración en Django

### settings.py

```python
# Habilitar escaneo de virus
ENABLE_VIRUS_SCAN = True

# Opción 1: Socket Unix (Linux - más rápido)
CLAMAV_SOCKET = '/var/run/clamav/clamd.ctl'

# Opción 2: TCP (Windows o alternativa)
CLAMAV_HOST = 'localhost'
CLAMAV_PORT = 3310

# Bloquear subidas si ClamAV no está disponible
REQUIRE_VIRUS_SCAN = False  # True en producción crítica
```

### Variables de Entorno

```bash
# .env o configuración del servidor
ENABLE_VIRUS_SCAN=True
CLAMAV_SOCKET=/var/run/clamav/clamd.ctl
# O
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
REQUIRE_VIRUS_SCAN=False
```

## Verificación

```python
# Probar conexión desde Python
import pyclamd
cd = pyclamd.ClamdUnixSocket('/var/run/clamav/clamd.ctl')
cd.ping()  # Debe retornar 'PONG'
```

## Actualización de Base de Datos

```bash
# Actualizar manualmente
sudo freshclam

# Configurar actualización automática (cron)
# Agregar a crontab:
0 2 * * * /usr/bin/freshclam --quiet
```

## Troubleshooting

### Error: "No se pudo conectar a ClamAV"

1. Verificar que el servicio esté ejecutándose:
   ```bash
   sudo systemctl status clamav-daemon
   ```

2. Verificar permisos del socket:
   ```bash
   ls -l /var/run/clamav/clamd.ctl
   sudo chmod 666 /var/run/clamav/clamd.ctl
   ```

3. Verificar configuración en `/etc/clamav/clamd.conf`:
   ```
   LocalSocket /var/run/clamav/clamd.ctl
   ```

### Error: "pyclamd no está instalado"

```bash
pip install pyclamd
```

### Rendimiento

- El escaneo puede ser lento para archivos grandes
- Considera usar un límite de tamaño antes de escanear
- En producción, considera procesar el escaneo de forma asíncrona



