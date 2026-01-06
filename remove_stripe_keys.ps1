# Script to remove Stripe keys from settings.py
param(
    [string]$FilePath = "nsc_admin/settings.py"
)

if (Test-Path $FilePath) {
    $content = Get-Content $FilePath -Raw
    $originalContent = $content

    # Replace hardcoded Stripe secret keys
    $content = $content -replace 'sk_live_[^",\s]+', '""'
    $content = $content -replace 'pk_live_[^",\s]+', '""'

    if ($content -ne $originalContent) {
        $content | Set-Content $FilePath -NoNewline
        Write-Host "Removed Stripe keys from $FilePath"
    }
}

