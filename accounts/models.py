from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(AbstractUser):
    bio = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bio')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    mobile = PhoneNumberField(unique=True, blank=True, null=True, verbose_name='Mobile Number')
    birthday = models.DateField(blank=True, null=True, verbose_name='Birthday')

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['username']