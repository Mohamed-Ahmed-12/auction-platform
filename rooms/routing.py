from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/place-bid/<int:item_id>/", consumers.BidConsumer.as_asgi()),
]