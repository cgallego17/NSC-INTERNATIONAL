"""
WSGI config for nsc_admin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

# Aplicar parche para compatibilidad con Python 3.14 si es necesario
try:
    from nsc_admin.patch_django_context import *
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc_admin.settings")

application = get_wsgi_application()
