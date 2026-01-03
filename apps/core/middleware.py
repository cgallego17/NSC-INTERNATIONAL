"""
Middleware para establecer inglés como idioma predeterminado
y manejar errores de sesión
"""
from django.utils import translation
from django.conf import settings
from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class DefaultLanguageMiddleware:
    """
    Middleware que establece inglés como idioma predeterminado
    si no hay idioma en la sesión.

    Debe ir ANTES de LocaleMiddleware en MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Establecer inglés como predeterminado
        # En Django 4.2.x no existe translation.LANGUAGE_SESSION_KEY.
        # Django usa típicamente '_language' en sesión para LocaleMiddleware/set_language.
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        user_selected_key = 'user_selected_language'  # Flag para saber si el usuario seleccionó explícitamente

        # NO interferir con la vista set_language - dejar que Django la maneje completamente
        # Solo establecer idioma si no hay idioma en la sesión Y no estamos en set_language
        if '/i18n/setlang/' not in request.path:
            # Verificar si el usuario seleccionó explícitamente un idioma
            user_selected = request.session.get(user_selected_key, False)
            session_language = request.session.get(language_key)

            # Si el usuario no ha seleccionado explícitamente un idioma
            if not user_selected:
                # Verificar si el usuario tiene un idioma preferido en su perfil
                preferred_language = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    try:
                        if hasattr(request.user, 'profile') and request.user.profile.preferred_language:
                            preferred_language = request.user.profile.preferred_language
                            # Establecer el idioma en la sesión basado en la preferencia del usuario
                            request.session[language_key] = preferred_language
                            if hasattr(request.session, 'modified'):
                                request.session.modified = True
                    except Exception:
                        pass  # Si hay algún error, usar el predeterminado

                # Si no hay idioma en sesión ni preferencia del usuario, usar inglés
                if not session_language and not preferred_language:
                    request.session[language_key] = settings.LANGUAGE_CODE
                    if hasattr(request.session, 'modified'):
                        request.session.modified = True

                # Activar el idioma (preferencia del usuario, sesión, o inglés por defecto)
                language_to_activate = preferred_language or session_language or settings.LANGUAGE_CODE
                translation.activate(language_to_activate)
            else:
                # El usuario seleccionó un idioma explícitamente, usar ese
                if session_language:
                    translation.activate(session_language)
                else:
                    # Por seguridad, establecer inglés si no hay idioma
                    request.session[language_key] = settings.LANGUAGE_CODE
                    translation.activate(settings.LANGUAGE_CODE)
        # Si estamos en set_language, no hacer nada - dejar que LocaleMiddleware lo maneje

        response = self.get_response(request)

        # Asegurar que el idioma activo se mantenga en la respuesta
        response.setdefault('Content-Language', translation.get_language())

        return response


class SessionInterruptedMiddleware:
    """
    Middleware para manejar errores de SessionInterrupted de manera elegante.

    Este error ocurre cuando la sesión se elimina antes de que la petición se complete,
    típicamente por peticiones concurrentes o problemas de sincronización.

    Debe ir DESPUÉS de SessionMiddleware en MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except SessionInterrupted as e:
            logger.warning(
                f"SessionInterrupted error for user {request.user if request.user.is_authenticated else 'anonymous'}: {e}"
            )

            # Si es una petición AJAX, devolver JSON con error
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "error": "Session expired. Please refresh the page and try again.",
                        "session_expired": True
                    },
                    status=401
                )

            # Si no es AJAX, intentar crear una respuesta básica
            # No podemos usar redirect porque la sesión está interrumpida
            from django.http import HttpResponse
            response = HttpResponse(
                "<html><body><h1>Session Error</h1><p>Your session has expired. "
                "Please <a href='/accounts/login/'>log in again</a>.</p></body></html>",
                status=401
            )
            return response

