"""
Debug ASGI config for core project - Simplified version
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import groups.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Simplified ASGI config without AllowedHostsOriginValidator for debugging
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            groups.routing.websocket_urlpatterns
        )
    ),
})
