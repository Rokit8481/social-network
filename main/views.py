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
        #1. CURRENT USER
        user = request.user

        users_i_follow = Follow.objects.filter(
            follower=request.user
        ).values_list('following', flat=True)

        second_level_ids  = Follow.objects.filter(follower__in=users_i_follow
        ).exclude(following=request.user
        ).exclude(following__in=users_i_follow
        ).values_list('following', flat=True).distinct()

        #2. POSSIBLE FRIENDS
        possible_friends = User.objects.filter(
            id__in=second_level_ids
        )

        #2.1. ALREADY FOLLOWING
        already_following = set(
            Follow.objects.filter(
                follower=request.user,
                following__in=possible_friends
            ).values_list('following_id', flat=True)
        )

        for possible_friend in possible_friends:
            possible_friend.is_following = possible_friend.id in already_following
        
        #3.TABS
        tab = request.GET.get("tab", "feed")

        #4. POSTS
        if tab == "recommendations":
            posts = Post.objects.filter(
                author__in=users_i_follow
            ).order_by("-id")
        else:
            posts = Post.objects.all().order_by("-id")

        #5. TOP 5 BOARDS
        boards = Board.objects.annotate(
            members_count=Count("members")
        ).order_by("-members_count")[:5]
        for board in boards:
            board.user_is_member = board.is_member(request.user)
            board.boards_position = True

        return render(request, self.template_name, {
            "user": user,
            "active_tab": tab,
            "posts": posts[:5],
            "top_boards": boards,
            "possible_friends": possible_friends[:15],
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
