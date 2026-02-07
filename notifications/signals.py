def notify_user(*, to_user, from_user, event_type, target, target_url):
    from .models import Notification 
    notification = Notification.create_notification(
        to_user=to_user,
        from_user=from_user,
        event_type=event_type,
        target=target,
        target_url=target_url,
    )
    
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{to_user.id}",
        {
            "type": "send_notification",
            "notification_id": notification.id,
        }
    )

    return notification