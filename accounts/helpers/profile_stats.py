"""Shared profile counters for main page and user profile (display caps)."""

from boards.models import Board, BoardMessage
from messenger.models import Chat, Message, Reaction
from posts.models import Post, PostLike, Comment, CommentLike


def cap_stat_number(number):
    if isinstance(number, bool):
        return number
    if isinstance(number, int) and number > 1000:
        return "+999"
    return number


def raw_profile_stats(user):
    return {
        "boards_count": Board.objects.filter(creator=user).count(),
        "board_messages_count": BoardMessage.objects.filter(sender=user).count(),
        "posts_count": Post.objects.filter(author=user).count(),
        "tagged_in_posts_count": Post.objects.filter(people_tags=user).count(),
        "posts_likes_given_count": PostLike.objects.filter(user=user).count(),
        "my_posts_likes_count": PostLike.objects.filter(post__author=user).count(),
        "comments_given_count": Comment.objects.filter(user=user).count(),
        "comments_got_count": Comment.objects.filter(post__author=user).count(),
        "comments_likes_given_count": CommentLike.objects.filter(user=user).count(),
        "my_comments_likes_count": CommentLike.objects.filter(comment__user=user).count(),
        "chats_count": Chat.objects.filter(users=user, is_group=False).count(),
        "groups_count": Chat.objects.filter(users=user, is_group=True).count(),
        "messenger_messages_count": Message.objects.filter(user=user).count(),
        "reactions_given_count": Reaction.objects.filter(user=user).count(),
        "reactions_got_count": Reaction.objects.filter(message__user=user).count(),
    }


def profile_stats_for_display(user, *, main_page=False):
    stats = raw_profile_stats(user)
    if main_page:
        stats["main_page"] = True
    for key, value in list(stats.items()):
        if key == "main_page":
            continue
        stats[key] = cap_stat_number(value)
    return stats
