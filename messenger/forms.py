from django import forms 
from .models import Message, Chat

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': "Напишіть повідомлення...",
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
                'placeholder': "Напишіть назву цього чату",
                'class': 'form-control',
            }),
            'background': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        title = forms.CharField(required=True)

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['background']
        widgets = {
            'background': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
