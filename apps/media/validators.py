"""
Validadores para verificar integridad de archivos multimedia
"""
import io
import logging
import os
import struct
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def validate_file_integrity(file):
    """
    Valida que el archivo no esté corrupto verificando:
    1. Magic bytes (firma del archivo)
    2. Integridad del contenido según el tipo
    """
    if not file:
        return

    # Guardar posición actual
    current_pos = file.tell() if hasattr(file, 'tell') else 0

    # Leer los primeros bytes para verificar magic bytes
    try:
        file.seek(0)
        header = file.read(16)
        file.seek(current_pos)  # Restaurar posición original
    except (AttributeError, IOError):
        # Si no se puede leer, puede ser un archivo en memoria
        # Intentar leer de otra forma
        try:
            if hasattr(file, 'read'):
                file.seek(0)
                header = file.read(16)
                file.seek(0)
            else:
                return  # No se puede validar
        except Exception:
            return  # Si falla, continuar sin validar magic bytes

    filename = file.name.lower() if hasattr(file, 'name') else ''
    ext = Path(filename).suffix.lower() if filename else ''

    # Verificar magic bytes según extensión
    if ext in ['.jpg', '.jpeg']:
        if not header.startswith(b'\xff\xd8\xff'):
            raise ValidationError(
                _('El archivo no es una imagen JPEG válida o está corrupto.')
            )
        # Validar con PIL
        _validate_image(file, ext)

    elif ext == '.png':
        if not header.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValidationError(
                _('El archivo no es una imagen PNG válida o está corrupto.')
            )
        _validate_image(file, ext)

    elif ext == '.gif':
        if not (header.startswith(b'GIF87a') or header.startswith(b'GIF89a')):
            raise ValidationError(
                _('El archivo no es una imagen GIF válida o está corrupto.')
            )
        _validate_image(file, ext)

    elif ext == '.bmp':
        if not header.startswith(b'BM'):
            raise ValidationError(
                _('El archivo no es una imagen BMP válida o está corrupto.')
            )
        _validate_image(file, ext)

    elif ext == '.webp':
        if not header.startswith(b'RIFF') or b'WEBP' not in header[:12]:
            raise ValidationError(
                _('El archivo no es una imagen WebP válida o está corrupto.')
            )
        _validate_image(file, ext)

    elif ext == '.pdf':
        if not header.startswith(b'%PDF'):
            raise ValidationError(
                _('El archivo no es un PDF válido o está corrupto.')
            )
        _validate_pdf(file)

    elif ext in ['.mp4', '.m4a']:
        # MP4/M4A tienen estructura más compleja, verificar cajas básicas
        if not (header.startswith(b'\x00\x00\x00') or b'ftyp' in header[:12]):
            # Algunos MP4 pueden empezar con diferentes estructuras
            # Verificar que al menos tenga estructura válida
            file.seek(0)
            try:
                # Leer más bytes para verificar estructura MP4
                larger_header = file.read(32)
                if b'ftyp' not in larger_header and b'moov' not in larger_header:
                    raise ValidationError(
                        _('El archivo no es un MP4/M4A válido o está corrupto.')
                    )
            except Exception:
                raise ValidationError(
                    _('El archivo no es un MP4/M4A válido o está corrupto.')
                )
            finally:
                file.seek(0)

    elif ext == '.zip':
        # Office files (docx, xlsx, pptx) son ZIP
        if not header.startswith(b'PK\x03\x04'):
            raise ValidationError(
                _('El archivo Office no es válido o está corrupto.')
            )

    elif ext in ['.mp3']:
        # MP3 puede empezar con ID3 tag o directamente con frame sync
        if not (header.startswith(b'ID3') or
                (len(header) >= 3 and (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0))):
            raise ValidationError(
                _('El archivo no es un MP3 válido o está corrupto.')
            )

    elif ext in ['.wav']:
        if not header.startswith(b'RIFF') or b'WAVE' not in header[:12]:
            raise ValidationError(
                _('El archivo no es un WAV válido o está corrupto.')
            )

    elif ext in ['.avi']:
        if not (header.startswith(b'RIFF') and b'AVI ' in header[:12]):
            raise ValidationError(
                _('El archivo no es un AVI válido o está corrupto.')
            )

    elif ext in ['.mov', '.qt']:
        # QuickTime/MOV puede tener diferentes estructuras
        if not (b'ftyp' in header[:12] or b'moov' in header[:12] or b'mdat' in header[:12]):
            raise ValidationError(
                _('El archivo no es un MOV válido o está corrupto.')
            )


