from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import BaseModel
from channels.db import database_sync_to_async

User = get_user_model()

class Notification(BaseModel):
    class EventType(models.TextChoices):
        # MESSENGER 2/2
        NEW_MESSENGER_MESSAGE = "new_messenger_message", "New messenger message" # ✔️
        MESSAGE_REACTION = "message_reaction", "Message reaction" # ✔️

        # POSTS 5/5
        NEW_POST = "new_post", "New post" # ✔️
        POST_LIKE = "post_like", "Post like" # ✔️
        NEW_COMMENT = "new_comment", "New comment" # ✔️
        COMMENT_LIKE = "comment_like", "Comment like" # ✔️
        TAGGED_IN_POST = "tagged_in_post", " Tagged in post" # ✔️ 

        # ACCOUNTS 1/1
        NEW_FOLLOWER = "new_follower", "New follower" # ✔️

        # GROUPS 2/2 
        NEW_GROUP_MESSAGE = "new_group_messsage", " New group message" # ✔️
        JOIN_GROUP = "join_group", "Join group" # ✔️


    class TargetType(models.TextChoices):
        USER = "user", "User"
        POST = "post", "Post"
        COMMENT = "comment", "Comment"
        REACTION = "reaction", "Reaction"
        MESSAGE = "message", "Message"
        GROUP = "group", "Group"

    
    TYPE_MAP = {
        "UserProfile": TargetType.USER,
        "Post": TargetType.POST,
        "Comment": TargetType.COMMENT,
        "Reaction": TargetType.REACTION,
        "Message": TargetType.MESSAGE,
        "Group": TargetType.GROUP,
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
        notification = cls.objects.create(
            to_user=to_user,
            from_user=from_user,
            event_type=event_type,
            target_type=cls.TYPE_MAP[target.__class__.__name__],
            target_id=target.id
        )
        return notification
        
    def get_message(self):
        if self.event_type == self.EventType.NEW_GROUP_MESSAGE:
            from groups.models import Group
            group = Group.objects.filter(pk=self.target_id).first()
            if group:
                return f"In group '{group.title}' there is a new message"
            return "New message in a group"

        elif self.event_type == self.EventType.JOIN_GROUP:
            from groups.models import Group
            group = Group.objects.filter(pk=self.target_id).first()
            if group:
                return f"{self.from_user.username} joined group, where you are admin, '{group.title}'"
            return f"{self.from_user.username} joined a group"

        elif self.event_type == self.EventType.NEW_POST:
            from posts.models import Post
            post = Post.objects.filter(pk=self.target_id).first()
            if post:
                return f"{self.from_user.username} posted a new post '{post.title}'"
            return f"{self.from_user.username} posted a new post"
        
        elif self.event_type == self.EventType.POST_LIKE:
            from posts.models import Post
            post = Post.objects.filter(pk=self.target_id).first()
            if post:
                return f"{self.from_user.username} liked your post '{post.title}'"
            return f"{self.from_user.username} liked your post"

        elif self.event_type == self.EventType.NEW_COMMENT:
            from posts.models import Post
            post = Post.objects.filter(pk=self.target_id).first()
            if post:
                return f"{self.from_user.username} commented on your post '{post.title}'"
            return f"{self.from_user.username} commented on your post"
        
        elif self.event_type == self.EventType.COMMENT_LIKE:
            from posts.models import Comment
            comment = Comment.objects.filter(pk=self.target_id).first()
            if comment:
                post = comment.post
                return f"{self.from_user.username} liked on your comment under the post '{post.title}'"
            return f"{self.from_user.username} liked on your comment"
        
        elif self.event_type == self.EventType.TAGGED_IN_POST:
            from posts.models import Post
            post = Post.objects.filter(pk=self.target_id).first()
            if post:
                return f"{self.from_user.username} posted a new post '{post.title}' and tagged you"
            return f"{self.from_user.username} posted a new post and tagged you"
        
        elif self.event_type == self.EventType.NEW_FOLLOWER:
            return f"{self.from_user.username} followed you"
        
        elif self.event_type == self.EventType.NEW_MESSENGER_MESSAGE:
            from messenger.models import Message
            message = Message.objects.filter(pk=self.target_id).first()
            if message:
                chat = message.chat
                author = message.user
                if chat.is_group == True:
                    return f"You have a new message in group '{chat.title}' by {author.username}"
                return f"You have a new message from '{author.username}'"
            return f"You have a new message in chat/group"
        elif self.event_type == self.EventType.MESSAGE_REACTION:
            from messenger.models import Reaction
            reaction = Reaction.objects.filter(pk=self.target_id).first()
            if reaction:
                message = reaction.message
                chat = message.chat
                author = reaction.user
                if chat.is_group == True:
                    return f"{author.username} put a {reaction.emoji} on your message '{message.text[:15]}...' in group '{chat.title}'"
                return f"{author.username} put a {reaction.emoji} on your message '{message.text[:15]}...' in your chat"
            return "You have a new reaction on your message"
        
        return "You have a new notification"
    
    @database_sync_to_async
    def async_get_message(self):
        return self.get_message()
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

