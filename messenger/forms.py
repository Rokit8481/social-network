from django import forms 
from messenger.models import Message, Chat
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': "Write down message...",
                'class': 'form-control',
                'id': 'message-input'
            })
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['users', 'background', 'title']
        widgets = {
            'users': forms.SelectMultiple(attrs={
                'class': 'form-select',
            }),
            'title': forms.TextInput(attrs={
                'placeholder': "Write down group title...",
                'class': 'form-control',
            }),
            'background': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        # Витягуємо поточного користувача
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            friends_qs = User.objects.filter(id__in=[u.id for u in user.get_friends()])
            self.fields['users'].queryset = friends_qs

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['background']
        widgets = {
            'background': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
