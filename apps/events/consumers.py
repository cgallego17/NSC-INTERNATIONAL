import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class SiteConsumer(AsyncWebsocketConsumer):
    """Consumer para actualizaciones de sitios en tiempo real"""
    
    groups = []
    
    async def connect(self):
        """Conectar al WebSocket"""
        try:
            await self.accept()
            logger.info("Cliente WebSocket conectado para actualizaciones de sitios")
            print("✅ Cliente WebSocket conectado para actualizaciones de sitios")
        except Exception as e:
            logger.error(f"Error aceptando conexión WebSocket: {e}")
            print(f"❌ Error aceptando conexión WebSocket: {e}")
    
    async def disconnect(self, close_code):
        """Desconectar del WebSocket"""
        # Desuscribirse de todos los grupos
        if hasattr(self, 'channel_layer') and self.channel_layer:
            for group in self.groups:
                await self.channel_layer.group_discard(group, self.channel_name)
        print(f"Cliente WebSocket desconectado: {close_code}")
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            
            if message_type == "subscribe_city":
                # El cliente quiere suscribirse a actualizaciones de una ciudad específica
                city_id = data.get("city_id")
                group_name = f"city_{city_id}"
                
                if hasattr(self, 'channel_layer') and self.channel_layer:
                    await self.channel_layer.group_add(
                        group_name,
                        self.channel_name
                    )
                    if group_name not in self.groups:
                        self.groups.append(group_name)
                    print(f"Cliente suscrito a actualizaciones de ciudad {city_id}")
                else:
                    print(f"Channel layer no disponible, pero registrando suscripción a ciudad {city_id}")
            
            elif message_type == "unsubscribe_city":
                # El cliente quiere dejar de recibir actualizaciones de una ciudad
                city_id = data.get("city_id")
                group_name = f"city_{city_id}"
                
                if hasattr(self, 'channel_layer') and self.channel_layer:
                    await self.channel_layer.group_discard(
                        group_name,
                        self.channel_name
                    )
                    if group_name in self.groups:
                        self.groups.remove(group_name)
                    print(f"Cliente desuscrito de actualizaciones de ciudad {city_id}")
        
        except json.JSONDecodeError:
            print("Error decodificando JSON del cliente")
    
    async def site_updated(self, event):
        """Enviar actualización de sitio al cliente"""
        await self.send(text_data=json.dumps({
            "type": "site_updated",
            "site": event["site"],
            "action": event["action"]
        }))

