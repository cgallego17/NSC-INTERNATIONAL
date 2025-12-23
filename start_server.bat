@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Iniciando servidor Django...
echo.
python manage.py runserver
pause



















