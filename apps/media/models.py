"""
Modelos para gestión de archivos multimedia
"""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# Configuración de almacenamiento en disco separado
def get_multimedia_storage():
    """Retorna el almacenamiento para archivos multimedia"""
    from django.conf import settings

    multimedia_root = getattr(settings, "MULTIMEDIA_ROOT", None)
    if multimedia_root:
        # IMPORTANT: normalize Path objects to str to avoid per-machine migration churn
        # (Django will serialize the storage.location into migrations)
        multimedia_root = str(multimedia_root)
        return FileSystemStorage(
            location=multimedia_root, base_url=settings.MULTIMEDIA_URL
        )
    return FileSystemStorage()


def multimedia_upload_path(instance, filename):
    """
    Genera la ruta de almacenamiento para archivos multimedia
    Organiza por tipo de archivo y fecha
    """
    from datetime import datetime

    # Obtener tipo de archivo o detectarlo de la extensión
    file_type = getattr(instance, "file_type", "other")
    if file_type == "other" or not file_type:
        # Intentar detectar desde la extensión
        ext = Path(filename).suffix.lower()
        if ext in [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".tiff",
            ".tif",
        ]:
            file_type = "image"
        elif ext in [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"]:
            file_type = "video"
        elif ext in [".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a"]:
            file_type = "audio"
        elif ext in [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".rtf",
        ]:
            file_type = "document"
        else:
            file_type = "other"

    # Obtener fecha (usar fecha actual si no existe created_at)
    if hasattr(instance, "created_at") and instance.created_at:
        year = instance.created_at.year
        month = instance.created_at.month
    else:
        # Si no hay fecha, usar la fecha actual
        now = datetime.now()
        year = now.year
        month = now.month

    # Obtener extensión del archivo
    ext = Path(filename).suffix.lower()

    # Generar nombre único
    base_name = Path(filename).stem
    slug_name = slugify(base_name)

    return f"{file_type}/{year}/{month:02d}/{slug_name}{ext}"


class MediaFile(models.Model):
    """
    Modelo para gestionar archivos multimedia (imágenes, videos, documentos)
    """

    FILE_TYPE_CHOICES = [
        ("image", _("Imagen")),
        ("video", _("Video")),
        ("document", _("Documento")),
        ("audio", _("Audio")),
        ("other", _("Otro")),
    ]

    STATUS_CHOICES = [
        ("active", _("Activo")),
        ("archived", _("Archivado")),
        ("deleted", _("Eliminado")),
    ]

    # Información básica
    title = models.CharField(
        max_length=255,
        verbose_name=_("Título"),
        help_text=_("Título descriptivo del archivo"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción opcional del archivo"),
    )

    # Archivo original
    original_file = models.FileField(
        upload_to=multimedia_upload_path,
        storage=get_multimedia_storage(),
        verbose_name=_("Archivo Original"),
        help_text=_("Archivo original subido"),
    )

    # Archivo procesado (para imágenes comprimidas a WebP)
    processed_file = models.FileField(
        upload_to=multimedia_upload_path,
        storage=get_multimedia_storage(),
        blank=True,
        null=True,
        verbose_name=_("Archivo Procesado"),
        help_text=_("Archivo procesado (ej: imagen WebP comprimida)"),
    )

    # Miniatura (thumbnail) para videos y otros archivos
    thumbnail = models.ImageField(
        upload_to=multimedia_upload_path,
        storage=get_multimedia_storage(),
        blank=True,
        null=True,
        verbose_name=_("Miniatura"),
        help_text=_("Miniatura del archivo (generada automáticamente para videos)"),
    )

    # Metadatos
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default="other",
        verbose_name=_("Tipo de Archivo"),
    )
    mime_type = models.CharField(
        max_length=100, blank=True, verbose_name=_("Tipo MIME")
    )
    file_size = models.PositiveIntegerField(
        default=0, verbose_name=_("Tamaño del Archivo (bytes)")
    )
    processed_file_size = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name=_("Tamaño del Archivo Procesado (bytes)"),
    )

    # Dimensiones (para imágenes y videos)
    width = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("Ancho (px)")
    )
    height = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("Alto (px)")
    )

    # Información adicional para imágenes
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Texto Alternativo"),
        help_text=_("Texto alternativo para accesibilidad (alt text)"),
    )

    # Estado y organización
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name=_("Estado"),
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Etiquetas"),
        help_text=_("Etiquetas separadas por comas para organización"),
    )

    # Usuario y fechas
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_media",
        verbose_name=_("Subido por"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Fecha de Creación")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Fecha de Actualización")
    )

    class Meta:
        verbose_name = _("Archivo Multimedia")
        verbose_name_plural = _("Archivos Multimedia")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["file_type", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["uploaded_by"]),
        ]

    def __str__(self):
        return self.title or self.original_file.name

    def save(self, *args, **kwargs):
        """Procesar archivo al guardar"""
        is_new = not self.pk
        if self.original_file and is_new:
            # Detectar tipo de archivo
            self._detect_file_type()
            # Calcular tamaño
            self.file_size = self.original_file.size
            # Procesar según el tipo
            if self.file_type == "image":
                self._process_image()
            elif self.file_type == "video":
                # Guardar primero para tener el path del archivo
                super().save(*args, **kwargs)
                # Generar thumbnail de forma asíncrona para no bloquear la respuesta
                # Usar threading para generar el thumbnail en segundo plano
                import threading

                video_pk = self.pk
                video_path = self.original_file.path if self.original_file else None

                def generate_thumbnail_async():
                    try:
                        if video_path:
                            # Recargar el objeto desde la BD
                            video_obj = self.__class__.objects.get(pk=video_pk)
                            video_obj._generate_video_thumbnail(video_path)
                            if video_obj.thumbnail:
                                video_obj.save(update_fields=["thumbnail"])
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"Error generando thumbnail asíncrono: {e}", exc_info=True
                        )

                # Iniciar generación de thumbnail en segundo plano
                thread = threading.Thread(target=generate_thumbnail_async)
                thread.daemon = True
                thread.start()

                # Procesar video de forma asíncrona también (comprimir)
                def process_video_async():
                    try:
                        # Recargar el objeto desde la BD
                        video_obj = self.__class__.objects.get(pk=video_pk)
                        video_obj._process_video()
                        # Guardar cambios si hay
                        update_fields = []
                        if video_obj.width:
                            update_fields.append("width")
                        if video_obj.height:
                            update_fields.append("height")
                        if video_obj.processed_file:
                            update_fields.extend(
                                ["processed_file", "processed_file_size"]
                            )
                        if update_fields:
                            video_obj.save(update_fields=update_fields)
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"Error procesando video asíncrono: {e}", exc_info=True
                        )

                # Iniciar procesamiento de video en segundo plano
                thread2 = threading.Thread(target=process_video_async)
                thread2.daemon = True
                thread2.start()

                return

        super().save(*args, **kwargs)

    def _detect_file_type(self):
        """Detecta el tipo de archivo basado en la extensión y MIME type"""
        if not self.original_file:
            return

        filename = self.original_file.name.lower()
        ext = Path(filename).suffix.lower()

        # Detectar MIME type
        import mimetypes

        mime_type, _ = mimetypes.guess_type(filename)
        self.mime_type = mime_type or ""

        # Detectar tipo de archivo
        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".tiff",
            ".tif",
        ]
        video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"]
        audio_extensions = [".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a"]
        document_extensions = [
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".rtf",
        ]

        if ext in image_extensions:
            self.file_type = "image"
        elif ext in video_extensions:
            self.file_type = "video"
        elif ext in audio_extensions:
            self.file_type = "audio"
        elif ext in document_extensions:
            self.file_type = "document"
        else:
            self.file_type = "other"

    def _process_image(self):
        """Procesa la imagen: comprime y convierte a WebP (excepto PNG que mantiene su formato)"""
        try:
            import io

            from PIL import Image

            # Leer la imagen original y validar que no esté corrupta
            self.original_file.seek(0)

            # Verificar que la imagen sea válida antes de procesar
            try:
                img = Image.open(self.original_file)
                img.verify()  # Verificar integridad
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Imagen corrupta detectada: {e}")
                raise ValueError(f"La imagen está corrupta: {e}")

            # Reabrir después de verify (verify cierra el archivo)
            self.original_file.seek(0)
            img = Image.open(self.original_file)

            # Guardar dimensiones
            self.width = img.width
            self.height = img.height

            # Detectar si es PNG
            original_ext = Path(self.original_file.name).suffix.lower()
            is_png = original_ext == ".png"

            # Si es PNG, mantener el formato original sin conversión
            if is_png:
                # Para PNG, solo optimizar sin cambiar el formato
                # Mantener el modo original (RGBA, RGB, P, etc.) para preservar transparencia
                output = io.BytesIO()

                # Guardar como PNG optimizado, manteniendo todas las propiedades
                img.save(
                    output,
                    format="PNG",
                    optimize=True,  # Optimizar sin perder calidad
                )

                output.seek(0)

                # Generar nombre del archivo procesado (mantener extensión PNG)
                original_name = Path(self.original_file.name).stem
                processed_filename = f"{original_name}.png"
            else:
                # Para otras imágenes (JPG, etc.), convertir a WebP
                # Convertir a RGB si es necesario (para PNG con transparencia que no sean PNG)
                if img.mode in ("RGBA", "LA", "P"):
                    # Crear fondo blanco para imágenes con transparencia
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    rgb_img.paste(
                        img,
                        mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None,
                    )
                    img = rgb_img
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Comprimir y convertir a WebP
                output = io.BytesIO()

                # Guardar como WebP con calidad alta (90) para mantener calidad
                img.save(
                    output,
                    format="WEBP",
                    quality=90,
                    method=6,  # Método de compresión más lento pero mejor calidad
                )

                output.seek(0)

                # Generar nombre del archivo procesado
                original_name = Path(self.original_file.name).stem
                processed_filename = f"{original_name}.webp"

            # Guardar el archivo procesado
            from django.core.files.base import ContentFile

            self.processed_file.save(
                processed_filename, ContentFile(output.read()), save=False
            )

            # Calcular tamaño del archivo procesado
            self.processed_file_size = self.processed_file.size

        except Exception as e:
            # Si hay error en el procesamiento, continuar sin archivo procesado
            print(f"Error procesando imagen: {e}")
            self.processed_file = None

    def get_file_url(self):
        """Retorna la URL del archivo a usar (procesado si existe, sino original)"""
        if self.processed_file and self.file_type == "image":
            return self.processed_file.url
        return self.original_file.url

    def get_file_path(self):
        """Retorna la ruta del archivo a usar"""
        if self.processed_file and self.file_type == "image":
            return self.processed_file.path
        return self.original_file.path

    def get_compression_ratio(self):
        """Calcula el ratio de compresión si hay archivo procesado"""
        if self.processed_file_size and self.file_size:
            return round((1 - self.processed_file_size / self.file_size) * 100, 2)
        return 0

    def _process_video(self):
        """Procesa el video: comprime manteniendo calidad"""
        try:
            import os
            import tempfile

            import ffmpeg

            from django.conf import settings
            from django.core.files.base import ContentFile

            # Configurar ruta de FFmpeg si está especificada en settings
            ffmpeg_path = getattr(settings, "FFMPEG_PATH", None)
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                # Agregar al PATH temporalmente
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                original_path_env = os.environ.get("PATH", "")
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + original_path_env

            # Obtener path del archivo original
            original_path = self.original_file.path

            # Crear archivo temporal para el video comprimido
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_output_path = temp_output.name
            temp_output.close()

            try:
                # Obtener información del video original
                # Si falla, continuar sin dimensiones
                try:
                    probe = ffmpeg.probe(original_path)
                    video_stream = next(
                        (
                            stream
                            for stream in probe["streams"]
                            if stream["codec_type"] == "video"
                        ),
                        None,
                    )

                    if video_stream:
                        # Guardar dimensiones
                        self.width = int(video_stream.get("width", 0))
                        self.height = int(video_stream.get("height", 0))
                except Exception as probe_error:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"No se pudo obtener información del video: {probe_error}"
                    )
                    # Continuar sin dimensiones

                # Generar thumbnail del video (siempre intentar, incluso si no hay video_stream)
                try:
                    self._generate_video_thumbnail(original_path)
                except Exception as thumb_error:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"No se pudo generar thumbnail en _process_video: {thumb_error}"
                    )
                    self.thumbnail = None

                # Verificar si la compresión está habilitada
                from django.conf import settings

                enable_compression = getattr(settings, "ENABLE_VIDEO_COMPRESSION", True)

                if not enable_compression:
                    self.processed_file = None
                    return

                # Configuración de compresión con CRF (Constant Rate Factor)
                # CRF 23 es un buen balance entre calidad y tamaño
                # Rango: 0 (sin pérdida, archivo grande) a 51 (muy comprimido, baja calidad)
                # 18-23 es considerado "transparente" (calidad visualmente idéntica)
                crf = getattr(settings, "VIDEO_COMPRESSION_CRF", 23)
                preset = getattr(settings, "VIDEO_COMPRESSION_PRESET", "medium")

                # Procesar video con FFmpeg
                stream = ffmpeg.input(original_path)

                # Aplicar compresión H.264 con CRF
                stream = ffmpeg.output(
                    stream,
                    temp_output_path,
                    vcodec="libx264",  # Codec H.264
                    crf=crf,  # Calidad constante (23 = alta calidad)
                    preset=preset,  # Velocidad de codificación
                    movflags="faststart",  # Optimizar para streaming web
                    pix_fmt="yuv420p",  # Formato de píxel compatible
                    acodec="aac",  # Codec de audio
                    audio_bitrate="128k",  # Bitrate de audio
                )

                # Ejecutar compresión
                ffmpeg.run(stream, overwrite_output=True, quiet=True)

                # Verificar que el archivo comprimido existe y es más pequeño
                if os.path.exists(temp_output_path):
                    compressed_size = os.path.getsize(temp_output_path)
                    original_size = os.path.getsize(original_path)

                    # Solo usar el archivo comprimido si es más pequeño
                    if compressed_size < original_size:
                        # Leer el archivo comprimido
                        with open(temp_output_path, "rb") as f:
                            compressed_content = f.read()

                        # Generar nombre del archivo procesado
                        original_name = Path(self.original_file.name).stem
                        processed_filename = f"{original_name}_compressed.mp4"

                        # Guardar el archivo procesado
                        self.processed_file.save(
                            processed_filename,
                            ContentFile(compressed_content),
                            save=False,
                        )

                        # Calcular tamaño del archivo procesado
                        self.processed_file_size = self.processed_file.size
                    else:
                        # Si el comprimido es más grande, no guardarlo
                        self.processed_file = None
                        self.processed_file_size = None

            finally:
                # Eliminar archivo temporal
                try:
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                except Exception:
                    pass

        except ImportError:
            # FFmpeg no está disponible
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "ffmpeg-python no está instalado. Instala con: pip install ffmpeg-python"
            )
            self.processed_file = None
            # No generar thumbnail si FFmpeg no está disponible
            self.thumbnail = None
        except Exception as e:
            # Si hay error en el procesamiento, continuar sin archivo procesado
            # NO bloquear la subida del video si hay error en el procesamiento
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error procesando video: {e}", exc_info=True)
            logger.warning("Continuando con la subida del video sin procesamiento")
            self.processed_file = None
            # Intentar generar thumbnail de todas formas (puede funcionar aunque el procesamiento falle)
            try:
                if hasattr(self, "original_file") and self.original_file:
                    original_path = self.original_file.path
                    self._generate_video_thumbnail(original_path)
            except Exception as thumb_error:
                logger.warning(f"No se pudo generar thumbnail: {thumb_error}")
                self.thumbnail = None

    def _generate_video_thumbnail(self, video_path):
        """Genera una miniatura (thumbnail) del video"""
        try:
            import os
            import subprocess
            import tempfile

            import ffmpeg
            from PIL import Image

            from django.conf import settings
            from django.core.files.base import ContentFile

            # Configurar ruta de FFmpeg si está especificada en settings
            ffmpeg_path = getattr(settings, "FFMPEG_PATH", None)
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                # Agregar al PATH temporalmente
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                original_path = os.environ.get("PATH", "")
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + original_path

            # Crear archivo temporal para el thumbnail
            temp_thumbnail = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_thumbnail_path = temp_thumbnail.name
            temp_thumbnail.close()

            try:
                # Extraer un frame del video (al segundo 1 o al inicio si falla)
                # Si hay una ruta específica de FFmpeg, usarla
                if ffmpeg_path and os.path.exists(ffmpeg_path):
                    # Intentar extraer frame al segundo 1 directamente
                    # Si falla, intentar al inicio del video
                    result = subprocess.run(
                        [
                            ffmpeg_path,
                            "-ss",
                            "1",
                            "-i",
                            video_path,
                            "-vframes",
                            "1",
                            "-q:v",
                            "2",
                            "-y",
                            temp_thumbnail_path,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    # Si falla, intentar sin especificar tiempo (frame 0)
                    if (
                        result.returncode != 0
                        or not os.path.exists(temp_thumbnail_path)
                        or os.path.getsize(temp_thumbnail_path) == 0
                    ):
                        result = subprocess.run(
                            [
                                ffmpeg_path,
                                "-i",
                                video_path,
                                "-vframes",
                                "1",
                                "-q:v",
                                "2",
                                "-y",
                                temp_thumbnail_path,
                            ],
                            capture_output=True,
                            text=True,
                            timeout=60,
                        )
                else:
                    # Usar ffmpeg-python (requiere que ffmpeg esté en PATH)
                    try:
                        probe = ffmpeg.probe(video_path)
                        duration = float(probe["format"].get("duration", 1))
                        seek_time = min(
                            1.0, duration * 0.1
                        )  # Al segundo 1 o 10% del video
                    except Exception:
                        seek_time = 1.0

                    # Extraer frame usando FFmpeg
                    (
                        ffmpeg.input(video_path, ss=seek_time)  # ss = seek time
                        .output(
                            temp_thumbnail_path,
                            vframes=1,
                            format="image2",
                            vcodec="mjpeg",
                        )
                        .overwrite_output()
                        .run(quiet=True)
                    )

                # Verificar que el thumbnail se generó
                if (
                    os.path.exists(temp_thumbnail_path)
                    and os.path.getsize(temp_thumbnail_path) > 0
                ):
                    # Optimizar thumbnail con PIL
                    img = Image.open(temp_thumbnail_path)

                    # Redimensionar si es muy grande (máximo 400x400)
                    max_size = 400
                    if img.width > max_size or img.height > max_size:
                        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                    # Convertir a RGB si es necesario
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    # Guardar optimizado
                    img.save(temp_thumbnail_path, "JPEG", quality=85, optimize=True)

                    # Leer el thumbnail
                    with open(temp_thumbnail_path, "rb") as f:
                        thumbnail_content = f.read()

                    # Generar nombre del thumbnail
                    original_name = Path(self.original_file.name).stem
                    thumbnail_filename = f"{original_name}_thumb.jpg"

                    # Guardar el thumbnail
                    self.thumbnail.save(
                        thumbnail_filename, ContentFile(thumbnail_content), save=False
                    )

            finally:
                # Eliminar archivo temporal
                try:
                    if os.path.exists(temp_thumbnail_path):
                        os.unlink(temp_thumbnail_path)
                except Exception:
                    pass

        except Exception as e:
            import logging
            import traceback

            logger = logging.getLogger(__name__)
            logger.error(f"No se pudo generar thumbnail del video: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.thumbnail = None

    def get_thumbnail_url(self):
        """Retorna la URL de la miniatura o del archivo si no hay thumbnail"""
        if self.thumbnail and hasattr(self.thumbnail, "url"):
            return self.thumbnail.url
        elif self.file_type == "image":
            return self.get_file_url()
        return None

    def get_seo_url(self):
        """Retorna una URL SEO-friendly basada en el título"""
        from django.conf import settings
        from django.utils.text import slugify

        # Generar slug del título
        title_slug = slugify(self.title)
        if not title_slug:
            title_slug = f"media-{self.id}"

        # Obtener la extensión del archivo original
        original_name = Path(self.original_file.name)
        ext = original_name.suffix.lower()

        # Construir URL SEO-friendly
        # Formato: /media/{tipo}/{año}/{mes}/{slug-titulo}{ext}
        if hasattr(self, "created_at") and self.created_at:
            year = self.created_at.year
            month = self.created_at.month
        else:
            from datetime import datetime

            now = datetime.now()
            year = now.year
            month = now.month

        # Usar el mismo almacenamiento que el archivo
        base_url = getattr(settings, "MULTIMEDIA_URL", "/media/")
        if not base_url.endswith("/"):
            base_url += "/"

        # Construir ruta SEO-friendly
        seo_path = f"{self.file_type}/{year}/{month:02d}/{title_slug}{ext}"

        return f"{base_url}{seo_path}"

    def delete(self, *args, **kwargs):
        """Elimina los archivos físicos al eliminar el registro"""
        if self.original_file:
            self.original_file.delete(save=False)
        if self.processed_file:
            self.processed_file.delete(save=False)
        if self.thumbnail:
            self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)
