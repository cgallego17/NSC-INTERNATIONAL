"""
Filtros personalizados para URLs y números
"""
from django import template
import re

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


@register.filter
def intcomma_dot(value):
    """
    Formatea un número con puntos como separadores de miles (formato español/europeo).
    El valor ya viene formateado con floatformat (ej: "1000.50")
    Convierte: "5752.90" -> "5.752,90" o "1000" -> "1.000"
    Usa puntos para miles y comas para decimales.
    """
    if value is None or value == '':
        return '0,00'

    try:
        # Convertir a string (ya viene formateado con floatformat)
        value_str = str(value).strip()

        # Si el valor es "0" o "0.00", retornar "0,00"
        if value_str in ['0', '0.0', '0.00', '0,0', '0,00']:
            return '0,00'

        # Si es un número decimal, separar parte entera y decimal
        if '.' in value_str:
            parts = value_str.split('.')
            integer_part = parts[0]
            decimal_part = parts[1] if len(parts) > 1 else '00'
            # Asegurar que siempre tenga 2 decimales
            if len(decimal_part) == 1:
                decimal_part = decimal_part + '0'
            elif len(decimal_part) == 0:
                decimal_part = '00'
        else:
            integer_part = value_str
            decimal_part = '00'

        # Agregar puntos como separadores de miles a la parte entera
        # Invertir la cadena, agregar puntos cada 3 dígitos, y volver a invertir
        if integer_part:
            integer_part = integer_part[::-1]
            integer_part = '.'.join(integer_part[i:i+3] for i in range(0, len(integer_part), 3))
            integer_part = integer_part[::-1]

        # Reconstruir el número: usar punto para miles y coma para decimales (formato español)
        return f"{integer_part},{decimal_part}"
    except (ValueError, TypeError):
        return str(value) if value else '0,00'


@register.filter
def make_range(value):
    """
    Crea un rango de números del 1 al valor especificado.
    Útil para iterar en templates cuando necesitas un bucle for con un número específico de iteraciones.
    Ejemplo: {% for i in 5|make_range %} -> itera 5 veces (1, 2, 3, 4, 5)
    """
    try:
        num = int(value)
        if num > 0:
            return range(1, num + 1)
        return []
    except (ValueError, TypeError):
        return []

