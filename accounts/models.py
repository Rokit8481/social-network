from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(AbstractUser):
    bio = models.CharField(max_length=200, blank=True, null=True, verbose_name='Bio', default='Bio is not set.')
    avatar = CloudinaryField('avatar', blank=True, null=True)
    mobile = PhoneNumberField(blank=True, null=True, verbose_name='Mobile Number', default='No mobile number.')
    slug = AutoSlugField(populate_from='username', unique=True, verbose_name='Slug')
    birthday = models.DateField(blank=True, null=True, verbose_name='Birthday')

    def __str__(self):
        return self.username
    
    def delete(self, *args, **kwargs):
        if self.avatar and self.avatar.public_id != 'default/default_avatar':
            self.avatar.delete(save=False)
        super().delete(*args, **kwargs)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return 'https://res.cloudinary.com/dcf7vcslc/image/upload/v1768654796/v1oczq9mbm66q0jbh64f.jpg'

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
