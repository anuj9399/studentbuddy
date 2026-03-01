# Poppler Installation Script for Student Buddy
# This script downloads and installs Poppler for OCR functionality

Write-Host "🔧 Installing Poppler for Student Buddy OCR..." -ForegroundColor Cyan

# Create installation directory
$installDir = "C:\Program Files\poppler"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force
}

# Download Poppler
Write-Host "📥 Downloading Poppler..." -ForegroundColor Yellow
$zipUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.07.0-0/Release-23.07.0-0.zip"
$zipPath = "$env:TEMP\poppler.zip"

try {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    Write-Host "✅ Download completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Download failed. Please download manually from: https://github.com/oschwartz10612/poppler-windows/releases" -ForegroundColor Red
    exit 1
}

# Extract
Write-Host "📂 Extracting Poppler..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
    Write-Host "✅ Extraction completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Extraction failed" -ForegroundColor Red
    exit 1
}

# Add to PATH (current session only)
$binPath = "$installDir\poppler-23.07.0\Library\bin"
$env:PATH += ";$binPath"

# Add to permanent PATH
try {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$binPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$binPath", "User")
        Write-Host "✅ Added to PATH permanently" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Could not add to PATH permanently. Please add manually: $binPath" -ForegroundColor Yellow
}

# Cleanup
Remove-Item $zipPath -Force

Write-Host "🎉 Poppler installation completed!" -ForegroundColor Green
Write-Host "📝 Please restart your terminal and Django server for changes to take effect." -ForegroundColor Cyan
Write-Host "🔍 Test with: pdftotext -v" -ForegroundColor Yellow