def _validate_image(file, ext):
    """Valida que una imagen sea válida usando PIL"""
    try:
        from PIL import Image

        file.seek(0)
        img = Image.open(file)

        # Verificar que la imagen se pueda leer completamente
        img.verify()

        # Para algunos formatos, necesitamos reabrir después de verify
        file.seek(0)
        img = Image.open(file)

        # Intentar cargar la imagen completamente
        img.load()

        # Verificar dimensiones razonables
        if img.width <= 0 or img.height <= 0:
            raise ValidationError(
                _('La imagen tiene dimensiones inválidas.')
            )

        # Verificar que no sea demasiado grande (prevención de bombas ZIP)
        if img.width > 50000 or img.height > 50000:
            raise ValidationError(
                _('La imagen es demasiado grande. Dimensiones máximas: 50000x50000px.')
            )

        file.seek(0)

    except Image.UnidentifiedImageError:
        raise ValidationError(
            _('No se pudo identificar el formato de la imagen o está corrupta.')
        )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            _('Error al validar la imagen: El archivo puede estar corrupto.')
        )


def _validate_pdf(file):
    """Valida que un PDF sea válido"""
    try:
        file.seek(0)
        content = file.read(1024)
        file.seek(0)

        # Verificar que tenga la estructura básica de PDF
        if b'%PDF' not in content:
            raise ValidationError(
                _('El archivo no es un PDF válido.')
            )

        # Verificar que tenga al menos un objeto PDF (%%EOF o similar)
        # Leer más del archivo si es necesario
        file.seek(0, 2)  # Ir al final
        file_size = file.tell()
        file.seek(0)

        if file_size < 100:  # PDFs muy pequeños probablemente están corruptos
            raise ValidationError(
                _('El archivo PDF parece estar corrupto o incompleto.')
            )

        # Leer los últimos bytes para verificar %%EOF
        if file_size > 1024:
            file.seek(max(0, file_size - 1024))
            end_content = file.read()
            if b'%%EOF' not in end_content and b'endobj' not in end_content:
                # Algunos PDFs pueden no tener %%EOF, pero deberían tener endobj
                pass  # No es crítico, algunos PDFs válidos no lo tienen

        file.seek(0)

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            _('Error al validar el PDF: El archivo puede estar corrupto.')
        )


def validate_file_size(file, max_size_mb=None):
    """
    Valida que el archivo no exceda el tamaño máximo
    max_size_mb: Tamaño máximo en MB. Si es None, usa límites por tipo de archivo
    """
    if not file:
        return

    if hasattr(file, 'size'):
        file_size = file.size
    else:
        # Si no tiene atributo size, calcularlo
        try:
            file.seek(0, 2)  # Ir al final
            file_size = file.tell()
            file.seek(0)  # Resetear
        except (AttributeError, IOError):
            return  # No se puede determinar el tamaño

    # Si no se especifica límite, usar límites por tipo de archivo desde settings
    if max_size_mb is None:
        from django.conf import settings
        filename = file.name.lower() if hasattr(file, 'name') else ''
        ext = Path(filename).suffix.lower() if filename else ''

        # Límites por tipo de archivo desde settings
        if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']:
            max_size_mb = getattr(settings, 'MEDIA_MAX_FILE_SIZE_VIDEO', 500)
        elif ext in ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a']:
            max_size_mb = getattr(settings, 'MEDIA_MAX_FILE_SIZE_AUDIO', 200)
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']:
            max_size_mb = getattr(settings, 'MEDIA_MAX_FILE_SIZE_DOCUMENT', 100)
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif']:
            max_size_mb = getattr(settings, 'MEDIA_MAX_FILE_SIZE_IMAGE', 50)
        else:
            max_size_mb = getattr(settings, 'MEDIA_MAX_FILE_SIZE_DEFAULT', 100)

    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        # Mostrar tamaño del archivo en el mensaje
        file_size_mb = round(file_size / (1024 * 1024), 2)
        raise ValidationError(
            _('El archivo es demasiado grande. Tamaño del archivo: {} MB. Tamaño máximo permitido: {} MB').format(
                file_size_mb, max_size_mb
            )
        )

    if file_size == 0:
        raise ValidationError(
            _('El archivo está vacío.')
        )


