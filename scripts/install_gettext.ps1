# Script para instalar gettext en Windows
# Descarga los binarios de gettext y los agrega al PATH

Write-Host "Instalando gettext para Windows..." -ForegroundColor Green

# URL del instalador de gettext para Windows
$gettextUrl = "https://mlocati.github.io/articles/gettext-iconv-windows.html"
$downloadUrl = "https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.21-v1.17/gettext0.21-iconv1.17-shared-64.exe"

# Directorio de instalación
$installDir = "$env:ProgramFiles\gettext"
$tempFile = "$env:TEMP\gettext-installer.exe"

Write-Host "Descargando gettext..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "Descarga completada." -ForegroundColor Green
    
    Write-Host "`nPor favor, ejecuta manualmente el instalador:" -ForegroundColor Yellow
    Write-Host "1. Abre: $tempFile" -ForegroundColor Cyan
    Write-Host "2. Instala en: $installDir" -ForegroundColor Cyan
    Write-Host "3. Asegúrate de agregar '$installDir\bin' al PATH" -ForegroundColor Cyan
    Write-Host "`nO puedes descargarlo manualmente desde:" -ForegroundColor Yellow
    Write-Host $gettextUrl -ForegroundColor Cyan
    
    # Intentar abrir el instalador
    Start-Process $tempFile
} catch {
    Write-Host "Error al descargar. Por favor, descarga manualmente desde:" -ForegroundColor Red
    Write-Host "https://mlocati.github.io/articles/gettext-iconv-windows.html" -ForegroundColor Cyan
    Write-Host "`nO usa winget si está disponible:" -ForegroundColor Yellow
    Write-Host "winget install --id=GnuWin32.GetText" -ForegroundColor Cyan
}

