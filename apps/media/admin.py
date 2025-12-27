"""
Configuración del admin para Media
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'title', 'file_type', 'file_size_display', 'status', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'status', 'created_at', 'uploaded_by']
    search_fields = ['title', 'description', 'tags', 'original_file']
    readonly_fields = ['file_size', 'processed_file_size', 'width', 'height', 'mime_type', 'compression_ratio', 'thumbnail_preview', 'created_at', 'updated_at']
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('title', 'description', 'alt_text', 'tags')
        }),
        (_('Archivos'), {
            'fields': ('original_file', 'processed_file', 'thumbnail', 'thumbnail_preview', 'file_type', 'mime_type')
        }),
        (_('Metadatos'), {
            'fields': ('file_size', 'processed_file_size', 'compression_ratio', 'width', 'height')
        }),
        (_('Estado'), {
            'fields': ('status', 'uploaded_by', 'created_at', 'updated_at')
        }),
    )

    def thumbnail(self, obj):
        """Muestra miniatura de la imagen o video"""
        thumbnail_url = obj.get_thumbnail_url()
        if thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: cover; border-radius: 4px;" />',
                thumbnail_url
            )
        return '-'
    thumbnail.short_description = _('Vista Previa')

    def thumbnail_preview(self, obj):
        """Vista previa grande del thumbnail en el admin"""
        thumbnail_url = obj.get_thumbnail_url()
        if thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; object-fit: contain; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />',
                thumbnail_url
            )
        return _('No hay miniatura disponible')
    thumbnail_preview.short_description = _('Vista Previa del Thumbnail')

    def file_size_display(self, obj):
        """Muestra el tamaño del archivo de forma legible"""
        size = obj.processed_file_size if obj.processed_file_size else obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    file_size_display.short_description = _('Tamaño')

    def compression_ratio(self, obj):
        """Muestra el ratio de compresión"""
        ratio = obj.get_compression_ratio()
        if ratio > 0:
            return f"{ratio}%"
        return '-'
    compression_ratio.short_description = _('Compresión')

