"""
Vistas para gestión de archivos multimedia
"""

import json
import os
from pathlib import Path

from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.mixins import StaffRequiredMixin

from .forms import MediaFileForm, MediaFileUploadForm
from .models import MediaFile


class MediaFileListView(StaffRequiredMixin, ListView):
    """Lista de archivos multimedia"""

    model = MediaFile
    template_name = "media/media_list.html"
    context_object_name = "media_files"
    paginate_by = 24

    def get_queryset(self):
        queryset = MediaFile.objects.filter(
            status__in=["active", "archived"]
        ).select_related("uploaded_by")

        # Filtros
        file_type = self.request.GET.get("type", "")
        search = self.request.GET.get("search", "")
        status = self.request.GET.get("status", "active")

        if file_type:
            queryset = queryset.filter(file_type=file_type)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_types"] = MediaFile.FILE_TYPE_CHOICES
        context["current_type"] = self.request.GET.get("type", "")
        context["current_search"] = self.request.GET.get("search", "")
        context["current_status"] = self.request.GET.get("status", "active")
        return context


class MediaFileDetailView(StaffRequiredMixin, DetailView):
    """Detalle de archivo multimedia"""

    model = MediaFile
    template_name = "media/media_detail.html"
    context_object_name = "media_file"


class MediaFileCreateView(StaffRequiredMixin, CreateView):
    """Crear nuevo archivo multimedia"""

    model = MediaFile
    form_class = MediaFileForm
    template_name = "media/media_form.html"

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, _("Archivo subido exitosamente."))
        return super().form_valid(form)

    def get_success_url(self):
        from django.urls import reverse

        return reverse("media:list")


class MediaFileUpdateView(StaffRequiredMixin, UpdateView):
    """Editar archivo multimedia"""

    model = MediaFile
    form_class = MediaFileForm
    template_name = "media/media_form.html"

    def form_valid(self, form):
        messages.success(self.request, _("Archivo actualizado exitosamente."))
        return super().form_valid(form)

    def get_success_url(self):
        from django.urls import reverse

        return reverse("media:list")


class MediaFileDeleteView(StaffRequiredMixin, DeleteView):
    """Eliminar archivo multimedia"""

    model = MediaFile
    template_name = "media/media_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Archivo eliminado exitosamente."))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        from django.urls import reverse

        return reverse("media:list")


@require_http_methods(["POST"])
def media_file_upload_ajax(request):
    """Vista AJAX para subir archivos"""
    import logging

    logger = logging.getLogger(__name__)

    if not request.user.is_staff:
        return JsonResponse({"error": "No autorizado"}, status=403)

    # Debug: Ver qué se está recibiendo
    logger.debug(f"POST data: {request.POST}")
    logger.debug(f"FILES data: {list(request.FILES.keys())}")

    # Verificar que se haya enviado un archivo
    if "original_file" not in request.FILES:
        logger.warning("No se encontró 'original_file' en request.FILES")
        return JsonResponse(
            {
                "error": "No se proporcionó ningún archivo",
                "errors": {"original_file": ["Este campo es requerido."]},
                "debug": {
                    "files_keys": list(request.FILES.keys()),
                    "post_keys": list(request.POST.keys()),
                },
            },
            status=400,
        )

    form = MediaFileUploadForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            media_file = form.save(commit=False)
            media_file.uploaded_by = request.user
            media_file.save()

            # Obtener URL del thumbnail
            thumbnail_url = None
            if media_file.file_type == "image":
                thumbnail_url = media_file.get_file_url()
            elif media_file.file_type == "video" and media_file.thumbnail:
                thumbnail_url = media_file.get_thumbnail_url()

            return JsonResponse(
                {
                    "success": True,
                    "id": media_file.id,
                    "title": media_file.title,
                    "url": media_file.get_file_url(),
                    "file_type": media_file.file_type,
                    "file_size": media_file.file_size,
                    "thumbnail": thumbnail_url,
                }
            )
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}", exc_info=True)
            return JsonResponse(
                {"error": "Error al guardar el archivo", "detail": str(e)}, status=500
            )

    # Si el formulario no es válido, retornar errores detallados
    logger.warning(f"Formulario inválido: {form.errors}")
    errors_dict = {}
    for field, error_list in form.errors.items():
        errors_dict[field] = [str(error) for error in error_list]

    return JsonResponse(
        {
            "error": "Error al validar el archivo",
            "errors": errors_dict,
            "debug": {
                "form_errors": dict(form.errors),
                "form_data": dict(request.POST),
                "files_received": list(request.FILES.keys()),
            },
        },
        status=400,
    )


