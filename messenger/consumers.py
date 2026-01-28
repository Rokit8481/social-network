from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.db.models import Count
from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']

        if data['type'] == 'chat_message':
            text = data['text']
            if not text.strip():
                return

            from .models import Chat, Message
            chat = await sync_to_async(Chat.objects.select_related().get)(id=self.chat_id)
            message = await sync_to_async(Message.objects.create)(
                chat=chat, user=user, text=text
            )

            def get_avatar_url(user):
                if user.avatar:
                    return settings.MEDIA_URL + user.avatar.name
                return settings.MEDIA_URL + 'default/default_avatar.png'


            event = {
                'type': 'chat_message',
                'id': message.id,
                'user': user.username,
                'user_slug': user.slug,
                'avatar': get_avatar_url(user),
                'text': message.text,
                "created_time": message.created_at.strftime("%H:%M"),
                "created_date": message.created_at.date().isoformat(),
                'updated_time': message.updated_at.strftime("%H:%M %d/%m/%Y"),
            }

            await self.channel_layer.group_send(self.room_group_name, event)

        elif data['type'] == 'reaction_update':
            from .models import Message, Reaction

            message_id = data['message_id']
            emoji = data['emoji']

            message = await sync_to_async(Message.objects.get)(id=message_id)

            existing = await sync_to_async(
                Reaction.objects.filter(message=message, user=user).first
            )()

            if existing:
                if existing.emoji == emoji:
                    await sync_to_async(existing.delete)()
                else:
                    existing.emoji = emoji
                    await sync_to_async(existing.save)()
            else:
                await sync_to_async(Reaction.objects.create)(
                    message=message,
                    user=user,
                    emoji=emoji
                )

            def avatar_url(avatar):
                if avatar:
                    return settings.MEDIA_URL + avatar.name
                return settings.MEDIA_URL + 'default/default_avatar.png'

            reactions = await sync_to_async(lambda: [
                {
                    "emoji": r["emoji"],
                    "count": r["count"],
                    "users": [
                        {
                            "username": u.user.username,
                            "avatar": avatar_url(u.user.avatar)
                        }
                        for u in Reaction.objects.filter(
                            message=message,
                            emoji=r["emoji"]
                        ).select_related("user")
                    ],
                }
                for r in Reaction.objects
                    .filter(message=message)
                    .values("emoji")
                    .annotate(count=Count("emoji"))
            ])()

            await self.channel_layer.group_send(self.room_group_name, {
                "type": "reaction_update",
                "message_id": message_id,
                "reactions": reactions
            })

        elif data['type'] == 'delete_message':
            from .models import Message

            message_id = data['message_id']
            message = await sync_to_async(Message.objects.filter(id=message_id, user=user).first)()

            if not message:
                return

            await sync_to_async(message.delete)()

            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'message_deleted',
                'message_id': message_id
            })

        elif data['type'] == "update_message":
            from .models import Message

            message_id = data['message_id']
            new_text = data['text'].strip()
            if not new_text:
                return

            message = await sync_to_async(Message.objects.filter(id=message_id, user=user).first)()
            if not message:
                return

            old_text = message.text
            if old_text == new_text:
                return

            message.text = new_text
            await sync_to_async(message.save)()

            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'update_message',
                'id': message.id,
                'user': user.username,
                'text': message.text,
                'created_time': message.created_at.strftime("%H:%M %d/%m/%Y"),
                'updated_time': message.updated_at.strftime("%H:%M %d/%m/%Y"),
                'is_own': False,
            })


    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def reaction_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))
        
    async def update_message(self, event):
        await self.send(text_data=json.dumps(event))