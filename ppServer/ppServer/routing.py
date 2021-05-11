from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chat.routing
import mining.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            *chat.routing.websocket_urlpatterns,
            *mining.routing.websocket_urlpatterns
        ])
    )
})