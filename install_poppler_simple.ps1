# Poppler Installation Script
Write-Host "Installing Poppler for Student Buddy OCR..." -ForegroundColor Cyan

$installDir = "C:\Program Files\poppler"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force
}

Write-Host "Downloading Poppler..." -ForegroundColor Yellow
$zipUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.07.0-0/Release-23.07.0-0.zip"
$zipPath = "$env:TEMP\poppler.zip"

try {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    Write-Host "Download completed" -ForegroundColor Green
} catch {
    Write-Host "Download failed. Please download manually." -ForegroundColor Red
    exit 1
}

Write-Host "Extracting Poppler..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
    Write-Host "Extraction completed" -ForegroundColor Green
} catch {
    Write-Host "Extraction failed" -ForegroundColor Red
    exit 1
}

$binPath = "$installDir\poppler-23.07.0\Library\bin"
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

Remove-Item $zipPath -Force
Write-Host "Installation completed! Restart your terminal." -ForegroundColor Green
