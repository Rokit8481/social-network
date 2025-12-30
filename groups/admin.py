from django.contrib import admin
from .models import Group, GroupMessage, Tag

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'slug', 'created_at')
    search_fields = ('title', 'creator__username', 'slug')
    list_filter = ('created_at',)
    readonly_fields = ('slug',)
    filter_horizontal = ('tags',) 
    
@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'slug', 'created_at')
    search_fields = ('content', 'sender__username', 'slug', 'group__title')
    list_filter = ('created_at', 'group')
    readonly_fields = ('slug',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
