from django.urls import Resolver404, resolve


def sidebar_context(request):
    """
    Context processor para determinar el estado activo del sidebar
    """
    current_path = request.path
    active_section = None
    active_subsection = None

    # Mapeo de rutas a secciones del sidebar
    route_mapping = {
        "dashboard": {"section": "dashboard", "subsection": None},
        "events:dashboard": {"section": "dashboard", "subsection": None},
        "events:list": {"section": "events", "subsection": "list"},
        "events:create": {"section": "events", "subsection": "create"},
        "events:calendar": {"section": "events", "subsection": "calendar"},
        "events:detail": {"section": "events", "subsection": "list"},
        "events:update": {"section": "events", "subsection": "list"},
        "events:delete": {"section": "events", "subsection": "list"},
        "events:attend": {"section": "events", "subsection": "list"},
        "locations:country_list": {"section": "locations", "subsection": "countries"},
        "locations:state_list": {"section": "locations", "subsection": "states"},
        "locations:city_list": {"section": "locations", "subsection": "cities"},
        "locations:season_list": {"section": "configuration", "subsection": "seasons"},
        "locations:country_create": {"section": "locations", "subsection": "countries"},
        "locations:country_update": {"section": "locations", "subsection": "countries"},
        "locations:country_delete": {"section": "locations", "subsection": "countries"},
        "locations:state_create": {"section": "locations", "subsection": "states"},
        "locations:state_update": {"section": "locations", "subsection": "states"},
        "locations:state_delete": {"section": "locations", "subsection": "states"},
        "locations:city_create": {"section": "locations", "subsection": "cities"},
        "locations:city_update": {"section": "locations", "subsection": "cities"},
        "locations:city_delete": {"section": "locations", "subsection": "cities"},
        "locations:season_create": {
            "section": "configuration",
            "subsection": "seasons",
        },
        "locations:season_update": {
            "section": "configuration",
            "subsection": "seasons",
        },
        "locations:season_delete": {
            "section": "configuration",
            "subsection": "seasons",
        },
        "locations:rule_list": {"section": "configuration", "subsection": "rules"},
        "locations:rule_create": {"section": "configuration", "subsection": "rules"},
        "locations:rule_update": {"section": "configuration", "subsection": "rules"},
        "locations:rule_delete": {"section": "configuration", "subsection": "rules"},
        "locations:site_list": {"section": "locations", "subsection": "sites"},
        "locations:site_detail": {"section": "locations", "subsection": "sites"},
        "locations:site_create": {"section": "locations", "subsection": "sites"},
        "locations:site_update": {"section": "locations", "subsection": "sites"},
        "locations:site_delete": {"section": "locations", "subsection": "sites"},
        "locations:admin_hotel_list": {"section": "hotels", "subsection": "hotel_list"},
        "locations:admin_hotel_detail": {
            "section": "hotels",
            "subsection": "hotel_list",
        },
        "locations:admin_hotel_create": {
            "section": "hotels",
            "subsection": "hotel_list",
        },
        "locations:admin_hotel_update": {
            "section": "hotels",
            "subsection": "hotel_list",
        },
        "locations:admin_hotel_delete": {
            "section": "hotels",
            "subsection": "hotel_list",
        },
        "locations:admin_hotel_room_list": {
            "section": "hotels",
            "subsection": "hotel_room_list",
        },
        "locations:admin_hotel_room_create": {
            "section": "hotels",
            "subsection": "hotel_room_list",
        },
        "locations:admin_hotel_room_update": {
            "section": "hotels",
            "subsection": "hotel_room_list",
        },
        "locations:admin_hotel_room_delete": {
            "section": "hotels",
            "subsection": "hotel_room_list",
        },
        "locations:admin_hotel_service_list": {
            "section": "hotels",
            "subsection": "hotel_service_list",
        },
        "locations:admin_hotel_service_create": {
            "section": "hotels",
            "subsection": "hotel_service_list",
        },
        "locations:admin_hotel_service_update": {
            "section": "hotels",
            "subsection": "hotel_service_list",
        },
        "locations:admin_hotel_service_delete": {
            "section": "hotels",
            "subsection": "hotel_service_list",
        },
        "locations:admin_hotel_reservation_list": {
            "section": "hotels",
            "subsection": "hotel_reservation_list",
        },
        "locations:admin_hotel_reservation_detail": {
            "section": "hotels",
            "subsection": "hotel_reservation_list",
        },
        "locations:admin_hotel_reservation_create": {
            "section": "hotels",
            "subsection": "hotel_reservation_list",
        },
        "locations:admin_hotel_reservation_update": {
            "section": "hotels",
            "subsection": "hotel_reservation_list",
        },
        "locations:admin_hotel_reservation_delete": {
            "section": "hotels",
            "subsection": "hotel_reservation_list",
        },
        "accounts:player_list": {"section": "players", "subsection": "player_list"},
        "accounts:player_detail": {"section": "players", "subsection": "player_list"},
        "accounts:player_register": {"section": "players", "subsection": "player_list"},
        "accounts:player_edit": {"section": "players", "subsection": "player_list"},
    }

    try:
        # Resolver la URL actual
        resolved = resolve(current_path)
        view_name = resolved.view_name

        # Buscar en el mapeo
        if view_name in route_mapping:
            mapping = route_mapping[view_name]
            active_section = mapping["section"]
            active_subsection = mapping["subsection"]
        else:
            # Fallback: determinar por la ruta
            if current_path == "/dashboard/" or current_path == "/dashboard":
                active_section = "dashboard"
            elif current_path.startswith("/events/"):
                if current_path == "/events/" or current_path == "/events":
                    active_section = "dashboard"
                elif "/list" in current_path:
                    active_section = "events"
                    active_subsection = "list"
                elif "/calendar" in current_path:
                    active_section = "events"
                    active_subsection = "calendar"
                else:
                    active_section = "events"
                    active_subsection = "list"
            elif current_path.startswith("/locations/"):
                if "/hotels" in current_path or "/hotel" in current_path:
                    active_section = "hotels"
                    if (
                        "/hotel-reservations" in current_path
                        or "/hotel_reservations" in current_path
                    ):
                        active_subsection = "hotel_reservation_list"
                    elif (
                        "/hotel-rooms" in current_path or "/hotel_rooms" in current_path
                    ):
                        active_subsection = "hotel_room_list"
                    elif (
                        "/hotel-services" in current_path
                        or "/hotel_services" in current_path
                    ):
                        active_subsection = "hotel_service_list"
                    else:
                        active_subsection = "hotel_list"
                elif "/seasons" in current_path or "/rules" in current_path:
                    active_section = "configuration"
                    if "/seasons" in current_path:
                        active_subsection = "seasons"
                    elif "/rules" in current_path:
                        active_subsection = "rules"
                else:
                    active_section = "locations"
                    if "/countries" in current_path:
                        active_subsection = "countries"
                    elif "/states" in current_path:
                        active_subsection = "states"
                    elif "/cities" in current_path:
                        active_subsection = "cities"
                    else:
                        active_subsection = "countries"
            elif current_path.startswith("/accounts/"):
                if "/players" in current_path:
                    active_section = "players"
                    active_subsection = "player_list"

    except Resolver404:
        # Si no se puede resolver la URL, usar fallback por ruta
        if current_path == "/dashboard/" or current_path == "/dashboard":
            active_section = "dashboard"
        elif current_path.startswith("/events/"):
            active_section = "events"
        elif current_path.startswith("/locations/"):
            if "/hotels" in current_path or "/hotel" in current_path:
                active_section = "hotels"
            elif "/seasons" in current_path or "/rules" in current_path:
                active_section = "configuration"
            else:
                active_section = "locations"
        elif current_path.startswith("/accounts/"):
            if "/users" in current_path:
                active_section = "users"
            elif "/players" in current_path:
                active_section = "players"

    return {
        "active_section": active_section,
        "active_subsection": active_subsection,
    }
