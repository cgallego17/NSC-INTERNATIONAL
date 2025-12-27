"""
Template tags personalizados para traducciones de contenido dinámico
"""

from django import template
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag
def translate_site_setting(value, setting_type):
    """
    Traduce valores de site_settings según el idioma actual

    Args:
        value: El valor a traducir
        setting_type: Tipo de setting ('schedule_title', 'schedule_subtitle', etc.)

    Returns:
        Valor traducido según el idioma actual
    """
    lang = get_language() or "en"
    lang_code = lang[:2]

    # Diccionario de traducciones
    translations = {
        "schedule_title": {
            "2026 EVENT CALENDAR": {
                "en": "2026 EVENT CALENDAR",
                "es": "CALENDARIO DE EVENTOS 2026",
            },
            "CALENDARIO DE EVENTOS 2026": {
                "en": "2026 EVENT CALENDAR",
                "es": "CALENDARIO DE EVENTOS 2026",
            },
        },
        "schedule_subtitle": {
            "REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026": {
                "en": "REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026",
                "es": "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026",
            },
            "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026": {
                "en": "REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026",
                "es": "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026",
            },
        },
        "showcase_title": {
            "SHOWCASES AND PROSPECT GATEWAYS": {
                "en": "SHOWCASES AND PROSPECT GATEWAYS",
                "es": "SHOWCASES Y PORTALES DE PROSPECTO",
            }
        },
        "showcase_subtitle": {
            "REGIONAL AND NATIONAL SHOWCASES": {
                "en": "REGIONAL AND NATIONAL SHOWCASES",
                "es": "SHOWCASES REGIONALES Y NACIONALES",
            }
        },
    }

    if not value:
        return value

    value_str = str(value).strip()

    if setting_type in translations and value_str in translations[setting_type]:
        return translations[setting_type][value_str].get(lang_code, value_str)

    return value_str


@register.simple_tag
def translate_schedule_description(description):
    """Traduce la descripción del schedule"""
    lang = get_language() or "en"
    lang_code = lang[:2]

    if not description:
        if lang_code == "es":
            return "A medida que avanzamos hacia 2026, NSC International continúa elevando su plataforma de torneos y exhibiciones. Con una expansión de la presencia regional para edades 7U-18U, nuevos y mejorados eventos de Campeonatos Nacionales y Regionales, y una programación aún más amplia de exhibiciones en todo el país, NSC se mantiene dedicado a ofrecer el más alto estándar de competencia y experiencia para jugadores, entrenadores y familias por igual."
        else:
            return "As we move forward into 2026, NSC International continues to elevate its tournament and showcase platform. With a regional presence expansion for ages 7U-18U, new and improved National and Regional Championship events, and an even broader showcase schedule across the country, NSC remains dedicated to providing the highest standard of competition and experience for players, coaches and families alike."

    description_str = str(description)

    # Si el texto contiene palabras clave en inglés y el idioma es español, traducirlo
    if lang_code == "es" and (
        "As we move forward" in description_str
        or "continues to elevate" in description_str
    ):
        return "A medida que avanzamos hacia 2026, NSC International continúa elevando su plataforma de torneos y exhibiciones. Con una expansión de la presencia regional para edades 7U-18U, nuevos y mejorados eventos de Campeonatos Nacionales y Regionales, y una programación aún más amplia de exhibiciones en todo el país, NSC se mantiene dedicado a ofrecer el más alto estándar de competencia y experiencia para jugadores, entrenadores y familias por igual."

    return description_str


@register.simple_tag
def translate_showcase_description(description):
    """Traduce la descripción del showcase"""
    lang = get_language() or "en"
    lang_code = lang[:2]

    if not description:
        if lang_code == "es":
            return "Perfect Game se complace en ofrecer showcases (HS) y Prospect Gateways (13U/14U) en todo el país para el calendario 2025. Esto incluye eventos regionales para todas las edades y nuevos eventos solo por invitación. PG se esfuerza por ofrecer los mejores eventos y experiencias para todos los jugadores, entrenadores y familias en todo el país."
        else:
            return "Perfect Game is thrilled to offer showcases (HS) and Prospect Gateways (13U/14U) across the country for the 2025 calendar. This includes regional events for all ages and new invite only events! PG strives to delivery the very best events and experience for all players, coaches and families across the country."

    description_str = str(description)

    # Si el texto contiene palabras clave en inglés y el idioma es español, traducirlo
    if lang_code == "es" and (
        "Perfect Game is thrilled" in description_str
        or "showcases (HS)" in description_str
    ):
        return "Perfect Game se complace en ofrecer showcases (HS) y Prospect Gateways (13U/14U) en todo el país para el calendario 2025. Esto incluye eventos regionales para todas las edades y nuevos eventos solo por invitación. PG se esfuerza por ofrecer los mejores eventos y experiencias para todos los jugadores, entrenadores y familias en todo el país."

    return description_str


@register.filter
def translate_choice(value):
    """
    Traduce valores de choices del modelo según el idioma actual
    Usa gettext para traducir automáticamente si el valor está en los archivos .po
    """
    from django.utils.translation import gettext as _

    if not value:
        return value

    # Intentar traducir el valor directamente
    try:
        return _(str(value))
    except:
        return value
