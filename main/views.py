from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.helpers.profile_stats import profile_stats_for_display
from accounts.models import Follow
from posts.models import Post, File
from posts.forms import PostForm
from boards.models import Board, Tag
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

User = get_user_model()


class MainPageView(LoginRequiredMixin, View):
    template_name = "main/main_page.html"

    def _build_context(self, request, form=None):
        current_user = request.user

        users_i_follow = Follow.objects.filter(
            follower=current_user
        ).values_list('following', flat=True)

        second_level_ids = Follow.objects.filter(follower__in=users_i_follow
        ).exclude(following=current_user
        ).exclude(following__in=users_i_follow
        ).values_list('following', flat=True).distinct()

        possible_friends = User.objects.filter(
            id__in=second_level_ids
        )

        already_following = set(
            Follow.objects.filter(
                follower=current_user,
                following__in=possible_friends
            ).values_list('following_id', flat=True)
        )
        following_ids = set(
            Follow.objects.filter(follower=current_user)
            .values_list("following_id", flat=True)
        )

        followers_ids = set(
            Follow.objects.filter(following=current_user)
            .values_list("follower_id", flat=True)
        )

        for possible_friend in possible_friends:
            possible_friend.is_following = possible_friend.id in already_following
            possible_friend.user_is_following = possible_friend.id in following_ids
            possible_friend.is_following_user = possible_friend.id in followers_ids
            possible_friend.is_user_friend = (
                possible_friend.id in following_ids and possible_friend.id in followers_ids
            )

        tab = request.GET.get("tab", "feed")

        q = request.GET.get("q", "").strip()
        if tab == "recommendations":
            posts = Post.objects.filter(
                author__in=users_i_follow
            ).exclude(author=current_user)
        else:
            posts = Post.objects.all().exclude(author=current_user)

        if q:
            posts = posts.filter(
                Q(author__username__icontains=q) |
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )

        posts = posts.order_by("-id")

        boards = Board.objects.annotate(
            members_count=Count("members")
        ).order_by("-members_count")[:5]
        for board in boards:
            board.user_is_member = board.is_member(current_user)
            board.boards_mini = True

        tags = (
            Tag.objects
            .annotate(boards_count=Count('boards'))
            .filter(boards_count__gt=0)
            .order_by('-boards_count')
        )[:10]
        for tag in tags:
            if tag.boards_count >= 100:
                tag.boards_count = "+99"
            else:
                tag.boards_count = tag.boards_count

        stats = profile_stats_for_display(current_user, main_page=True)

        ctx = {
            "user": current_user,
            "active_tab": tab,
            "posts": posts[:5],
            "top_boards": boards,
            "top_tags": tags,
            "possible_friends": possible_friends[:15],
            "stats": stats,
        }
        if form is not None:
            ctx["form"] = form
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self._build_context(request))

    def post(self, request):
        form = PostForm(request.POST, request.FILES, user=request.user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self._build_context(request, form=form),
            )

        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()

        try:
            for f in request.FILES.getlist('files'):
                File.objects.create(post=post, file=f)
        except ValidationError as e:
            for errors in e.message_dict.values():
                for error in errors:
                    form.add_error(None, error)
            return render(
                request,
                self.template_name,
                self._build_context(request, form=form),
            )

        return redirect('post_detail', post_pk=post.pk)
