"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()  # Required when using custom middleware before get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from Apps.message_app.routing import websocket_urlpatterns 
from project.jwt_auth_middlewear import JWTAuthMiddleware
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": JWTAuthMiddleware(
    #      AuthMiddlewareStack(
    #         URLRouter(websocket_urlpatterns)
    #     )
    # )
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})

print("✅ ASGI application is loaded")
