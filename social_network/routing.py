from messenger.routing import websocket_urlpatterns as messenger_ws
from notifications.routing import get_notifications_ws_patterns

websocket_urlpatterns = messenger_ws + get_notifications_ws_patterns()