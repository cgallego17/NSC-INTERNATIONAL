#!/usr/bin/env python3
"""
Script para probar el hook de changelog manualmente
Simula lo que haría el hook post-commit
"""
import subprocess
import sys
import os
from datetime import datetime

def get_last_commit_info():
    """Obtiene información del último commit"""
    try:
        # Obtener hash corto del commit
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()

        # Obtener mensaje del commit
        commit_msg = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B'],
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()

        # Obtener autor del commit
        commit_author = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%an'],
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()

        # Obtener fecha del commit
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%ai'],
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()

        # Obtener archivos modificados
        files_changed = subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip().split('\n')

        return {
            'hash': commit_hash,
            'message': commit_msg,
            'author': commit_author,
            'date': commit_date,
            'files': [f for f in files_changed if f]
        }
    except subprocess.CalledProcessError as e:
        print(f"Error obteniendo información del commit: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def parse_date(date_str):
    """Convierte la fecha del commit a formato legible"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        # Si hay error con timezone, intentar sin timezone
        try:
            date_part = ' '.join(date_str.split()[:2])
            dt = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str

def format_changelog_entry(commit_info):
    """Formatea una entrada del changelog"""
    date_formatted = parse_date(commit_info['date'])

    # Separar el mensaje en líneas
    msg_lines = commit_info['message'].split('\n')
    main_message = msg_lines[0] if msg_lines else 'Sin mensaje'
    details = msg_lines[1:] if len(msg_lines) > 1 else []

    entry = f"- **[{commit_info['hash']}]** {main_message}\n"
    entry += f"  - *Fecha:* {date_formatted}\n"
    entry += f"  - *Autor:* {commit_info['author']}\n"

    if commit_info['files']:
        # Limitar a 10 archivos para no hacer la entrada muy larga
        files_to_show = commit_info['files'][:10]
        entry += f"  - *Archivos modificados:* {len(commit_info['files'])} archivo(s)\n"
        if len(commit_info['files']) <= 10:
            for file in files_to_show:
                entry += f"    - `{file}`\n"
        else:
            for file in files_to_show:
                entry += f"    - `{file}`\n"
            entry += f"    - ... y {len(commit_info['files']) - 10} archivo(s) más\n"

    if details:
        entry += f"  - *Detalles:*\n"
        for detail in details:
            if detail.strip():
                entry += f"    - {detail.strip()}\n"

    return entry

def update_changelog(commit_info):
    """Actualiza el archivo CHANGELOG.md"""
    changelog_path = 'CHANGELOG.md'

    # Leer el contenido actual del changelog
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = """# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versión]

"""

    # Formatear la nueva entrada
    new_entry = format_changelog_entry(commit_info)

    # Insertar la nueva entrada después de la sección "## [Sin versión]"
    if '## [Sin versión]' in content:
        parts = content.split('## [Sin versión]', 1)
        # Obtener la fecha actual para la última actualización
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_content = parts[0] + '## [Sin versión]\n\n'
        updated_content += f'### Actualizado: {now}\n\n'
        updated_content += new_entry + '\n'
        if len(parts) > 1:
            updated_content += parts[1]
    else:
        # Si no existe la sección, agregarla al principio
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_content = content
        updated_content += '## [Sin versión]\n\n'
        updated_content += f'### Actualizado: {now}\n\n'
        updated_content += new_entry + '\n'

    # Escribir el contenido actualizado
    try:
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✓ CHANGELOG.md actualizado con el commit {commit_info['hash']}")
        return True
    except Exception as e:
        print(f"Error escribiendo CHANGELOG.md: {e}")
        return False

def main():
    """Función principal del script de prueba"""
    print("Probando hook de changelog...")

    # Obtener información del último commit
    commit_info = get_last_commit_info()

    if not commit_info:
        print("No se pudo obtener información del commit")
        sys.exit(1)

    print(f"Commit: {commit_info['hash']}")
    print(f"Mensaje: {commit_info['message'][:50]}...")
    print(f"Autor: {commit_info['author']}")
    print(f"Archivos: {len(commit_info['files'])}")

    # Actualizar el changelog
    success = update_changelog(commit_info)

    if success:
        print("\n✓ Changelog actualizado correctamente")
    else:
        print("\n✗ Error al actualizar changelog")
        sys.exit(1)

if __name__ == '__main__':
    main()
