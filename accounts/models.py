from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(AbstractUser):
    bio = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bio', default='Bio is not set.')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar', default='default/default_avatar.png')
    mobile = PhoneNumberField(blank=True, null=True, verbose_name='Mobile Number', default='No mobile number.')
    slug = AutoSlugField(populate_from='username', unique=True, verbose_name='Slug')
    birthday = models.DateField(blank=True, null=True, verbose_name='Birthday')

    def __str__(self):
        return self.username
    
    def delete(self, *args, **kwargs):
        if self.avatar and self.avatar.name != 'default/default_avatar.png':
            self.avatar.delete(save=False)

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['username']

class Follow(BaseModel):
    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='following', verbose_name='Follower')
    following = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='followers', verbose_name='Following')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} → {self.following}"
