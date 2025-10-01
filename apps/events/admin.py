from django.contrib import admin
from django.utils.html import format_html

from .models import Division, Event, EventAttendance, EventCategory, EventComment, EventReminder


class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 0
    readonly_fields = ["registered_at"]
    fields = ["user", "status", "registered_at", "notes"]


class EventCommentInline(admin.TabularInline):
    model = EventComment
    extra = 0
    readonly_fields = ["created_at", "updated_at"]
    fields = ["user", "comment", "is_internal", "created_at"]


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color_display", "icon", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.color,
            obj.color,
        )

    color_display.short_description = "Color"


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ["name", "age_range", "skill_level", "is_active", "created_at"]
    list_filter = ["is_active", "skill_level", "created_at"]
    search_fields = ["name", "description", "skill_level"]
    readonly_fields = ["created_at", "updated_at", "age_range"]
    
    fieldsets = (
        ("Información Básica", {"fields": ("name", "description")}),
        ("Configuración de Edad", {"fields": ("age_min", "age_max", "age_range")}),
        ("Configuración de Habilidad", {"fields": ("skill_level",)}),
        ("Estado", {"fields": ("is_active",)}),
        ("Fechas del Sistema", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "division",
        "start_date",
        "end_date",
        "status",
        "priority",
        "organizer",
        "attendees_count",
        "is_public",
    ]
    list_filter = ["status", "priority", "category", "division", "is_public", "requires_registration", "start_date"]
    search_fields = ["title", "description", "location", "organizer__username"]
    readonly_fields = ["created_at", "updated_at", "attendees_count", "is_past", "is_ongoing", "is_upcoming", "is_full"]
    inlines = [EventAttendanceInline, EventCommentInline]

    fieldsets = (
        ("Información Básica", {"fields": ("title", "description", "short_description", "category", "image")}),
        ("Estado y Prioridad", {"fields": ("status", "priority")}),
        ("Fechas y Horarios", {"fields": ("start_date", "end_date", "all_day")}),
        ("Ubicación", {"fields": ("location", "address")}),
        ("Organización", {"fields": ("organizer", "is_public", "requires_registration", "max_attendees")}),
        ("Enlaces y Notas", {"fields": ("external_link", "notes")}),
        (
            "Estadísticas",
            {"fields": ("attendees_count", "is_past", "is_ongoing", "is_upcoming", "is_full"), "classes": ("collapse",)},
        ),
        ("Fechas del Sistema", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def attendees_count(self, obj):
        return obj.attendees_count

    attendees_count.short_description = "Asistentes"


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "status", "registered_at"]
    list_filter = ["status", "registered_at"]
    search_fields = ["event__title", "user__username", "user__first_name", "user__last_name"]
    readonly_fields = ["registered_at"]


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "comment_preview", "is_internal", "created_at"]
    list_filter = ["is_internal", "created_at"]
    search_fields = ["event__title", "user__username", "comment"]
    readonly_fields = ["created_at", "updated_at"]

    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = "Vista Previa"


@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "reminder_type", "minutes_before", "sent", "sent_at"]
    list_filter = ["reminder_type", "sent", "created_at"]
    search_fields = ["event__title", "user__username"]
    readonly_fields = ["created_at", "sent_at"]
