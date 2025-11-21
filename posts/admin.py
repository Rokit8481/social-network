from django.contrib import admin
from .models import Post, PostLike, Comment, CommentLike, File

from django.contrib import admin
from .models import Post, PostLike, Comment, CommentLike, File


class FileInline(admin.TabularInline): 
    model = File
    extra = 1   
    fields = ("file",)  
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("title", "content")
    inlines = [FileInline]  


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "created_at")
