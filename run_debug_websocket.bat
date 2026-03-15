@echo off
echo 🔍 Starting DEBUG ASGI Server for WebSocket Issues...
echo 📱 This will show detailed connection logs
echo 🌐 Server: http://127.0.0.1:8000
echo ⚡ Press Ctrl+C to stop server
echo.

REM Change to core directory and run debug ASGI server
cd /d "d:\projects\studentbuddy\core"
"d:\projects\studentbuddy\source\Scripts\python.exe" run_asgi_debug.py

pause
