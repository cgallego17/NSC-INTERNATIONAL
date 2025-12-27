"""
Formularios para gestión de archivos multimedia
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import MediaFile
from .validators import (
    scan_file_for_viruses,
    validate_file_extension,
    validate_file_integrity,
    validate_file_size,
)


class MediaFileForm(forms.ModelForm):
    """Formulario para crear/editar archivo multimedia"""

    class Meta:
        model = MediaFile
        fields = ['title', 'description', 'alt_text', 'tags', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Título del archivo')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Descripción opcional')
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Texto alternativo para accesibilidad')
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Etiquetas separadas por comas')
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class MediaFileUploadForm(forms.ModelForm):
    """Formulario simplificado para subir archivos (AJAX)"""

    class Meta:
        model = MediaFile
        fields = ['original_file', 'title']
        widgets = {
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf,.bmp,.webp,.svg,.tiff,.tif,.flv,.webm,.mkv,.wav,.ogg,.aac,.flac,.m4a'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Título (opcional, se usará el nombre del archivo si está vacío)')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        # No agregar validadores aquí, se validan en clean_original_file
        # Los validadores del modelo se ejecutarán automáticamente

    def clean_original_file(self):
        """Validar el archivo antes de procesarlo"""
        original_file = self.cleaned_data.get('original_file')

        if not original_file:
            return original_file

        # Lista de extensiones permitidas
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
            '.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf',
        ]

        # Validar extensión
        validate_file_extension(original_file, allowed_extensions)

        # Validar integridad del archivo
        try:
            validate_file_integrity(original_file)
        except ValidationError as e:
            raise ValidationError(
                _('Error al validar el archivo: {}').format(str(e))
            )

        # Validar tamaño (None = usar límites automáticos por tipo)
        validate_file_size(original_file, max_size_mb=None)

        # Escanear en busca de virus (si está habilitado)
        scan_file_for_viruses(original_file)

        return original_file

    def clean(self):
        cleaned_data = super().clean()
        original_file = cleaned_data.get('original_file')
        title = cleaned_data.get('title')

        # Si no hay título, usar el nombre del archivo
        if original_file and not title:
            from pathlib import Path
            filename = Path(original_file.name).stem
            cleaned_data['title'] = filename

        return cleaned_data

