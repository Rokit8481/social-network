from django.db import models
from accounts.helpers.choices.emoji import EMOJI_CHOICES
from django.contrib.auth import get_user_model
from accounts.models import BaseModel
from cloudinary.models import CloudinaryField
from cloudinary import uploader

User = get_user_model()

class Chat(BaseModel):
    users = models.ManyToManyField(User, related_name='chats', blank=False)
    background = CloudinaryField(
        'background',
        blank=True,
        null=True,
    )
    is_group = models.BooleanField(default=False, verbose_name = 'Is group chat')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name = 'Title')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.is_group and self.users.count() > 2:
            raise ValueError("Privately chats cannot have more than 2 users.")
    
    def get_background_url(self):
        if self.background and getattr(self.background, 'public_id', None) != 'default/default_bg':
            return self.background.url
        return 'https://res.cloudinary.com/dcf7vcslc/image/upload/v1768654798/xoz3mmnu8m0qq8ktpxn6.webp'
            
    def has_custom_background(self):
        return self.background and getattr(self.background, 'public_id', None) != 'default/default_bg'
    
    def __str__(self):
        return self.title or f"Chat between {' and '.join(user.username for user in self.users.all())}"
    
    def delete(self, *args, **kwargs):
        if self.background and getattr(self.background, 'public_id', None) != 'default/default_bg':
            try:
                uploader.destroy(self.background.public_id)
            except Exception as e:
                print(f"Error deleting Cloudinary file: {e}")
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

