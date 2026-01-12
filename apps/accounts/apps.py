from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Cuentas de Usuario'

    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.accounts.signals  # noqa
