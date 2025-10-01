from django.contrib import admin

from .models import City, Country, Rule, Season, Site, State


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
