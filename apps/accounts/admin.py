from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    Team,
    Player,
    PlayerParent,
    DashboardContent,
    HomeBanner,
    SiteSettings,
    Sponsor,
    DashboardBanner,
    UserWallet,
    WalletTransaction,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "user_type", "phone", "city", "is_active", "created_at"]
    list_filter = ["user_type", "is_active", "created_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "manager",
        "city",
        "players_count",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at", "country"]
    search_fields = [
        "name",
        "city",
        "state",
        "manager__username",
        "manager__first_name",
        "manager__last_name",
    ]
    readonly_fields = ["created_at", "updated_at", "players_count"]

    def players_count(self, obj):
        return obj.players.filter(is_active=True).count()

    players_count.short_description = "Jugadores"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "team",
        "position",
        "jersey_number",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "position", "team", "created_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "team__name",
        "jersey_number",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PlayerParent)
class PlayerParentAdmin(admin.ModelAdmin):
    list_display = [
        "parent",
        "player",
        "relationship",
        "is_primary",
        "can_pickup",
        "created_at",
    ]
    list_filter = ["relationship", "is_primary", "can_pickup", "created_at"]
    search_fields = [
        "parent__username",
        "parent__first_name",
        "parent__last_name",
        "player__user__username",
        "player__user__first_name",
        "player__user__last_name",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DashboardContent)
class DashboardContentAdmin(admin.ModelAdmin):
    list_display = ["title", "user_type", "is_active", "order", "created_at"]
    list_filter = ["user_type", "is_active", "created_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Contenido de Bienvenida",
            {
                "fields": ("title", "user_type", "content", "is_active", "order"),
                "description": "Configure el contenido HTML que se mostrará en la zona de bienvenida del dashboard según el tipo de usuario. Puede usar HTML completo para personalizar el diseño. Seleccione 'Todos los Usuarios' para que se muestre a todos, o un tipo específico (Manager, Padre/Acudiente, Jugador)."
            }
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('admin/js/core.js',)


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ["title", "banner_type", "is_active", "order", "created_at"]
    list_filter = ["banner_type", "is_active", "created_at"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Información General",
            {"fields": ("title", "description", "banner_type", "is_active", "order")},
        ),
        (
            "Imagen",
            {"fields": ("image",), "description": 'Usar si el tipo es "Imagen"'},
        ),
        (
            "Gradiente",
            {
                "fields": ("gradient_color_1", "gradient_color_2", "gradient_color_3"),
                "description": 'Usar si el tipo es "Gradiente con Texto"',
            },
        ),
        (
            "Botones",
            {"fields": ("button_text", "button_url", "button_text_2", "button_url_2")},
        ),
        ("Icono", {"fields": ("icon_class",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Solo permitir una instancia
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar
        return False

    fieldsets = (
        (
            "Sección Schedule - Inglés",
            {
                "fields": (
                    "schedule_image",
                    "schedule_title_en",
                    "schedule_subtitle_en",
                    "schedule_description_en",
                )
            },
        ),
        (
            "Sección Schedule - Español",
            {
                "fields": (
                    "schedule_title_es",
                    "schedule_subtitle_es",
                    "schedule_description_es",
                )
            },
        ),
        (
            "Sección Showcase - Inglés",
            {
                "fields": (
                    "showcase_image",
                    "showcase_title_en",
                    "showcase_subtitle_en",
                    "showcase_description_en",
                )
            },
        ),
        (
            "Sección Showcase - Español",
            {
                "fields": (
                    "showcase_title_es",
                    "showcase_subtitle_es",
                    "showcase_description_es",
                )
            },
        ),
        (
            "Auditoría",
            {"fields": ("updated_at",), "classes": ("collapse",)},
        ),
    )
    readonly_fields = ["updated_at"]


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "order", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Información",
            {"fields": ("name", "logo", "website_url", "is_active", "order")},
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ["user", "balance", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Información",
            {"fields": ("user", "balance")},
        ),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "wallet",
        "transaction_type",
        "amount",
        "balance_after",
        "created_at",
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = [
        "wallet__user__username",
        "wallet__user__first_name",
        "wallet__user__last_name",
        "description",
        "reference_id",
    ]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
