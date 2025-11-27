from django.contrib import admin
from .models import Group, GroupMessage, GroupMessageFile, Tags

class TagsInline(admin.TabularInline):
    model = Tags
    extra = 1
    fields = ('name',)
    readonly_fields = ()
    show_change_link = True

class GroupMessageFileInline(admin.TabularInline):
    model = GroupMessageFile
    extra = 1
    fields = ('file',)
    readonly_fields = ()
    show_change_link = True

class GroupMessageInline(admin.TabularInline):
    model = GroupMessage
    extra = 1
    fields = ('sender', 'content', 'slug')
    readonly_fields = ('slug',)
    show_change_link = True
    inlines = [GroupMessageFileInline]  

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'slug', 'created_at')
    search_fields = ('title', 'creator__username', 'slug')
    list_filter = ('created_at',)
    readonly_fields = ('slug',)
    inlines = [TagsInline, GroupMessageInline]

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'slug', 'created_at')
    search_fields = ('content', 'sender__username', 'slug', 'group__title')
    list_filter = ('created_at', 'group')
    readonly_fields = ('slug',)
    inlines = [GroupMessageFileInline]

@admin.register(GroupMessageFile)
class GroupMessageFileAdmin(admin.ModelAdmin):
    list_display = ('message', 'file', 'created_at')
    search_fields = ('message__slug', 'file')
    list_filter = ('created_at',)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')
    search_fields = ('name', 'group__title')
    list_filter = ('group',)