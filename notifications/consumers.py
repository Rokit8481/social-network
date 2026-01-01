import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from notifications.models import Notification
from channels.db import database_sync_to_async

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

        unread_count = await self.get_unread_count()

        await self.send(text_data=json.dumps({
            "notification": {
                "id": notification.id,
                "message": message,
                "event_type": notification.event_type,
                "created": notification.created_at.strftime("%H:%M %d/%m/%Y"),
                "is_read": False,
            },
            "unread_count": unread_count
        }))

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(
            to_user=self.user,
            is_read=False
        ).count()
