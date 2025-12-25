from django.dispatch import receiver
from django.db.models.signals import post_save
from messenger.models import Message, Reaction
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.signals import notify_user

User = get_user_model()

@receiver(post_save, sender=Message)
def new_messanger_message_notifications(sender, instance, created, **kwargs):
    if not created:
        return
    
    message = instance
    chat = message.chat
    message_user = message.user
    chat_users = chat.users.exclude(pk=message_user.pk)

    for user in chat_users:
        already = Notification.objects.filter(
            to_user=user,
            from_user=message_user,
            event_type=Notification.EventType.NEW_MESSENGER_MESSAGE,
            target_type=Notification.TargetType.MESSAGE,
            target_id=message.id
        ).exists()

        if not already:
            notify_user(
                to_user=user,
                from_user=message_user,
                event_type=Notification.EventType.NEW_MESSENGER_MESSAGE,
                target=message
            )

@receiver(post_save, sender=Reaction)
def new_message_notification_notifications(sender, instance, created, **kwargs):
    if not created:
        return
    
    reaction = instance
    message = reaction.message
    reaction_user = reaction.user
    message_user = message.user

    if reaction_user == message_user:
        return

    already = Notification.objects.filter(
        to_user=message_user,
        from_user=reaction_user,
        event_type=Notification.EventType.MESSAGE_REACTION,
        target_type=Notification.TargetType.REACTION,
        target_id=reaction.id
    ).exists()

    if not already:
        notify_user(
            to_user=message_user,
            from_user=reaction_user,
            event_type=Notification.EventType.MESSAGE_REACTION,
            target=reaction
        )
