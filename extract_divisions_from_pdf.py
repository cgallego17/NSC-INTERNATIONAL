"""
Script para extraer divisiones del PDF
"""

import os
import sys

# Intentar importar librerías para leer PDF
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

pdf_path = "Baseball_Divisions.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: No se encontró el archivo {pdf_path}")
    sys.exit(1)

print(f"Leyendo PDF: {pdf_path}")

# Intentar con pdfplumber primero (mejor para extraer texto)
if HAS_PDFPLUMBER:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        print("\n=== CONTENIDO EXTRAÍDO DEL PDF ===")
        print(text)
        print("=" * 70)
    except Exception as e:
        print(f"Error con pdfplumber: {e}")
        HAS_PDFPLUMBER = False

# Intentar con PyPDF2 como alternativa
if not HAS_PDFPLUMBER and HAS_PYPDF2:
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        print("\n=== CONTENIDO EXTRAÍDO DEL PDF ===")
        print(text)
        print("=" * 70)
    except Exception as e:
        print(f"Error con PyPDF2: {e}")

if not HAS_PDFPLUMBER and not HAS_PYPDF2:
    print("\n⚠ No se encontraron librerías para leer PDFs.")
    print("Instala una de estas opciones:")
    print("  pip install pdfplumber")
    print("  pip install PyPDF2")
    print("\nPor favor, proporciona manualmente las divisiones del PDF.")





