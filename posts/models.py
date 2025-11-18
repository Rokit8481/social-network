from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Author')
    title = models.CharField(max_length=100, verbose_name='Title', blank=False, null=False)
    content = models.CharField(max_length=16384, verbose_name='Content', blank=False, null=False)
    viewers = models.ManyToManyField(User, related_name='viewed_posts', blank=True, verbose_name='Viewers')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']

class Like(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='User')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='Post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
    
    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        unique_together = ('user', 'post')

