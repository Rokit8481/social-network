from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from accounts.models import Follow
from posts.models import Post, PostLike, Comment, CommentLike, File
from posts.forms import PostForm
from messenger.models import Chat, Message, Reaction
from boards.models import Board, BoardMessage, Tag
from notifications.models import Notification
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

class MainPageView(LoginRequiredMixin, View):
    template_name = "main/main_page.html"
    def get(self, request, *args, **kwargs):
        #0. HELPERS
        user = request.user
        follows = Follow.objects.filter(follower=user)
        users_i_follow = follows.values_list('following', flat=True)
        tab = request.GET.get("tab", "feed")

        if tab == "recommendations":
            posts = Post.objects.filter(
                author__in=users_i_follow
            ).order_by("-id")
        else:
            posts = Post.objects.all().order_by("-id")


        #2. POSTS BY USERS I FOLLOW
        posts_by_followings = Post.objects.filter(author__in=users_i_follow).order_by("-id")[:5]

        #3. ALL BOARDS
        boards = Board.objects.annotate(
            members_count=Count("members")
        ).order_by("-members_count")[:5]

        #4. BOARDS BY USERS I FOLLOW
        boards_by_followings = Board.objects.filter(creator__in=users_i_follow).order_by("members")

        return render(request, self.template_name, {
            "user": user,
            "active_tab": tab,
            "posts": posts[:5],
            "posts_by_followings": posts_by_followings,
            "boards": boards,
            "boards_by_followings": boards_by_followings,
        })
    
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            
            for f in request.FILES.getlist('files'):
                File.objects.create(post=post, file=f)
            return redirect('post_detail', post_pk=post.pk)
        
        return render(request, self.template_name, {'form': form})
