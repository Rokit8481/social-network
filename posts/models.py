from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import BaseModel
import os

User = get_user_model()

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Author')
    title = models.CharField(max_length=100, verbose_name='Title', blank=False, null=False)
    content = models.TextField(blank=False, null=False, verbose_name='Content')
    people_tags = models.ManyToManyField(User, related_name='tagged_posts', blank=True, verbose_name='Tagged People')
    viewers = models.ManyToManyField(User, related_name='viewed_posts', blank=True, verbose_name='Viewers')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']

class File(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files', verbose_name='Post')
    file = models.FileField(upload_to='post_files/', verbose_name='File')

    def __str__(self):
        return f"File for {self.post.title}"
    
    @property
    def file_type(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            return "image"
        if ext in [".mp4", ".mov", ".webm"]:
            return "video"
        return "other"
    
    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['-created_at']

class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='User')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Post')
    content = models.TextField(blank=False, null=False, verbose_name='Content')
    

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

class PostLike(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name='User')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='Post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
    
    class Meta:
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'
        unique_together = ('user', 'post')

class CommentLike(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes', verbose_name='User')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', verbose_name='Comment')

    def __str__(self):
        return f"{self.user.username} likes {self.comment.post.title} comment"
    
    class Meta:
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'
        unique_together = ('user', 'comment')

