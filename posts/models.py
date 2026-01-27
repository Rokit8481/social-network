from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import BaseModel
from accounts.helpers.custom_settings import MAX_FILES_PER_POST
from accounts.helpers.choices.files import FILE_TYPE_MAP
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
import os
from urllib.parse import urlparse

User = get_user_model()

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Author')
    title = models.CharField(max_length=128, verbose_name='Title', blank=False, null=False)
    content = models.CharField(max_length=4096, blank=False, null=False, verbose_name='Content')
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
    file = CloudinaryField('file', folder='post_files/')

    def __str__(self):
        return f"File for {self.post.title}"
    
    @property
    def file_type(self):
        if not self.file:
            return "other"

        parsed_url = urlparse(self.file.url)
        ext = os.path.splitext(parsed_url.path)[1].lower()

        for file_type, extensions in FILE_TYPE_MAP.items():
            if ext in extensions:
                return file_type

        return "other"
    
    @property
    def is_media(self):
        return self.file_type in {"image", "video"}

    @property
    def is_attachment(self):
        return not self.is_media
    
    def clean(self):
        if not self.post_id:
            return

        qs = self.post.files.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.count() >= MAX_FILES_PER_POST:
            raise ValidationError(
                f"One post can have at most {MAX_FILES_PER_POST} files."
            )


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['-created_at']

class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='User')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Post')
    content = models.CharField(max_length=4096, blank=False, null=False, verbose_name='Content')
    

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

