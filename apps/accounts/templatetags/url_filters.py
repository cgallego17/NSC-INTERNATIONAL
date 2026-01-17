"""
Filtros personalizados para URLs y números
"""

import re
from decimal import Decimal, InvalidOperation

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
    url_str = url_str.replace("http://127.0.0.1:8000", "")
    # Remover http://localhost:8000
    url_str = url_str.replace("http://localhost:8000", "")
    # Remover https://127.0.0.1:8000 (por si acaso)
    url_str = url_str.replace("https://127.0.0.1:8000", "")
    # Remover https://localhost:8000 (por si acaso)
    url_str = url_str.replace("https://localhost:8000", "")

    return url_str


@register.filter
def intcomma_dot(value):
    """
    Formatea un número con puntos como separadores de miles (formato español/europeo).
    El valor ya viene formateado con floatformat (ej: "1000.50")
    Convierte: "5752.90" -> "5.752,90" o "1000" -> "1.000"
    Usa puntos para miles y comas para decimales.
    """
    if value is None or value == "":
        return "0,00"

    try:
        # Convertir a string (a veces viene ya con separadores de miles/decimales)
        raw = str(value).strip()

        if raw in ["0", "0.0", "0.00", "0,0", "0,00"]:
            return "0,00"

        # Normalizar a un formato numérico simple con '.' como separador decimal y sin miles
        # Soporta entradas tipo: "3435.68", "3,435.68", "3.435,68", etc.
        s = raw.replace(" ", "")
        s = re.sub(r"[^0-9,\.-]", "", s)

        last_dot = s.rfind(".")
        last_comma = s.rfind(",")

        decimal_sep = None
        thousands_sep = None

        if last_dot != -1 and last_comma != -1:
            # El separador que aparece más a la derecha suele ser el decimal
            if last_dot > last_comma:
                decimal_sep = "."
                thousands_sep = ","
            else:
                decimal_sep = ","
                thousands_sep = "."
        elif last_comma != -1:
            # Solo comas: si la parte final parece decimal (1-2 dígitos), usar coma como decimal
            tail = s.split(",")[-1]
            if len(tail) in (1, 2):
                decimal_sep = ","
            elif s.count(",") > 1:
                decimal_sep = ","
            else:
                thousands_sep = ","
        elif last_dot != -1:
            # Solo puntos: si la parte final parece decimal (1-2 dígitos), usar punto como decimal
            tail = s.split(".")[-1]
            if len(tail) in (1, 2):
                decimal_sep = "."
            elif s.count(".") > 1:
                decimal_sep = "."
            else:
                thousands_sep = "."

        if thousands_sep:
            s = s.replace(thousands_sep, "")
        if decimal_sep and decimal_sep != ".":
            # Reemplazar el separador decimal a '.' para normalizar
            s = s.replace(decimal_sep, ".")

        # Extraer signo (si existiera)
        sign = ""
        if s.startswith("-"):
            sign = "-"
            s = s[1:]

        if "." in s:
            integer_part, decimal_part = s.split(".", 1)
        else:
            integer_part, decimal_part = s, "00"

        decimal_part = (decimal_part or "")[:2]
        if len(decimal_part) == 0:
            decimal_part = "00"
        elif len(decimal_part) == 1:
            decimal_part = decimal_part + "0"

        integer_part = integer_part or "0"

        # Agregar puntos como separadores de miles a la parte entera
        integer_part = integer_part[::-1]
        integer_part = ".".join(
            integer_part[i : i + 3] for i in range(0, len(integer_part), 3)
        )
        integer_part = integer_part[::-1]

        return f"{sign}{integer_part},{decimal_part}"
    except (ValueError, TypeError):
        return str(value) if value else "0,00"


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


@register.filter
def mul(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal("0")
