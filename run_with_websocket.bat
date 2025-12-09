@echo off
echo ========================================
echo Iniciando servidor Django con WebSocket
echo ========================================
echo.
echo Este script usa Daphne para soportar WebSockets
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
daphne -b 127.0.0.1 -p 8000 nsc_admin.asgi:application











