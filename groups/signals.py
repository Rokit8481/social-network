from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from groups.models import Group, GroupMessage
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

# @receiver(post_save, sender=Follow)
# def create_follow_notification(sender, instance, created, **kwargs):
#     if not created:
#         return

#     follower = instance.follower
#     following = instance.following

#     if follower == following:
#         return

#     already = Notification.objects.filter(
#         to_user=following,
#         from_user=follower,
#         event_type=Notification.EventType.NEW_FOLLOWER,
#         target_type=Notification.TargetType.USER,
#         target_id=following.id
#     ).exists()

#     if not already:
#         Notification.create_notification(
#             to_user=following,
#             from_user=follower,
#             event_type=Notification.EventType.NEW_FOLLOWER,
#             target=following
#         )

@receiver(post_save, sender=GroupMessage)
def create_new_group_message_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    group = instance.group
    sender = instance.sender

    members = group.members.all()
    for member in members:
        if member.pk == sender.pk:
            continue

        Notification.create_notification(
            to_user=member,
            from_user=sender,
            event_type=Notification.EventType.NEW_GROUP_MESSAGE,
            target=group
        )

@receiver(m2m_changed, sender=Group.members.through)
def create_join_group_notification(sender, instance, pk_set, action, **kwargs):
    if action != "post_add" or not pk_set:
        return
    
    new_users = User.objects.filter(pk__in=pk_set)

    admins = list(instance.admins.all())

    for new_user in new_users:
        for admin in admins:

            if admin.pk == new_user.pk:
                continue

            already = Notification.objects.filter(
                to_user=admin,
                from_user=new_user,
                event_type=Notification.EventType.JOIN_GROUP,
                target_type=Notification.TargetType.GROUP,
                target_id=instance.pk
            ).exists()

            if not already:
                Notification.create_notification(
                    to_user=admin,
                    from_user=new_user,
                    event_type=Notification.EventType.JOIN_GROUP,
                    target=instance
                )
