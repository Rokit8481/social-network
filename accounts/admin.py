from django.contrib import admin
from .models import UserProfile, Follow

admin.site.register(Follow)
admin.site.register(UserProfile)