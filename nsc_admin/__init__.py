# NSC International Admin Dashboard

# Aplicar parche para compatibilidad con Python 3.14 si es necesario
try:
    from .patch_django_context import *
except ImportError:
    pass
