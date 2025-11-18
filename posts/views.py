from django.views.generic import View, ListView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from posts.models import Post, Like
from posts.forms import *
from django.contrib.auth import get_user_model

User = get_user_model()

class PostsMainView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_at')
        form = PostForm()
        return render(request, 'posts/main.html', {
            'posts': posts,
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('main')

        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'posts/main.html', {
            'posts': posts,
            'form': form
        })
    
class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()

        return redirect('main')