@require_http_methods(["POST"])
def media_file_bulk_delete(request):
    """Eliminar múltiples archivos - Solo admin"""
    if not request.user.is_superuser:
        return JsonResponse({"error": "No autorizado. Solo administradores pueden realizar esta operación."}, status=403)

    try:
        data = json.loads(request.body)
        file_ids = data.get("ids", [])

        if not file_ids:
            return JsonResponse({"error": "No se proporcionaron IDs"}, status=400)

        files = MediaFile.objects.filter(id__in=file_ids)
        count = files.count()

        for file_obj in files:
            file_obj.delete()

        messages.success(
            request, _("{} archivos eliminados exitosamente.").format(count)
        )
        return JsonResponse({"success": True, "count": count})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def media_file_bulk_update(request):
    """Actualizar múltiples archivos (cambiar estado, agregar tags, etc.) - Solo admin"""
    if not request.user.is_superuser:
        return JsonResponse({"error": "No autorizado. Solo administradores pueden realizar esta operación."}, status=403)

    try:
        data = json.loads(request.body)
        file_ids = data.get("ids", [])
        action = data.get("action")

        if not file_ids:
            return JsonResponse({"error": "No se proporcionaron IDs"}, status=400)

        files = MediaFile.objects.filter(id__in=file_ids)
        count = files.count()

        if action == "archive":
            files.update(status="archived")
            message = _("{} archivos archivados exitosamente.").format(count)
        elif action == "activate":
            files.update(status="active")
            message = _("{} archivos activados exitosamente.").format(count)
        elif action == "delete":
            for file_obj in files:
                file_obj.delete()
            message = _("{} archivos eliminados exitosamente.").format(count)
        else:
            return JsonResponse({"error": "Acción no válida"}, status=400)

        messages.success(request, message)
        return JsonResponse({"success": True, "count": count})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def media_file_update_ajax(request, pk):
    """Vista AJAX para actualizar información de un archivo multimedia"""
    if not request.user.is_staff:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        media_file = get_object_or_404(MediaFile, pk=pk)
        data = json.loads(request.body)

        # Actualizar campos permitidos
        if "title" in data:
            media_file.title = data["title"]
        if "description" in data:
            media_file.description = data.get("description", "")
        if "alt_text" in data:
            media_file.alt_text = data.get("alt_text", "")
        if "tags" in data:
            media_file.tags = data.get("tags", "")

        media_file.save()

        return JsonResponse(
            {
                "success": True,
                "id": media_file.id,
                "title": media_file.title,
                "description": media_file.description or "",
                "alt_text": media_file.alt_text or "",
                "tags": media_file.tags or "",
                "url": media_file.get_file_url(),
                "seo_url": media_file.get_seo_url(),
            }
        )

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error al actualizar archivo: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def media_file_list_ajax(request):
    """Vista AJAX para listar archivos multimedia"""
    if not request.user.is_staff:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        file_type = request.GET.get("type", "").strip()
        search = request.GET.get("search", "").strip()
        limit = int(request.GET.get("limit", 50))

        # Construir queryset base
        queryset = MediaFile.objects.filter(status="active").order_by("-created_at")

        # Filtrar por tipo solo si se especifica
        if file_type:
            queryset = queryset.filter(file_type=file_type)

        # Filtrar por búsqueda
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__icontains=search)
            )

        # Limitar resultados
        queryset = queryset[:limit]

        # Serializar resultados
        results = []
        for media in queryset:
            # Obtener URL relativa
            relative_url = media.get_file_url()
            # Construir URL absoluta
            absolute_url = request.build_absolute_uri(relative_url)

            # Obtener thumbnail URL (si existe)
            thumbnail_url = media.get_thumbnail_url()
            if thumbnail_url:
                thumbnail_url = request.build_absolute_uri(thumbnail_url)

            results.append(
                {
                    "id": media.id,
                    "title": media.title,
                    "description": media.description or "",
                    "url": absolute_url,
                    "thumbnail": thumbnail_url or "",
                    "file_type": media.file_type,
                    "file_size": media.file_size,
                    "created_at": media.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse({"success": True, "results": results})

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error al listar archivos: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)
