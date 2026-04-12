import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count
from django.conf import settings

from messenger.models import Chat, Message, Reaction


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = int(self.scope['url_route']['kwargs']['chat_id'])
        self.room_group_name = f"chat_{self.chat_id}"
        user = self.scope["user"]

        if isinstance(user, AnonymousUser):
            await self.close()
            return

        is_member = await sync_to_async(
            Chat.objects.filter(id=self.chat_id, users=user).exists
        )()
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") == "chat_message":
            await self.handle_chat_message(data, user)

        elif data.get("type") == "reaction_update":
            await self.handle_reaction_update(data, user)

        elif data.get("type") == "delete_message":
            await self.handle_delete_message(data, user)

        elif data.get("type") == "update_message":
            await self.handle_update_message(data, user)

    async def handle_chat_message(self, data, user):
        is_member = await sync_to_async(
            Chat.objects.filter(id=self.chat_id, users=user).exists
        )()
        if not is_member:
            return

        text = data.get("text", "").strip()
        if not text:
            return

        reply_on = None
        reply_on_id = data.get("reply_on")
        if reply_on_id:
            try:
                reply_on = await sync_to_async(Message.objects.select_related("user").get)(
                    id=reply_on_id, chat_id=self.chat_id
                )
            except Message.DoesNotExist:
                reply_on = None

        chat = await sync_to_async(Chat.objects.get)(id=self.chat_id)

        message = await sync_to_async(Message.objects.create)(
            chat=chat,
            user=user,
            text=text,
            reply_on=reply_on,
        )

        message = await self._get_message_with_related(message.pk)

        event = await self._build_message_event(message, user)
        await self.channel_layer.group_send(self.room_group_name, event)

    async def handle_reaction_update(self, data, user):
        is_member = await sync_to_async(
            Chat.objects.filter(id=self.chat_id, users=user).exists
        )()
        if not is_member:
            return

        message_id = data.get("message_id")
        emoji = data.get("emoji")
        if message_id is None or emoji is None:
            return

        try:
            message = await sync_to_async(Message.objects.get)(
                id=message_id, chat_id=self.chat_id
            )
        except Message.DoesNotExist:
            return

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
                message=message, user=user, emoji=emoji
            )

        reactions = await self._get_reactions_for_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "reaction_update",
                "message_id": message_id,
                "reactions": reactions,
            },
        )

    async def handle_delete_message(self, data, user):
        message_id = data.get("message_id")
        if message_id is None:
            return

        message = await sync_to_async(
            Message.objects.filter(
                id=message_id, user=user, chat_id=self.chat_id
            ).first
        )()

        if not message:
            return

        await sync_to_async(message.delete)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "message_deleted", "message_id": message_id},
        )

    async def handle_update_message(self, data, user):
        message_id = data.get("message_id")
        if message_id is None:
            return

        new_text = data.get("text", "").strip()

        message = await sync_to_async(
            Message.objects.filter(
                id=message_id, user=user, chat_id=self.chat_id
            ).first
        )()
        if not message:
            return

        if not new_text or new_text == message.text:
            return

        message.text = new_text
        await sync_to_async(message.save)()

        message = await self._get_message_with_related(message.pk)

        event = await self._build_message_event(message, user, event_type="update_message")
        await self.channel_layer.group_send(self.room_group_name, event)

    async def _get_message_with_related(self, pk):
        return await sync_to_async(
            Message.objects.select_related("user", "reply_on", "reply_on__user").get
        )(pk=pk, chat_id=self.chat_id)

    async def _get_reactions_for_message(self, message):
        def inner():
            return [
                {
                    "emoji": r["emoji"],
                    "count": r["count"],
                    "users": [
                        {
                            "username": u.user.username,
                            "avatar": self._get_avatar_url(u.user.avatar),
                        }
                        for u in Reaction.objects.filter(
                            message=message, emoji=r["emoji"]
                        ).select_related("user")
                    ],
                }
                for r in Reaction.objects.filter(message=message)
                .values("emoji")
                .annotate(count=Count("emoji"))
            ]

        return await sync_to_async(inner)()

    def _get_avatar_url(self, avatar):
        if avatar:
            return settings.MEDIA_URL + avatar.name
        return settings.MEDIA_URL + "default/default_avatar.png"

    async def _build_message_event(self, message, user, event_type="chat_message"):
        reply_on_id = message.reply_on_id
        reply_on_user = None
        reply_on_text = None

        if message.reply_on:
            reply_on_user = message.reply_on.user.username
            txt = message.reply_on.text or ""
            reply_on_text = (txt[:30] + "...") if len(txt) > 30 else txt

        return {
            "type": event_type,
            "id": message.id,
            "user": user.username,
            "user_slug": user.slug,
            "avatar": self._get_avatar_url(user.avatar),
            "text": message.text,
            "reply_on_id": reply_on_id,
            "reply_on_user": reply_on_user,
            "reply_on_text": reply_on_text,
            "created_time": message.created_at.strftime("%H:%M"),
            "created_date": message.created_at.date().isoformat(),
            "updated_time": message.updated_at.strftime("%H:%M %d/%m/%Y"),
            "is_own": False,
        }

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def reaction_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def update_message(self, event):
        await self.send(text_data=json.dumps(event))
