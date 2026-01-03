#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Aplicar parche para compatibilidad con Python 3.14 si es necesario
try:
    from nsc_admin.patch_django_context import *
except ImportError:
    pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
