#!/usr/bin/env python
"""
Script de prueba para verificar que WebSocket funciona
Ejecutar: python test_websocket.py
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws/sites/"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conexión WebSocket exitosa!")
            
            # Enviar mensaje de suscripción
            message = {
                "type": "subscribe_city",
                "city_id": 1
            }
            await websocket.send(json.dumps(message))
            print("✅ Mensaje de suscripción enviado")
            
            # Esperar respuesta
            response = await websocket.recv()
            print(f"✅ Respuesta recibida: {response}")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Error de conexión: {e}")
        print("   Asegúrate de que el servidor Django esté corriendo con ASGI")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Probando conexión WebSocket...")
    print("Asegúrate de que el servidor Django esté corriendo en http://127.0.0.1:8000")
    asyncio.run(test_websocket())















