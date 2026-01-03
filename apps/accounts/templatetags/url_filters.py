"""
Filtros personalizados para URLs
"""
from django import template

register = template.Library()


@register.filter
def clean_localhost_url(url):
    """
    Limpia URLs que contengan http://127.0.0.1:8000 o http://localhost:8000
    y las convierte en URLs relativas
    """
    if not url:
        return url

    url_str = str(url)
    # Remover http://127.0.0.1:8000
    url_str = url_str.replace('http://127.0.0.1:8000', '')
    # Remover http://localhost:8000
    url_str = url_str.replace('http://localhost:8000', '')
    # Remover https://127.0.0.1:8000 (por si acaso)
    url_str = url_str.replace('https://127.0.0.1:8000', '')
    # Remover https://localhost:8000 (por si acaso)
    url_str = url_str.replace('https://localhost:8000', '')

    return url_str

