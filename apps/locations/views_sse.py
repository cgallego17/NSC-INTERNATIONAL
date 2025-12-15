"""
Vistas para Server-Sent Events (SSE) - Actualizaciones de sitios en tiempo real
"""
import json
import time
from django.http import StreamingHttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .models import Site


@login_required
@never_cache
@require_GET
def site_updates_stream(request):
    """
    Stream de actualizaciones de sitios usando Server-Sent Events (SSE)
    """
    city_id = request.GET.get('city_id')
    
    if not city_id:
        def error_stream():
            yield f"data: {json.dumps({'error': 'city_id requerido'})}\n\n"
        return StreamingHttpResponse(error_stream(), content_type='text/event-stream')
    
    def event_stream():
        """Generador de eventos SSE"""
        last_count = 0
        last_site_ids = set()
        
        try:
            # Obtener sitios iniciales
            sites = Site.objects.filter(
                city_id=city_id,
                is_active=True
            ).values_list('id', flat=True)
            last_count = sites.count()
            last_site_ids = set(str(id) for id in sites)
            
            # Enviar evento inicial
            yield f"data: {json.dumps({'type': 'connected', 'city_id': city_id})}\n\n"
            
            # Monitorear cambios
            while True:
                try:
                    # Verificar cambios cada 2 segundos
                    time.sleep(2)
                    
                    current_sites = Site.objects.filter(
                        city_id=city_id,
                        is_active=True
                    )
                    current_count = current_sites.count()
                    current_site_ids = set(str(site.id) for site in current_sites)
                    
                    # Detectar cambios
                    if current_count != last_count or current_site_ids != last_site_ids:
                        # Hay cambios, enviar evento
                        sites_data = list(current_sites.values(
                            'id', 'site_name', 'abbreviation',
                            'city_id', 'state_id', 'country_id'
                        ))
                        
                        event_data = {
                            'type': 'sites_updated',
                            'city_id': int(city_id),
                            'sites': sites_data,
                            'count': current_count
                        }
                        
                        yield f"data: {json.dumps(event_data)}\n\n"
                        
                        last_count = current_count
                        last_site_ids = current_site_ids
                    
                    # Enviar heartbeat cada 30 segundos para mantener conexión
                    yield ": heartbeat\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                    break
                    
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Deshabilitar buffering en nginx
    return response
















