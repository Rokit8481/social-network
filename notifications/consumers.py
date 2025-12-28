import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from .models import Notification 

        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            await self.close()
            return

        self.user = user
        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        from .models import Notification  

        notification_id = event["notification_id"]

        notification = await Notification.objects.aget(pk=notification_id)
        message = await notification.async_get_message()

        await self.send(text_data=json.dumps({
            "id": notification.id,
            "message": message,
            "event_type": notification.event_type,
            "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M"),
        }))
