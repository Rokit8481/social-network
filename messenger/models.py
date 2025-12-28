from django.db import models
from accounts.choices.emoji import EMOJI_CHOICES
from django.contrib.auth import get_user_model
from accounts.models import BaseModel

User = get_user_model()

class Chat(BaseModel):
    users = models.ManyToManyField(User, related_name='chats', blank=False)
    background = models.ImageField(upload_to='backgrounds/', null=True, blank=True, default='default/default_bg.png', verbose_name = 'Background')
    is_group = models.BooleanField(default=False, verbose_name = 'Is group chat')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name = 'Title')

    def save(self, *args, **kwargs):
        if not self.background:
            self.background = 'default/default_bg.png'
        super().save(*args, **kwargs)
        if not self.is_group and self.users.count() > 2:
            raise ValueError("Privately chats cannot have more than 2 users.")
            
    def __str__(self):
        return self.title or f"Chat between {' and '.join(user.username for user in self.users.all())}"
    
    def delete(self, *args, **kwargs):
        if self.background and self.background.name != 'default/default_bg.png':
            self.background.delete(save=False)

        super().delete(*args, **kwargs)

    class Meta: 
        ordering = ["created_at"]
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'

class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', null=False)
    text = models.TextField(null=True, blank=True, verbose_name = 'Text')

    def __str__(self):
        return f"{self.user}: {self.text[:30] if self.text else '[файл]'}"
    
    def was_edited(self):
        if (self.updated_at - self.created_at).total_seconds() > 1:
            return True
        return False

    class Meta: 
        ordering = ["created_at"]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

class Reaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions', null=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES, verbose_name = 'Emoji')

    def __str__(self):
        return f"{self.emoji} --- {self.message}"
    
    class Meta: 
        unique_together = ("message", "user")
        ordering = ["created_at"]
        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'

