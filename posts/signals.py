from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from posts.models import Post, PostLike, Comment, CommentLike
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.signals import notify_user
from accounts.helpers.custom_settings import MAX_PEOPLE_TAGS
from django.core.exceptions import ValidationError

User = get_user_model()

@receiver(m2m_changed, sender=Post.people_tags.through)
def limit_people_tags(sender, instance, action, pk_set, **kwargs):
    if action != "pre_add":
        return

    current_count = instance.people_tags.count()
    if current_count + len(pk_set) > MAX_PEOPLE_TAGS:
        raise ValidationError(
            f"You can tag at most {MAX_PEOPLE_TAGS} people."
        )

@receiver(post_save, sender=Post)
def create_new_post_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    post_author = instance.author
    followers = post_author.followers.all()

    for follow_obj in followers:
        follower = follow_obj.follower 

        already = Notification.objects.filter(
            to_user=follower,
            from_user=post_author,
            event_type=Notification.EventType.NEW_POST,
            target_type=Notification.TargetType.POST,
            target_id=instance.id
        ).exists()

        if not already:
            notify_user(
                to_user=follower,
                from_user=post_author,
                event_type=Notification.EventType.NEW_POST,
                target=instance
            )


@receiver(post_save, sender=Comment)
def create_new_comment_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    comment = instance
    post = comment.post
    post_author = post.author
    comment_author = comment.user  

    if post_author == comment_author:
        return
    
    already = Notification.objects.filter(
        to_user=post_author,
        from_user=comment_author,
        event_type=Notification.EventType.NEW_COMMENT,
        target_type=Notification.TargetType.POST,
        target_id=post.id
    ).exists()

    if not already:
        notify_user(
            to_user=post_author,
            from_user=comment_author,
            event_type=Notification.EventType.NEW_COMMENT,
            target=post
        )

@receiver(post_save, sender=PostLike)
def create_new_post_like_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    post_like = instance
    post = post_like.post
    like_author = post_like.user
    post_author = post.author

    if like_author == post_author:
        return
    
    already = Notification.objects.filter(
        to_user=post_author,
        from_user=like_author,
        event_type=Notification.EventType.POST_LIKE,
        target_type=Notification.TargetType.POST,
        target_id=post.id
    ).exists()

    if not already:
        notify_user(
            to_user=post_author,
            from_user=like_author,
            event_type=Notification.EventType.POST_LIKE,
            target=post
        )
    

@receiver(post_save, sender=CommentLike)
def create_new_comment_like_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    comment_like = instance
    comment = comment_like.comment
    like_author = comment_like.user
    comment_author = comment.user

    if like_author == comment_author:
        return
    
    already = Notification.objects.filter(
        to_user=comment_author,
        from_user=like_author,
        event_type=Notification.EventType.COMMENT_LIKE,
        target_type=Notification.TargetType.COMMENT,
        target_id=comment.id
    ).exists()

    if not already:
        notify_user(
            to_user=comment_author,
            from_user=like_author,
            event_type=Notification.EventType.COMMENT_LIKE,
            target=comment
        )
    


@receiver(m2m_changed, sender=Post.people_tags.through)
def create_tagged_in_post_notification(sender, instance, pk_set, action, **kwargs):
    if action != "post_add" or not pk_set:
        return
    
    tagged_users = User.objects.filter(pk__in=pk_set)

    author = instance.author

    for tagged_user in tagged_users:
            if author.pk == tagged_user.pk:
                continue

            already = Notification.objects.filter(
                to_user=tagged_user,
                from_user=author,
                event_type=Notification.EventType.TAGGED_IN_POST,
                target_type=Notification.TargetType.POST,
                target_id=instance.pk
            ).exists()

            if not already:
                notify_user(
                    to_user=tagged_user,
                    from_user=author,
                    event_type=Notification.EventType.TAGGED_IN_POST,
                    target=instance
                )
