"""
Vista personalizada para cambiar idioma que marca la selección del usuario
"""

from django.conf import settings
from django.utils import translation  # type: ignore
from django.views.i18n import set_language as django_set_language  # type: ignore


def set_language(request):
    """
    Vista personalizada que envuelve set_language de Django
    y marca que el usuario seleccionó explícitamente un idioma
    """
    # Marcar que el usuario seleccionó explícitamente un idioma ANTES de cambiar
    if request.method == "POST":
        language = request.POST.get("language")
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            # Establecer el idioma en la sesión ANTES de llamar a Django
            language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
            request.session[language_key] = language
            request.session["user_selected_language"] = True
            request.session.modified = True
            # Activar el idioma inmediatamente
            translation.activate(language)
            print(f"✅ Idioma activado: {language}")  # Debug

    # Llamar a la vista original de Django (que también establecerá el idioma)
    response = django_set_language(request)

    # Asegurar que el idioma se mantenga en la respuesta
    if hasattr(request, 'session'):
        language_key = getattr(translation, "LANGUAGE_SESSION_KEY", "_language")
        current_lang = request.session.get(language_key, settings.LANGUAGE_CODE)
        translation.activate(current_lang)
        response.setdefault('Content-Language', current_lang)

    return response
