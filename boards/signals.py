from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from boards.models import Board, BoardMessage
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.signals import notify_user

User = get_user_model()

@receiver(post_save, sender=BoardMessage)
def create_new_board_message_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    board = instance.board
    sender = instance.sender

    members = board.members.all()
    for member in members:
        if member.pk == sender.pk:
            continue

        notify_user(
            to_user=member,
            from_user=sender,
            event_type=Notification.EventType.NEW_BOARD_MESSAGE,
            target=board
        )

@receiver(m2m_changed, sender=Board.members.through)
def create_join_board_notification(sender, instance, pk_set, action, **kwargs):
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
                event_type=Notification.EventType.JOIN_BOARD,
                target_type=Notification.TargetType.BOARD,
                target_id=instance.pk
            ).exists()

            if not already:
                notify_user(
                    to_user=admin,
                    from_user=new_user,
                    event_type=Notification.EventType.JOIN_BOARD,
                    target=instance
                )
