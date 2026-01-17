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
                    return user.avatar.url
                return "https://res.cloudinary.com/dcf7vcslc/image/upload/v1768654796/v1oczq9mbm66q0jbh64f.jpg"

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

            existing = await sync_to_async(Reaction.objects.filter(message=message, user=user, emoji=emoji).first)()

            if existing:
                await sync_to_async(existing.delete)()
                action = 'removed'
            else:
                existing = await sync_to_async(Reaction.objects.filter)(
                    message=message, user=user
                )
                if await sync_to_async(existing.exists)():
                    reaction = await sync_to_async(existing.first)()
                    if reaction.emoji == emoji:
                        await sync_to_async(reaction.delete)()
                    else:
                        reaction.emoji = emoji
                        await sync_to_async(reaction.save)()
                else:
                    await sync_to_async(Reaction.objects.create)(
                        message=message, user=user, emoji=emoji
                )
                action = 'added'

            def avatar_url(user):
                if user.avatar:
                    return user.avatar.url
                return "https://res.cloudinary.com/dcf7vcslc/image/upload/v1768654796/v1oczq9mbm66q0jbh64f.jpg"

            counts = await sync_to_async(lambda: [
                {
                    'emoji': item['emoji'],
                    'count': item['count'],
                    'users': [
                        {
                            'username': u.user.username,
                            'avatar': avatar_url(u.user)
                        }
                        for u in message.reactions
                            .filter(emoji=item['emoji'])
                            .select_related('user')[:3]
                    ]
                }
                for item in message.reactions
                    .values('emoji')
                    .annotate(count=Count('emoji'))
            ])()


            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'reaction_update',
                'message_id': message_id,
                'emoji': emoji,
                'action': action,
                'counts': counts,
                'user_reacted_emojis': await sync_to_async(lambda: list(Reaction.objects.filter(message=message, user=user).values_list('emoji', flat=True)))()
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