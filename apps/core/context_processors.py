from django.urls import resolve, Resolver404


def sidebar_context(request):
    """
    Context processor para determinar el estado activo del sidebar
    """
    current_path = request.path
    active_section = None
    active_subsection = None
    
    # Mapeo de rutas a secciones del sidebar
    route_mapping = {
        'events:dashboard': {'section': 'dashboard', 'subsection': None},
        'events:list': {'section': 'events', 'subsection': 'list'},
        'events:create': {'section': 'events', 'subsection': 'create'},
        'events:calendar': {'section': 'events', 'subsection': 'calendar'},
        'events:detail': {'section': 'events', 'subsection': 'list'},
        'events:update': {'section': 'events', 'subsection': 'list'},
        'events:delete': {'section': 'events', 'subsection': 'list'},
        'events:attend': {'section': 'events', 'subsection': 'list'},
        'locations:country_list': {'section': 'locations', 'subsection': 'countries'},
        'locations:state_list': {'section': 'locations', 'subsection': 'states'},
        'locations:city_list': {'section': 'locations', 'subsection': 'cities'},
        'locations:season_list': {'section': 'configuration', 'subsection': 'seasons'},
        'locations:country_create': {'section': 'locations', 'subsection': 'countries'},
        'locations:country_update': {'section': 'locations', 'subsection': 'countries'},
        'locations:country_delete': {'section': 'locations', 'subsection': 'countries'},
        'locations:state_create': {'section': 'locations', 'subsection': 'states'},
        'locations:state_update': {'section': 'locations', 'subsection': 'states'},
        'locations:state_delete': {'section': 'locations', 'subsection': 'states'},
        'locations:city_create': {'section': 'locations', 'subsection': 'cities'},
        'locations:city_update': {'section': 'locations', 'subsection': 'cities'},
        'locations:city_delete': {'section': 'locations', 'subsection': 'cities'},
        'locations:season_create': {'section': 'configuration', 'subsection': 'seasons'},
        'locations:season_update': {'section': 'configuration', 'subsection': 'seasons'},
        'locations:season_delete': {'section': 'configuration', 'subsection': 'seasons'},
        'locations:rule_list': {'section': 'configuration', 'subsection': 'rules'},
        'locations:rule_create': {'section': 'configuration', 'subsection': 'rules'},
        'locations:rule_update': {'section': 'configuration', 'subsection': 'rules'},
        'locations:rule_delete': {'section': 'configuration', 'subsection': 'rules'},
        'locations:site_list': {'section': 'locations', 'subsection': 'sites'},
        'locations:site_detail': {'section': 'locations', 'subsection': 'sites'},
        'locations:site_create': {'section': 'locations', 'subsection': 'sites'},
        'locations:site_update': {'section': 'locations', 'subsection': 'sites'},
        'locations:site_delete': {'section': 'locations', 'subsection': 'sites'},
    }
    
    try:
        # Resolver la URL actual
        resolved = resolve(current_path)
        view_name = resolved.view_name
        
        # Buscar en el mapeo
        if view_name in route_mapping:
            mapping = route_mapping[view_name]
            active_section = mapping['section']
            active_subsection = mapping['subsection']
        else:
            # Fallback: determinar por la ruta
            if current_path.startswith('/events/'):
                if current_path == '/events/' or current_path == '/events':
                    active_section = 'dashboard'
                elif '/list' in current_path:
                    active_section = 'events'
                    active_subsection = 'list'
                elif '/create' in current_path:
                    active_section = 'events'
                    active_subsection = 'create'
                elif '/calendar' in current_path:
                    active_section = 'events'
                    active_subsection = 'calendar'
                else:
                    active_section = 'events'
                    active_subsection = 'list'
            elif current_path.startswith('/locations/'):
                if '/seasons' in current_path or '/rules' in current_path:
                    active_section = 'configuration'
                    if '/seasons' in current_path:
                        active_subsection = 'seasons'
                    elif '/rules' in current_path:
                        active_subsection = 'rules'
                else:
                    active_section = 'locations'
                    if '/countries' in current_path:
                        active_subsection = 'countries'
                    elif '/states' in current_path:
                        active_subsection = 'states'
                    elif '/cities' in current_path:
                        active_subsection = 'cities'
                    else:
                        active_subsection = 'countries'
    
    except Resolver404:
        # Si no se puede resolver la URL, usar fallback por ruta
        if current_path.startswith('/events/'):
            active_section = 'events'
        elif current_path.startswith('/locations/'):
            if '/seasons' in current_path or '/rules' in current_path:
                active_section = 'configuration'
            else:
                active_section = 'locations'
    
    return {
        'active_section': active_section,
        'active_subsection': active_subsection,
    }
