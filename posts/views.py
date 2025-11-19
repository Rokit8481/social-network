from django.views.generic import View, ListView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from posts.models import Post, Like
from posts.forms import *
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

class PostsListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_at')
        form = PostForm()
        return render(request, 'posts/posts_list.html', {
            'posts': posts,
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts-list')

        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'posts/posts_list.html', {
            'posts': posts,
            'form': form
        })
    
class ToggleLikeAPI(LoginRequiredMixin, View):
    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })

class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        like = Like.objects.filter(post=post)

        viewed = post.viewers.filter(id=request.user.id).exists()
        if not viewed:
            post.viewers.add(request.user)

        viewers_count = post.viewers.count()
        liked_by_user = like.filter(user=request.user).exists()
            
        return render(request, 'posts/post_detail.html', {
            'post': post,
            'viewers_count': viewers_count,
            'liked_by_user': liked_by_user
        })