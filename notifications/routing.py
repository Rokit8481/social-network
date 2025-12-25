from django.urls import re_path

def get_notifications_ws_patterns():
    from notifications.consumers import NotificationConsumer
    return [
        re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    ]