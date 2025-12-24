# Script para compilar traducciones de NSC International
# Compila solo los archivos de traducción del proyecto (no los de Django)

Write-Host "Compilando traducciones..." -ForegroundColor Green

# Intentar usar la versión moderna primero, luego la antigua como fallback
$gettextPath = "C:\Program Files\gettext-iconv\bin\msgfmt.exe"
if (-not (Test-Path $gettextPath)) {
    $gettextPath = "C:\Program Files (x86)\GnuWin32\bin\msgfmt.exe"
}

if (-not (Test-Path $gettextPath)) {
    Write-Host "Error: gettext no encontrado" -ForegroundColor Red
    Write-Host "Por favor, instala gettext usando: winget install --id=MicheleLocati.GettextIconv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Usando gettext en: $gettextPath" -ForegroundColor Cyan

# Compilar inglés
Write-Host "Compilando traducciones en inglés..." -ForegroundColor Yellow
& $gettextPath "locale\en\LC_MESSAGES\django.po" -o "locale\en\LC_MESSAGES\django.mo"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Traducciones en inglés compiladas correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ Error al compilar traducciones en inglés" -ForegroundColor Red
    exit 1
}

# Compilar español
Write-Host "Compilando traducciones en español..." -ForegroundColor Yellow
& $gettextPath "locale\es\LC_MESSAGES\django.po" -o "locale\es\LC_MESSAGES\django.mo"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Traducciones en español compiladas correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ Error al compilar traducciones en español" -ForegroundColor Red
    exit 1
}

Write-Host "`n¡Todas las traducciones compiladas exitosamente!" -ForegroundColor Green

