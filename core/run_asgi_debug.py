#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import the debug ASGI application
from core.asgi_debug import application

print("🚀 Starting DEBUG ASGI server with WebSocket support...")
print("📱 Chat will now work!")
print("🌐 Server running at: http://127.0.0.1:8000")
print("⚡ Real-time features enabled!")
print("🔍 Using simplified ASGI config for debugging")

import uvicorn

uvicorn.run(
    application,
    host="127.0.0.1",
    port=8000,
    ws_ping_interval=20,
    ws_ping_timeout=20,
    log_level="debug"  # Enable debug logging
)
