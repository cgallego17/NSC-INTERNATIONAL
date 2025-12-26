"""
Middleware para establecer inglés como idioma predeterminado
"""
from django.utils import translation
from django.conf import settings


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
        # Solo establecer inglés si no hay idioma en la sesión Y no estamos en set_language
        if '/i18n/setlang/' not in request.path:
            # Verificar si el usuario seleccionó explícitamente un idioma
            user_selected = request.session.get(user_selected_key, False)
            session_language = request.session.get(language_key)
            
            # Si el usuario no ha seleccionado explícitamente un idioma, forzar inglés
            if not user_selected:
                # Establecer inglés como predeterminado (sobrescribir cualquier idioma existente)
                request.session[language_key] = settings.LANGUAGE_CODE
                request.session.modified = True
                translation.activate(settings.LANGUAGE_CODE)
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
        
        return response

