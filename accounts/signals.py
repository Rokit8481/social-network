# accounts/signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models import Follow
from notifications.models import Notification


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if not created:
        return

    follower = instance.follower
    following = instance.following

    if follower == following:
        return

    already = Notification.objects.filter(
        to_user=following,
        from_user=follower,
        event_type=Notification.EventType.NEW_FOLLOWER,
        target_type=Notification.TargetType.USER,
        target_id=following.id
    ).exists()

    if not already:
        Notification.create_notification(
            to_user=following,
            from_user=follower,
            event_type=Notification.EventType.NEW_FOLLOWER,
            target=following
        )
