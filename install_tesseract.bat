@echo off
echo Installing Tesseract OCR for Student Buddy...
echo.

echo Opening download page in your browser...
start https://github.com/UB-Mannheim/tesseract/wiki

echo.
echo Instructions:
echo 1. Download: tesseract-ocr-w64-setup-5.4.0.20240606.exe
echo 2. Run the installer
echo 3. Choose installation path: C:\Program Files\Tesseract-OCR
echo 4. Check "Add Tesseract to PATH" during installation
echo 5. Restart this command prompt and Django server
echo.

echo Press any key to continue when installation is complete...
pause > nul

echo Testing Tesseract installation...
tesseract --version

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Tesseract is installed and working.
    echo You can now try uploading your PDF again.
) else (
    echo.
    echo Tesseract not found in PATH.
    echo Please add C:\Program Files\Tesseract-OCR to your system PATH.
)

echo.
pause
