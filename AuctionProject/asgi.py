"""
ASGI config for AuctionProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from rooms.routing import websocket_urlpatterns
from authen.middleware.token_auth import TokenAuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuctionProject.settings')

# Get the basic Django HTTP application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)