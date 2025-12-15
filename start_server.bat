@echo off
echo Iniciando servidor Django con soporte para WebSockets...
echo.
echo NOTA: Para que WebSockets funcionen, el servidor debe usar ASGI.
echo Django runserver detecta automaticamente ASGI cuando Channels esta instalado.
echo.
python manage.py runserver
pause
















