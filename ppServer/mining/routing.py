from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/mining/game/(?P<region_id>\d+)/$', consumers.MiningGameConsumer.as_asgi())
]