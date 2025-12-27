from django.contrib import admin

from .models import (
    City,
    Country,
    Hotel,
    HotelAmenity,
    HotelImage,
    HotelReservation,
    HotelRoom,
    HotelRoomImage,
    HotelService,
    Rule,
    Season,
    Site,
    State,
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "code"]
    ordering = ["name"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "code", "is_active", "created_at"]
    list_filter = ["country", "is_active", "created_at"]
    search_fields = ["name", "code", "country__name"]
    ordering = ["country__name", "name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state", "get_country", "is_active", "created_at"]
    list_filter = ["state__country", "state", "is_active", "created_at"]
    search_fields = ["name", "state__name", "state__country__name"]
    ordering = ["state__country__name", "state__name", "name"]

    def get_country(self, obj):
        return obj.state.country.name

    get_country.short_description = "País"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "year",
        "start_date",
        "end_date",
        "status",
        "is_active",
        "created_at",
    ]
    list_filter = ["status", "is_active", "year", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["-year", "-start_date"]
    date_hierarchy = "start_date"


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ["name", "rule_type", "is_active", "events_count", "created_at"]
    list_filter = ["rule_type", "is_active", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = [
        "site_name",
        "abbreviation",
        "get_city",
        "state",
        "country",
        "is_active",
        "created_at",
    ]
    list_filter = ["country", "state", "city", "is_active", "created_at"]
    search_fields = ["site_name", "abbreviation", "city__name", "address_1", "website"]
    ordering = ["site_name"]
    readonly_fields = ["created_at", "updated_at", "full_address"]

    def get_city(self, obj):
        return obj.city.name if obj.city else "-"

    get_city.short_description = "Ciudad"

    fieldsets = (
        ("Basic Information", {"fields": ("site_name", "abbreviation", "is_active")}),
        (
            "Address",
            {
                "fields": (
                    "address_1",
                    "address_2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                )
            },
        ),
        ("Additional Information", {"fields": ("website", "image", "additional_info")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


# Inlines for Hotel
class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1
    fields = ["image", "title", "alt_text", "order", "is_featured"]
    ordering = ["order", "-is_featured"]


class HotelAmenityInline(admin.TabularInline):
    model = HotelAmenity
    extra = 1
    fields = ["name", "category", "icon", "is_available", "order"]
    ordering = ["category", "order"]


class HotelRoomInline(admin.TabularInline):
    model = HotelRoom
    extra = 0
    fields = ["room_number", "room_type", "capacity", "price_per_night", "is_available"]
    readonly_fields = []


class HotelServiceInline(admin.TabularInline):
    model = HotelService
    extra = 0
    fields = ["service_name", "service_type", "price", "is_per_person", "is_per_night", "is_active"]
    readonly_fields = []


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = [
        "hotel_name",
        "city",
        "state",
        "country",
        "capacity",
        "total_rooms",
        "available_rooms_count",
        "is_active",
    ]
    list_filter = ["country", "state", "city", "is_active", "created_at"]
    search_fields = ["hotel_name", "address", "city__name", "contact_name", "contact_email"]
    ordering = ["hotel_name"]
    readonly_fields = ["created_at", "updated_at", "total_rooms", "available_rooms_count"]
    inlines = [HotelImageInline, HotelAmenityInline, HotelRoomInline, HotelServiceInline]

    fieldsets = (
        (
            "Información Básica",
            {
                "fields": (
                    "hotel_name",
                    "address",
                    "photo",
                    "information",
                    "registration_url",
                    "is_active",
                )
            },
        ),
        (
            "Ubicación",
            {
                "fields": ("city", "state", "country")
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "capacity",
                    "contact_name",
                    "contact_email",
                    "contact_phone",
                )
            },
        ),
        (
            "Estadísticas",
            {
                "fields": ("total_rooms", "available_rooms_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Fechas",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ["hotel", "title", "is_featured", "order", "created_at"]
    list_filter = ["hotel", "is_featured", "created_at"]
    search_fields = ["hotel__hotel_name", "title", "alt_text"]
    ordering = ["hotel", "order", "-is_featured", "-created_at"]
    list_editable = ["order", "is_featured"]


@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ["hotel", "name", "category", "icon", "is_available", "order"]
    list_filter = ["hotel", "category", "icon", "is_available"]
    search_fields = ["hotel__hotel_name", "name", "description"]
    ordering = ["hotel", "category", "order", "name"]
    list_editable = ["order", "is_available"]

    fieldsets = (
        (
            "Información Básica",
            {
                "fields": ("hotel", "name", "category", "icon")
            },
        ),
        (
            "Detalles",
            {
                "fields": ("description", "is_available", "order")
            },
        ),
        (
            "Fechas",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(HotelRoomImage)
class HotelRoomImageAdmin(admin.ModelAdmin):
    list_display = ["room", "title", "is_featured", "order", "created_at"]
    list_filter = ["is_featured", "created_at", "room__hotel"]
    search_fields = ["room__room_number", "room__hotel__hotel_name", "title", "alt_text"]
    ordering = ["room", "order", "-is_featured"]


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = [
        "hotel",
        "room_number",
        "room_type",
        "capacity",
        "price_per_night",
        "is_available",
    ]
    list_filter = ["hotel", "room_type", "is_available", "created_at"]
    search_fields = ["hotel__hotel_name", "room_number", "description"]
    ordering = ["hotel", "room_number"]
    list_editable = ["is_available"]


@admin.register(HotelService)
class HotelServiceAdmin(admin.ModelAdmin):
    list_display = [
        "hotel",
        "service_name",
        "service_type",
        "price",
        "is_per_person",
        "is_per_night",
        "is_active",
    ]
    list_filter = ["hotel", "service_type", "is_active", "is_per_person", "is_per_night"]
    search_fields = ["hotel__hotel_name", "service_name", "description"]
    ordering = ["hotel", "service_name"]
    list_editable = ["is_active"]


@admin.register(HotelReservation)
class HotelReservationAdmin(admin.ModelAdmin):
    list_display = [
        "hotel",
        "room",
        "guest_name",
        "check_in",
        "check_out",
        "number_of_guests",
        "status",
        "total_amount",
    ]
    list_filter = ["hotel", "status", "check_in", "check_out", "created_at"]
    search_fields = [
        "hotel__hotel_name",
        "room__room_number",
        "guest_name",
        "guest_email",
        "guest_phone",
        "user__email",
    ]
    ordering = ["-check_in"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "check_in"
