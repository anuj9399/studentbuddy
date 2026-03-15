@echo off
echo 🚀 Starting StudentBuddy with WebSocket Support...
echo 📱 Study Groups Chat will work in real-time!
echo 🌐 Server: http://127.0.0.1:8000
echo ⚡ Press Ctrl+C to stop server
echo.

REM Use the same Python path that works for Django
"d:\projects\studentbuddy\source\Scripts\python.exe" run_asgi.py

pause
