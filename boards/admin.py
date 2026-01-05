from django.contrib import admin
from .models import Board, BoardMessage, Tag

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'slug', 'created_at')
    search_fields = ('title', 'creator__username', 'slug')
    list_filter = ('created_at',)
    readonly_fields = ('slug',)
    filter_horizontal = ('tags',) 
    
@admin.register(BoardMessage)
class BoardMessageAdmin(admin.ModelAdmin):
    list_display = ('board', 'sender', 'slug', 'created_at')
    search_fields = ('content', 'sender__username', 'slug', 'board__title')
    list_filter = ('created_at', 'board')
    readonly_fields = ('slug',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
