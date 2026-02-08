from django.db import models
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from accounts.models import BaseModel
from accounts.helpers.help_functions import truncate
User = get_user_model()

class Notification(BaseModel):
    
    class EventType(models.TextChoices):
        # Messenger
        NEW_MESSENGER_MESSAGE = "new_messenger_message", "New messenger message"
        MESSAGE_REACTION = "message_reaction", "Message reaction"

        # Posts
        NEW_POST = "new_post", "New post"
        POST_LIKE = "post_like", "Post like"
        NEW_COMMENT = "new_comment", "New comment"
        COMMENT_LIKE = "comment_like", "Comment like"
        TAGGED_IN_POST = "tagged_in_post", "Tagged in post"

        # Accounts
        NEW_FOLLOWER = "new_follower", "New follower"

        # Boards
        NEW_BOARD_MESSAGE = "new_board_messsage", "New board message"
        JOIN_BOARD = "join_board", "Join board"

    class TargetType(models.TextChoices):
        USER = "user", "User"
        POST = "post", "Post"
        COMMENT = "comment", "Comment"
        REACTION = "reaction", "Reaction"
        MESSAGE = "message", "Message"
        BOARD = "board", "Board"

    TYPE_MAP = {
        "UserProfile": TargetType.USER,
        "Post": TargetType.POST,
        "Comment": TargetType.COMMENT,
        "Reaction": TargetType.REACTION,
        "Message": TargetType.MESSAGE,
        "Board": TargetType.BOARD,
    }

    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_notifications"
    )

    event_type = models.CharField(max_length=100, choices=EventType.choices)
    target_type = models.CharField(max_length=100, choices=TargetType.choices)
    target_id = models.IntegerField()
    target_url = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.to_user} — {self.event_type}"

    @classmethod
    def create_notification(cls, to_user, from_user, event_type, target, target_url):
        return cls.objects.create(
            to_user=to_user,
            from_user=from_user,
            event_type=event_type,
            target_type=cls.TYPE_MAP[target.__class__.__name__],
            target_id=target.id,
            target_url=target_url,
        )

    # =========================
    # Message builders
    # =========================

    def get_message(self):
        username = truncate(self.from_user.username, 20)

        match self.event_type:

            case self.EventType.NEW_BOARD_MESSAGE:
                from boards.models import Board
                board = Board.objects.filter(pk=self.target_id).first()
                if not board:
                    return f"New message in a board by {username}"

                title = truncate(board.title, 15)
                return f"In board '{title}' there is a new message by {username}"

            case self.EventType.JOIN_BOARD:
                from boards.models import Board
                board = Board.objects.filter(pk=self.target_id).first()
                if not board:
                    return f"{username} joined a board"

                title = truncate(board.title, 15)
                return f"{username} joined board, where you are admin, '{title}'"

            case self.EventType.NEW_POST:
                from posts.models import Post
                post = Post.objects.filter(pk=self.target_id).first()
                if not post:
                    return f"{username} posted a new post"

                title = truncate(post.title, 20)
                return f"{username} posted a new post '{title}'"

            case self.EventType.POST_LIKE:
                from posts.models import Post
                post = Post.objects.filter(pk=self.target_id).first()
                if not post:
                    return f"{username} liked your post"

                title = truncate(post.title, 20)
                return f"{username} liked your post '{title}'"

            case self.EventType.NEW_COMMENT:
                from posts.models import Comment
                comment = Comment.objects.select_related("post").filter(
                    pk=self.target_id
                ).first()
                if not comment:
                    return f"{username} commented on your post"

                text = truncate(comment.content, 10)
                title = truncate(comment.post.title, 20)
                return f"{username} commented `{text}` on your post '{title}'"

            case self.EventType.COMMENT_LIKE:
                from posts.models import Comment
                comment = Comment.objects.select_related("post").filter(
                    pk=self.target_id
                ).first()
                if not comment:
                    return f"{username} liked your comment"

                text = truncate(comment.content, 10)
                title = truncate(comment.post.title, 20)
                return f"{username} liked your comment '{text}' under the post '{title}'"

            case self.EventType.TAGGED_IN_POST:
                from posts.models import Post
                post = Post.objects.filter(pk=self.target_id).first()
                if not post:
                    return f"{username} tagged you in a post"

                title = truncate(post.title, 20)
                return f"{username} posted a new post '{title}' and tagged you"

            case self.EventType.NEW_FOLLOWER:
                return f"{username} followed you"

            case self.EventType.NEW_MESSENGER_MESSAGE:
                from messenger.models import Message
                message = Message.objects.select_related("chat").filter(
                    pk=self.target_id
                ).first()
                if not message:
                    return f"You have a new message from {username}"

                chat = message.chat
                text = truncate(message.text, 15)

                if chat.is_group:
                    title = truncate(chat.title, 15)
                    return f"You have a new message in group '{title}' by {username}"

                return f"You have a new message '{text}' from '{username}'"

            case self.EventType.MESSAGE_REACTION:
                from messenger.models import Reaction
                reaction = Reaction.objects.select_related(
                    "message__chat"
                ).filter(pk=self.target_id).first()

                if not reaction:
                    return f"{username} reacted to your message"

                message = reaction.message
                chat = message.chat
                text = truncate(message.text, 15)

                if chat.is_group:
                    title = truncate(chat.title, 15)
                    return (
                        f"{username} put a {reaction.emoji} "
                        f"on your message '{text}' in group '{title}'"
                    )

                return (
                    f"{username} put a {reaction.emoji} "
                    f"on your message '{text}' in your chat"
                )

        return "You have a new notification"

    @database_sync_to_async
    def async_get_message(self):
        return self.get_message()

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

