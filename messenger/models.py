from django.db import models
from .choices.emoji import EMOJI_CHOICES
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Chat(BaseModel):
    users = models.ManyToManyField(User, related_name='chats', blank=False)
    background = models.ImageField(upload_to='backgrounds/', null=True, blank=True, default='default/default_bg.png', verbose_name = 'Фон')
    is_group = models.BooleanField(default=False, verbose_name = 'Група')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name = 'Назва')

    def save(self, *args, **kwargs):
        if not self.background:
            self.background = 'default/default_bg.png'
        super().save(*args, **kwargs)
        if not self.is_group and self.users.count() > 2:
            raise ValueError("Приватний чат може мати лише двох користувачів")
            
    def __str__(self):
        return self.title or f"Чат між {' та '.join(user.username for user in self.users.all())}"
    
    class Meta: 
        ordering = ["created_at"]
        verbose_name = 'Чат'
        verbose_name_plural = 'Чати'

class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', null=False)
    text = models.TextField(null=True, blank=True, verbose_name = 'Текст')

    def __str__(self):
        return f"{self.user}: {self.text[:30] if self.text else '[файл]'}"

    class Meta: 
        ordering = ["created_at"]
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'

class Reaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions', null=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES, verbose_name = 'Емодзі')

    def __str__(self):
        return f"{self.emoji} --- {self.message}"
    
    class Meta: 
        unique_together = ("message", "user")
        ordering = ["created_at"]
        verbose_name = 'Реакція'
        verbose_name_plural = 'Реакції'

