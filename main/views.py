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
        current_user = request.user

        users_i_follow = Follow.objects.filter(
            follower=current_user
        ).values_list('following', flat=True)

        second_level_ids  = Follow.objects.filter(follower__in=users_i_follow
        ).exclude(following=current_user
        ).exclude(following__in=users_i_follow
        ).values_list('following', flat=True).distinct()

        #2. POSSIBLE FRIENDS
        possible_friends = User.objects.filter(
            id__in=second_level_ids
        )

        #2.1. ALREADY FOLLOWING
        already_following = set(
            Follow.objects.filter(
                follower=current_user,
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
            board.user_is_member = board.is_member(current_user)
            board.boards_mini = True

        #6. TOP 10 TAGS
        tags = (
            Tag.objects
            .annotate(boards_count=Count('boards'))
            .order_by('-boards_count')
        )[:10]
        for tag in tags:
            if tag.boards_count >= 100:
                tag.boards_count = "+99"
            
        #7. STATS
        boards_count = Board.objects.filter(creator=current_user).count()
        board_messages_count = BoardMessage.objects.filter(sender=current_user).count()
        posts_count = Post.objects.filter(author=current_user).count()
        posts_likes_count = PostLike.objects.filter(user=current_user).count()
        comments_count = Comment.objects.filter(user=current_user).count()
        comments_likes_count = CommentLike.objects.filter(user=current_user).count()
        chats_count = Chat.objects.filter(users=current_user, is_group=False).count()
        messenger_messages_count = Message.objects.filter(user=current_user).count()
        stats = {
            "boards_count": boards_count,
            "board_messages_count": board_messages_count,
            "posts_count": posts_count,
            "posts_likes_count": posts_likes_count,
            "comments_count": comments_count,
            "comments_likes_count": comments_likes_count,
            "chats_count": chats_count,
            "messenger_messages_count": messenger_messages_count,
        }

        return render(request, self.template_name, {
            "user": current_user,
            "active_tab": tab,
            "posts": posts[:5],
            "top_boards": boards,
            "top_tags": tags,
            "possible_friends": possible_friends[:15],
            "stats": stats,
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
