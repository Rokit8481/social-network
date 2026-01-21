from django.views.generic import View, CreateView, UpdateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from messenger.models import Chat, Message, Reaction
from messenger.forms import MessageForm, GroupForm, ChatForm
from django.db.models import Count
from accounts.helpers.choices.emoji import EMOJI_CHOICES
from django.contrib.auth import get_user_model
from accounts.models import Follow
from django.conf import settings
import json

User = get_user_model()

#Вью для створення чату
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
            
        return redirect('chat', chat_pk=chat.id)
    
# Вью для редагування чату/групи
class ChatEditView(LoginRequiredMixin, UpdateView):
    model = Chat
    pk_url_kwarg = 'chat_pk'
    template_name = 'messenger/chat_edit.html'

    def get_form_class(self):
        if self.object.is_group:
            return GroupForm
        else:
            return ChatForm
    
    def get_success_url(self):
        return reverse_lazy('chat', kwargs={'chat_pk': self.object.id})
    
# Вью для видалення чату/групи без шаблона
class ChatDeleteView(LoginRequiredMixin, View):
    def post(self, request, chat_pk, *args, **kwargs):
        chat = get_object_or_404(Chat, id=chat_pk, users=request.user)
        chat.delete()
        return JsonResponse({'success': True, 'redirect_url': '/messenger/'})

# Вью для редагування повідомлення без шаблона
class MessageEditView(LoginRequiredMixin, View):
    def post(self, request, message_pk, *args, **kwargs):
        message = get_object_or_404(Message, id=message_pk, user=request.user)
        data = json.loads(request.body)
        text = data.get("text")

        if not text.strip():
            return JsonResponse({"success": False, "error": "Порожнє повідомлення"}, status=400)

        message.text = text
        message.save()

        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "text": message.text,
                "created_at": message.created_at.strftime("%H:%M %d/%m/%Y"),
                "updated_at": message.updated_at.strftime("%H:%M %d/%m/%Y"),
            }
        })

# Вью для видалення повідомлення без шаблона
class MessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, message_pk, *args, **kwargs):
        message = get_object_or_404(Message, id=message_pk, user=request.user)
        message.delete()
        return JsonResponse({"success": True})
    
# Вью для редагування повідомлення без шаблона
class MessageUpdateView(LoginRequiredMixin, View):
    def post(self, request, message_pk, *args, **kwargs):
        message = get_object_or_404(Message, id=message_pk, user=request.user)
        data = json.loads(request.body)
        text = data.get("text")

        if not text.strip():
            return JsonResponse({"success": False, "error": "Порожнє повідомлення"}, status=400)

        message.text = text
        message.save()

        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "text": message.text,
                "created_at": message.created_at.strftime("%H:%M %d/%m/%Y"),
                "updated_at": message.updated_at.strftime("%H:%M %d/%m/%Y"),
            }
        })

# Вью для створення групи
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

# Основна сторінка виведення чату
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
                .select_related("user")
                .prefetch_related("reactions")
            )

            user_reaction_map = {
                r.message_id: r.emoji
                for r in Reaction.objects.filter(
                    message__chat=chat,
                    user=request.user
                )
            }
            if chat.is_group == False:
                chat.title = User.objects.exclude(id=request.user.id).filter(chats__id=chat.id).first().username
                chat.save()
                
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

#Вью для відправки повідомлень
class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = MessageForm(json.loads(request.body))
        if form.is_valid():
            chat_id = kwargs.get('chat_id') or json.loads(request.body).get('chat_id')
            chat = get_object_or_404(Chat, id=chat_id)
            message = Message.objects.create(
                chat = chat,
                user = request.user,
                text = form.cleaned_data['text']
            )

            return JsonResponse({
                "id": message.id, 
                "user": message.user.username,
                "text": message.text,
                "created_at": message.created_at.strftime("%H:%M %d/%m/%Y"),
                "updated_at": message.updated_at.strftime("%H:%M %d/%m/%Y"),
            })
        return JsonResponse({'errors': form.errors}, status=400)


#В'ю для реакцій
class AddReactionView(LoginRequiredMixin, View):
    def post(self, request, message_id, *args, **kwargs):
        data = json.loads(request.body)
        emoji = data.get("emoji")

        if not emoji:
            return JsonResponse({"success": False, "error": "Не вказано емодзі"}, status=400)

        message = get_object_or_404(Message, id=message_id)
        user = request.user

        existing_reaction = Reaction.objects.filter(message=message, user=user).first()

        if existing_reaction:
            if existing_reaction.emoji == emoji:
                existing_reaction.delete()
                return JsonResponse({"success": True, "removed": True, "emoji": emoji})
            else:
                existing_reaction.emoji = emoji
                existing_reaction.save()
                return JsonResponse({"success": True, "changed": True, "emoji": emoji})
        else:
            Reaction.objects.create(message=message, user=user, emoji=emoji)
            return JsonResponse({"success": True, "added": True, "emoji": emoji})