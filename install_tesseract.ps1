# Tesseract OCR Installation Script for Student Buddy
Write-Host "Installing Tesseract OCR for Student Buddy..." -ForegroundColor Cyan

# Create installation directory
$installDir = "C:\Program Files\Tesseract-OCR"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force
}

# Try multiple download sources
$sources = @(
    "https://github.com/UB-Mannheim/tesseract/wiki/releases/download/5.4.0/tesseract-ocr-w64-setup-5.4.0.20240606.exe",
    "https://github.com/UB-Mannheim/tesseract/releases/download/5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe",
    "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
)

$installerPath = "$env:TEMP\tesseract-installer.exe"
$downloaded = $false

foreach ($source in $sources) {
    try {
        Write-Host "Trying to download from: $source" -ForegroundColor Yellow
        Invoke-WebRequest -Uri $source -OutFile $installerPath -TimeoutSec 30
        if (Test-Path $installerPath) {
            $downloaded = $true
            Write-Host "Download successful!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Download failed from this source, trying next..." -ForegroundColor Yellow
        continue
    }
}

if (-not $downloaded) {
    Write-Host "All download sources failed. Please install manually." -ForegroundColor Red
    Write-Host "1. Visit: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host "2. Download: tesseract-ocr-w64-setup-5.4.0.20240606.exe" -ForegroundColor Cyan
    Write-Host "3. Install to: C:\Program Files\Tesseract-OCR" -ForegroundColor Cyan
    exit 1
}

# Silent install
Write-Host "Installing Tesseract..." -ForegroundColor Yellow
try {
    Start-Process -FilePath $installerPath -ArgumentList "/S", "/D=$installDir" -Wait
    Write-Host "Installation completed!" -ForegroundColor Green
} catch {
    Write-Host "Installation failed. Please run the installer manually." -ForegroundColor Red
    Write-Host "Installer located at: $installerPath" -ForegroundColor Yellow
}

# Add to PATH
$binPath = "$installDir"
$env:PATH += ";$binPath"

try {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$binPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$binPath", "User")
        Write-Host "Added to PATH permanently" -ForegroundColor Green
    }
} catch {
    Write-Host "Please add to PATH manually: $binPath" -ForegroundColor Yellow
}

# Cleanup
Remove-Item $installerPath -Force

Write-Host "Tesseract installation completed!" -ForegroundColor Green
Write-Host "Restart your terminal and Django server for changes to take effect." -ForegroundColor Cyan

# Test installation
try {
    $tesseractVersion = & "$binPath\tesseract.exe" --version
    Write-Host "Tesseract version: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "Please restart terminal to test Tesseract" -ForegroundColor Yellow
}
