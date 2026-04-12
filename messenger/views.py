from django.views.generic import View, CreateView, UpdateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from messenger.models import Chat, Message, Reaction
from messenger.forms import MessageForm, GroupForm, ChatForm
from accounts.helpers.choices.emoji import EMOJI_CHOICES
from django.contrib.auth import get_user_model
from django.conf import settings
import json

User = get_user_model()


class CreateChatView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        other_user_id = request.POST.get('user_id')

        if not other_user_id:
            return JsonResponse({'error': 'Не вказано користувача'}, status=400)

        other_user = get_object_or_404(User, id=other_user_id)

        chat = Chat.objects.filter(is_group=False, users=current_user).filter(users=other_user).first()

        if not chat:
            chat = Chat.objects.create(is_group=False)
            chat.users.add(current_user, other_user)

            chat.title = other_user.username
            chat.save()

        redirect_url = reverse('chat', kwargs={'chat_pk': chat.id})
        if request.accepts('application/json'):
            return JsonResponse({
                'redirect_url': redirect_url,
                'chat_id': chat.id,
            })
        return redirect('chat', chat_pk=chat.id)


class ChatEditView(LoginRequiredMixin, UpdateView):
    model = Chat
    pk_url_kwarg = 'chat_pk'
    template_name = 'messenger/chat_edit.html'

    def get_queryset(self):
        return Chat.objects.filter(users=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.is_group:
            kwargs['user'] = self.request.user
        return kwargs

    def get_form_class(self):
        if self.object.is_group:
            return GroupForm
        return ChatForm

    def get_success_url(self):
        return reverse_lazy('chat', kwargs={'chat_pk': self.object.id})


class ChatDeleteView(LoginRequiredMixin, View):
    def post(self, request, chat_pk, *args, **kwargs):
        chat = get_object_or_404(Chat, id=chat_pk, users=request.user)
        chat.delete()
        return JsonResponse({'success': True, 'redirect_url': '/messenger/'})


class MessageEditView(LoginRequiredMixin, View):
    def post(self, request, message_pk, *args, **kwargs):
        message = get_object_or_404(Message, id=message_pk, user=request.user)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Некоректний JSON"},
                status=400,
            )
        text = data.get("text")
        if text is None or not str(text).strip():
            return JsonResponse({"success": False, "error": "Порожнє повідомлення"}, status=400)

        message.text = text
        message.save()

        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "text": message.text,
                "reply_to": message.reply_on.id if message.reply_on else None,
                "created_at": message.created_at.strftime("%H:%M %d/%m/%Y"),
                "updated_at": message.updated_at.strftime("%H:%M %d/%m/%Y"),
            }
        })


class MessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, message_pk, *args, **kwargs):
        message = get_object_or_404(Message, id=message_pk, user=request.user)
        message.delete()
        return JsonResponse({"success": True})


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = Chat
    form_class = GroupForm
    template_name = 'messenger/create_group.html'
    success_url = reverse_lazy('messenger_main')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.is_group = True
        response = super().form_valid(form)
        self.object.users.add(self.request.user)

        users = self.object.users.all()
        title = self.object.title.strip() if self.object.title else ""

        if not title:
            if users.count() >= 4:
                title = "Group without title"
            else:
                user_names = users.values_list('username', flat=True)
                title = " and ".join(user_names)

        self.object.title = title
        self.object.save()

        return redirect('chat', chat_pk=self.object.pk)


class ChatView(LoginRequiredMixin, View):
    template_name = 'messenger/chat.html'

    def get(self, request, chat_pk=None, *args, **kwargs):
        chat = None
        if chat_pk:
            chat = get_object_or_404(Chat, id=chat_pk, users=request.user)
        else:
            chat = ''

        messages = []
        user_reaction_map = {}

        if chat:
            messages = (
                chat.messages.all()
                .select_related("user", "reply_on", "reply_on__user")
                .prefetch_related("reactions")
            )

            user_reaction_map = {
                r.message_id: r.emoji
                for r in Reaction.objects.filter(
                    message__chat=chat,
                    user=request.user
                )
            }
            if not chat.is_group:
                other = User.objects.exclude(id=request.user.id).filter(chats__id=chat.id).first()
                chat.display_title = other.username if other else (chat.title or '')
            else:
                chat.display_title = chat.title or ''

            for msg in messages:
                reactions_by_emoji = {}
                for reaction in msg.reactions.select_related('user'):
                    if reaction.emoji not in reactions_by_emoji:
                        reactions_by_emoji[reaction.emoji] = {'count': 0, 'users': []}
                    reactions_by_emoji[reaction.emoji]['count'] += 1
                    reactions_by_emoji[reaction.emoji]['users'].append(reaction.user)
                msg.reactions_by_emoji = reactions_by_emoji
                msg.user_reacted_emoji = user_reaction_map.get(msg.id)

        default_background = Chat._meta.get_field('background').default

        user_friends = User.objects.filter(id__in=[u.id for u in request.user.get_friends()])

        context = {
            "chat": chat,
            "messages": messages,
            "chats": Chat.objects.filter(users=request.user),
            "form": MessageForm(),
            "emoji_choices": EMOJI_CHOICES,
            "user_friends": user_friends,
            "default_background": settings.MEDIA_URL + default_background,
        }

        return render(request, self.template_name, context)


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Invalid JSON'}, status=400)

        form = MessageForm(payload)
        chat_id = kwargs.get('chat_id') or payload.get('chat_id')
        if chat_id is None:
            return JsonResponse({'errors': {'chat_id': ['Required.']}}, status=400)

        chat = get_object_or_404(Chat, id=chat_id, users=request.user)

        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=400)

        message = Message.objects.create(
            chat=chat,
            user=request.user,
            text=form.cleaned_data['text'],
            reply_on=form.cleaned_data.get('reply_to'),
        )

        return JsonResponse({
            "id": message.id,
            "user": message.user.username,
            "text": message.text,
            "reply_to": message.reply_on.id if message.reply_on else None,
            "created_at": message.created_at.strftime("%H:%M %d/%m/%Y"),
            "updated_at": message.updated_at.strftime("%H:%M %d/%m/%Y"),
        })


class AddReactionView(LoginRequiredMixin, View):
    def post(self, request, message_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Некоректний JSON"},
                status=400,
            )
        emoji = data.get("emoji")

        if not emoji:
            return JsonResponse({"success": False, "error": "Не вказано емодзі"}, status=400)

        message = get_object_or_404(
            Message.objects.select_related('chat'),
            id=message_id,
            chat__users=request.user,
        )
        user = request.user

        existing_reaction = Reaction.objects.filter(message=message, user=user).first()

        if existing_reaction:
            if existing_reaction.emoji == emoji:
                existing_reaction.delete()
                return JsonResponse({"success": True, "removed": True, "emoji": emoji})
            existing_reaction.emoji = emoji
            existing_reaction.save()
            return JsonResponse({"success": True, "changed": True, "emoji": emoji})

        Reaction.objects.create(message=message, user=user, emoji=emoji)
        return JsonResponse({"success": True, "added": True, "emoji": emoji})
