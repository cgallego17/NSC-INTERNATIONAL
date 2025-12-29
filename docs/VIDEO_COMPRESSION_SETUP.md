# Configuración de Compresión de Video

## Requisitos

### 1. Instalar FFmpeg

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

#### Windows
1. Descargar FFmpeg desde: https://ffmpeg.org/download.html
2. Extraer y agregar al PATH del sistema
3. O usar chocolatey: `choco install ffmpeg`

#### macOS
```bash
brew install ffmpeg
```

### 2. Instalar Python Package
```bash
pip install ffmpeg-python
```

## Configuración

### En settings.py

```python
# Habilitar compresión automática de videos
ENABLE_VIDEO_COMPRESSION = True

# Calidad de compresión (CRF)
# 18 = calidad casi sin pérdida (archivos más grandes)
# 23 = alta calidad con buena compresión (recomendado)
# 28 = calidad media con mejor compresión
VIDEO_COMPRESSION_CRF = 23

# Preset de codificación
# Opciones: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# medium = buen balance entre velocidad y compresión
VIDEO_COMPRESSION_PRESET = 'medium'
```

### Variables de Entorno

```bash
ENABLE_VIDEO_COMPRESSION=True
VIDEO_COMPRESSION_CRF=23
VIDEO_COMPRESSION_PRESET=medium
```

## Cómo Funciona

1. **Al subir un video**: El sistema detecta automáticamente que es un video
2. **Procesamiento**: FFmpeg comprime el video usando H.264 con CRF
3. **Resultado**:
   - Si el video comprimido es más pequeño, se guarda como `processed_file`
   - Si no es más pequeño, se mantiene el original
4. **Uso**: El sistema usa automáticamente el video comprimido si existe

## Calidad CRF

- **CRF 18**: Calidad casi sin pérdida, compresión ~30-40%
- **CRF 23**: Alta calidad (recomendado), compresión ~50-60%
- **CRF 28**: Calidad media, compresión ~70-80%

## Optimización

### Para máxima calidad (archivos más grandes):
```python
VIDEO_COMPRESSION_CRF = 18
VIDEO_COMPRESSION_PRESET = 'slow'  # Más lento pero mejor compresión
```

### Para mejor compresión (archivos más pequeños):
```python
VIDEO_COMPRESSION_CRF = 28
VIDEO_COMPRESSION_PRESET = 'medium'
```

### Para procesamiento rápido:
```python
VIDEO_COMPRESSION_CRF = 23
VIDEO_COMPRESSION_PRESET = 'fast'  # Más rápido pero menos compresión
```

## Verificación

```bash
# Verificar que FFmpeg está instalado
ffmpeg -version

# Probar compresión manual
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4
```

## Notas

- La compresión se hace automáticamente después de subir el video
- Solo se guarda el video comprimido si es más pequeño que el original
- El video original siempre se mantiene
- El procesamiento puede tardar según el tamaño del video







