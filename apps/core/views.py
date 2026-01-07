"""
Vistas core de la aplicación
"""
from django.http import JsonResponse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.i18n import JavaScriptCatalog
from django.core.cache import cache
from django.contrib.auth import logout
from django.shortcuts import redirect
import json


@require_http_methods(["GET", "POST"])
def set_language(request):
    """
    Vista personalizada para cambiar el idioma
    """
    from django.shortcuts import redirect
    from django.utils import translation
    from django.conf import settings

    # Obtener el idioma del request
    if request.method == "POST":
        language = request.POST.get("language")
        next_url = request.POST.get("next", "/")
    else:
        language = request.GET.get("language")
        next_url = request.GET.get("next", "/")

    # Validar que el idioma esté en los idiomas soportados
    valid_languages = [lang[0] for lang in settings.LANGUAGES]

    if language and language in valid_languages:
        # Activar el idioma
        translation.activate(language)

        # Guardar en sesión (usar la clave correcta para Django 4.2)
        language_session_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        request.session[language_session_key] = language
        request.session["user_selected_language"] = True
        request.session.modified = True

        # Guardar en cookie
        language_cookie_name = getattr(translation, "LANGUAGE_COOKIE_NAME", "django_language")

        # Redirigir a la página anterior o al home
        response = redirect(next_url)
        response.set_cookie(language_cookie_name, language, max_age=365 * 24 * 60 * 60)  # 1 año
        return response
    else:
        # Si el idioma no es válido, redirigir sin cambiar
        return redirect(next_url or "/")


class CachedJavaScriptCatalog(JavaScriptCatalog):
    """
    Versión optimizada de JavaScriptCatalog con caché
    para mejorar el rendimiento del endpoint /jsi18n/
    """

    def get(self, request, *args, **kwargs):
        # Obtener el idioma actual
        language = translation.get_language()

        # Crear clave de caché única por idioma
        cache_key = f'jsi18n_catalog_{language}'

        # Intentar obtener del caché
        cached_catalog = cache.get(cache_key)
        if cached_catalog is not None:
            from django.http import HttpResponse
            response = HttpResponse(
                cached_catalog,
                content_type='application/javascript; charset=utf-8'
            )
            # Agregar headers de caché
            response['Cache-Control'] = 'public, max-age=3600'  # Cache por 1 hora
            return response

        # Si no está en caché, generar el catálogo normalmente
        response = super().get(request, *args, **kwargs)

        # Guardar en caché por 1 hora
        if response.status_code == 200:
            cache.set(cache_key, response.content, 3600)
            # Agregar headers de caché
            response['Cache-Control'] = 'public, max-age=3600'

        return response


def custom_logout_view(request):
    """
    Vista personalizada de logout que acepta GET y POST
    y redirige al home después del logout con parámetro para mostrar alert
    """
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.utils.translation import gettext_lazy as _

    logout(request)
    messages.success(request, _("You have been successfully logged out."))
    # Redirigir con parámetro para que JavaScript muestre el alert
    return redirect("/?logout=success")


def handler404(request, exception):
    """
    Handler personalizado para errores 404 (Página no encontrada)
    """
    from django.shortcuts import render
    from django.template import RequestContext

    return render(request, '404.html', status=404)