def validate_file_extension(file, allowed_extensions):
    """
    Valida que la extensión del archivo esté en la lista permitida
    """
    if not file:
        return

    filename = file.name if hasattr(file, 'name') else ''
    if not filename:
        raise ValidationError(_('El archivo no tiene nombre.'))

    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _('Tipo de archivo no permitido: {}. Extensiones permitidas: {}').format(
                ext, ', '.join(allowed_extensions)
            )
        )


def scan_file_for_viruses(file):
    """
    Escanea un archivo en busca de virus usando ClamAV

    Requiere:
    - ClamAV instalado en el servidor
    - pyclamd instalado: pip install pyclamd

    Configuración en settings.py:
    ENABLE_VIRUS_SCAN = True  # Habilitar escaneo
    CLAMAV_SOCKET = '/var/run/clamav/clamd.ctl'  # Socket de ClamAV (Linux)
    # O
    CLAMAV_HOST = 'localhost'  # Host de ClamAV
    CLAMAV_PORT = 3310  # Puerto de ClamAV
    """
    # Verificar si el escaneo está habilitado
    enable_scan = getattr(settings, 'ENABLE_VIRUS_SCAN', False)
    if not enable_scan:
        return  # Escaneo deshabilitado, continuar sin validar

    if not file:
        return

    try:
        import pyclamd
    except ImportError:
        logger.warning(
            'pyclamd no está instalado. Instala con: pip install pyclamd'
        )
        # Si no está instalado, no bloquear la subida pero registrar advertencia
        return

    try:
        # Intentar conectar a ClamAV
        clamav_socket = getattr(settings, 'CLAMAV_SOCKET', None)
        clamav_host = getattr(settings, 'CLAMAV_HOST', 'localhost')
        clamav_port = getattr(settings, 'CLAMAV_PORT', 3310)

        if clamav_socket:
            # Conectar vía socket Unix (Linux)
            try:
                cd = pyclamd.ClamdUnixSocket(clamav_socket)
            except Exception:
                # Fallback a TCP
                cd = pyclamd.ClamdNetworkSocket(clamav_host, clamav_port)
        else:
            # Conectar vía TCP
            cd = pyclamd.ClamdNetworkSocket(clamav_host, clamav_port)

        # Verificar que ClamAV esté funcionando
        cd.ping()

        # Guardar el archivo temporalmente para escanearlo
        file.seek(0)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Escribir el contenido del archivo
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Escanear el archivo
            scan_result = cd.scan_file(temp_file_path)

            if scan_result:
                # Virus detectado
                virus_name = list(scan_result.values())[0][1] if scan_result else 'Unknown'
                raise ValidationError(
                    _('Virus detectado en el archivo: {}. El archivo ha sido rechazado por seguridad.').format(
                        virus_name
                    )
                )
        finally:
            # Eliminar archivo temporal
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

        # Resetear posición del archivo
        file.seek(0)

    except pyclamd.ConnectionError:
        logger.error('No se pudo conectar a ClamAV. Verifica que el servicio esté ejecutándose.')
        # Si ClamAV no está disponible, registrar error pero no bloquear
        # En producción, podrías querer bloquear la subida si ClamAV es crítico
        if getattr(settings, 'REQUIRE_VIRUS_SCAN', False):
            raise ValidationError(
                _('El servicio de escaneo antivirus no está disponible. Por favor, contacta al administrador.')
            )
    except Exception as e:
        logger.error(f'Error al escanear archivo con ClamAV: {e}')
        # Si hay error, decidir si bloquear o permitir
        if getattr(settings, 'REQUIRE_VIRUS_SCAN', False):
            raise ValidationError(
                _('Error al escanear el archivo. Por favor, intenta nuevamente o contacta al administrador.')
            )

