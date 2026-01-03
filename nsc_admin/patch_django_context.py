"""
Parche temporal para Django 4.2.27 con Python 3.14
Soluciona el error: 'super' object has no attribute 'dicts'
Este parche se aplicará automáticamente si Django 4.2.27 está instalado
"""
import sys
import copy

# Solo aplicar el parche si estamos en Python 3.14+
if sys.version_info >= (3, 14):
    try:
        import django
        django_version = django.get_version()

        # Aplicar el parche para Django 4.2.x
        if django_version.startswith('4.2'):
            from django.template import context

            def patched_basecontext_copy(self):
                """Versión parcheada de BaseContext.__copy__ que funciona con Python 3.14"""
                # Crear una nueva instancia directamente en lugar de copy(super())
                duplicate = context.BaseContext()
                duplicate.__class__ = self.__class__
                # Copiar __dict__ manualmente en lugar de usar copy(super())
                duplicate.__dict__.update(self.__dict__)
                duplicate.dicts = self.dicts[:]
                return duplicate

            def patched_context_copy(self):
                """Versión parcheada de Context.__copy__ que funciona con Python 3.14"""
                # Crear una nueva instancia directamente
                duplicate = context.Context()
                duplicate.dicts = self.dicts[:]
                if hasattr(self, 'render_context'):
                    duplicate.render_context = copy.copy(self.render_context) if hasattr(self.render_context, '__dict__') else self.render_context
                return duplicate

            # Aplicar el parche a BaseContext primero
            context.BaseContext.__copy__ = patched_basecontext_copy

            # Aplicar el parche a Context si existe
            if hasattr(context, 'Context'):
                context.Context.__copy__ = patched_context_copy

            print(f"✅ Parche aplicado para Django {django_version} con Python 3.14")
    except ImportError:
        pass
    except Exception as e:
        # Silenciar errores al aplicar el parche
        pass

