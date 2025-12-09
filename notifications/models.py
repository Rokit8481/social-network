from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import BaseModel

User = get_user_model()

class Notification(BaseModel):
    class EventType(models.TextChoices):
        # MESSENGER 2/2
        NEW_MESSENGER_MESSAGE = "new_messenger_message", "New messenger message"
        MESSAGE_REACTION = "message_reaction", "Message reaction"

        # POSTS 5/5
        NEW_POST = "new_post", "New post"
        POST_LIKE = "post_like", "Post like"
        NEW_COMMENT = "new_comment", "New comment"
        COMMENT_LIKE = "comment_like", "Comment like"
        TAGGED_IN_POST = "tagged_in_post", " Tagged in post"

        # ACCOUNTS 1/1
        NEW_FOLLOWER = "new_follower", "New follower"

        # GROUPS 2/2
        NEW_GROUP_MESSAGE = "new_group_messsage", " New group message"
        JOIN_GROUP = "join_group", "Join group"


    class TargetType(models.TextChoices):
        USER = "user", "User"
        POST = "post", "Post"
        COMMENT = "comment", "Comment"
        REACTION = "reaction", "Reaction"
        MESSAGE = "message", "Message"
        GROUP = "group", "Group"
        CHAT = "chat", "Chat"

    
    TYPE_MAP = {
        "UserProfile": TargetType.USER,
        "Post": TargetType.POST,
        "Comment": TargetType.COMMENT,
        "Reaction": TargetType.REACTION,
        "Message": TargetType.MESSAGE,
        "Group": TargetType.GROUP,
        "Chat": TargetType.CHAT,
    }

    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Recipient")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name="Sender")
    event_type = models.CharField(max_length=100, choices=EventType.choices, verbose_name="Event Type")
    target_type = models.CharField(max_length=100, choices=TargetType.choices, verbose_name="Target Type")
    target_id = models.IntegerField(verbose_name="Target ID")
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.to_user} - {self.event_type}"

    @classmethod
    def create_notification(cls, to_user, from_user, event_type, target):
        cls.objects.create(
            to_user=to_user,
            from_user=from_user,
            event_type=event_type,
            target_type=cls.TYPE_MAP[target.__class__.__name__],
            target_id=target.id
        )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
