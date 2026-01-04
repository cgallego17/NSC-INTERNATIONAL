"""
Mixins para manejo de permisos y autenticación
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class StaffRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere que el usuario sea staff o superuser.
    Si no cumple, redirige al panel con mensaje de error.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(
                request,
                "No tienes permisos para acceder a esta sección. Se requieren permisos de administrador.",
            )
            return redirect("panel")

        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere que el usuario sea manager de equipo.
    Si no cumple, redirige al panel con mensaje de error.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        # Verificar si tiene perfil y es manager
        if not hasattr(request.user, "profile"):
            messages.error(
                request,
                "No tienes un perfil configurado. Por favor, completa tu perfil.",
            )
            return redirect("accounts:profile")

        if not request.user.profile.is_team_manager:
            messages.error(
                request, "Solo los managers de equipo pueden acceder a esta sección."
            )
            return redirect("panel")

        return super().dispatch(request, *args, **kwargs)


class OwnerOrStaffRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere que el usuario sea el dueño del objeto o sea staff.
    Debe usarse con vistas que tengan un método get_object().
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        # Si es staff, permitir acceso
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Obtener el objeto y verificar si es el dueño
        obj = self.get_object()

        # Verificar si tiene atributo 'user', 'manager', 'owner', u 'organizer'
        if hasattr(obj, "user"):
            if obj.user != request.user:
                messages.error(
                    request, "No tienes permisos para acceder a este recurso."
                )
                return redirect("panel")
        elif hasattr(obj, "manager"):
            if obj.manager != request.user:
                messages.error(
                    request, "No tienes permisos para acceder a este recurso."
                )
                return redirect("panel")
        elif hasattr(obj, "organizer"):
            if obj.organizer != request.user:
                messages.error(
                    request, "No tienes permisos para acceder a este recurso."
                )
                return redirect("panel")
        elif hasattr(obj, "owner"):
            if obj.owner != request.user:
                messages.error(
                    request, "No tienes permisos para acceder a este recurso."
                )
                return redirect("panel")
        else:
            # Si no tiene atributo de ownership, requerir staff
            messages.error(request, "No tienes permisos para acceder a este recurso.")
            return redirect("panel")

        return super().dispatch(request, *args, **kwargs)
