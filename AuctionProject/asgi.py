"""
ASGI config for AuctionProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# 1. Set env variable to load settings file of the project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuctionProject.settings')

# 2. Get the basic Django HTTP application
django_asgi_app = get_asgi_application()

# 3. Import any apps after initializing django asgi app
from rooms.routing import websocket_urlpatterns as bid_url
from notificationapp.routing import websocket_urlpatterns as notification_url
from authen.middleware.token_auth import TokenAuthMiddlewareStack


ws_urls = bid_url + notification_url


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddlewareStack(
                URLRouter(ws_urls)
            )
        ),
    }
)