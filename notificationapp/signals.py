from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from main.models import Auction, AuctionResult, Bid 
from notificationapp.models import Notification, NotificationCategories

User = get_user_model()

@receiver(post_save, sender=Auction)
def notify_all_users_on_auction_create(sender, instance, created, **kwargs):
    if not created:
        return

    channel_layer = get_channel_layer()
    auction_ct = ContentType.objects.get_for_model(Auction)
    all_users = User.objects.all()

    for user in all_users:
        # --------------------------------------
        # 1) Create notification for this user
        # --------------------------------------
        notif = Notification.objects.create(
            user=user,
            sender=instance.created_by,
            category=NotificationCategories.AUCTION_CREATED,
            content_type=auction_ct,
            object_id=instance.id,
        )
        # content auto-generated in model.save()

        # --------------------------------------
        # 2) Send WebSocket message to this user
        # --------------------------------------
        async_to_sync(channel_layer.group_send)(
            f"user_notifications_{user.id}",
            {
                "type": "send_notification",
                "message": notif.content,  # use the generated message
                "data": {
                    "notification_id": notif.id,
                    "auction_id": instance.id,
                    "title": instance.title,
                    "sender": instance.created_by.username,
                    "category": notif.category,
                    "created_at": notif.created_at.isoformat(),
                }
            }
        )


@receiver(post_save, sender=AuctionResult)
def handle_auction_result(sender, instance, created, **kwargs):
    """
    Handles actions after an AuctionResult is created (i.e., an item is finalized).
    It sends notifications to all participants (winner and losers).
    """
    if not created:
        # Only run this logic when the AuctionResult is first created, not on update.
        return

    # 1. Gather all participants and the item details
    result = instance
    item = result.item
    winner = result.winner
    
    # Get all unique users who placed a bid on this item
    participant_ids = Bid.objects.filter(item=item).values_list('created_by', flat=True).distinct()
    
    participants = list(participant_ids)
    
    # Send a separate notification and real-time alert to each participant
    for user_id in participants:
        is_winner = (user_id == winner.id)
        
        if is_winner:
            category = NotificationCategories.AUCTION_WON
            message_content = f"🎉 **Congratulations!** You won the bid for **{item.title}**!"
        else:
            category = NotificationCategories.AUCTION_OUTBID # Re-using OUTBID for simplicity, or add a new 'AUCTION_LOST'
            message_content = f"😔 You did not win the bid for **{item.title}**."

        # 2. Create the Notification object in the database
        notif = Notification.objects.create(
            user_id=user_id,
            sender=item.auction.created_by, # The user who created the auction (or leave null)
            category=category,
            content=message_content,
            # Use Generic Foreign Key to link to the Item
            content_object=item 
        )

        # 3. Send real-time alert via Channels
        send_realtime_notification(user_id, notif)


def send_realtime_notification(user_id, notification_instance: Notification):
    """
    Helper function to send a message to the user's private Channels group.
    """
    channel_layer = get_channel_layer()
    group_name = f'user_notifications_{user_id}'

    # Use async_to_sync since signals run synchronously
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            # IMPORTANT: 'type' must match the consumer's handler method name (send_notification)
            'type': 'send_notification', 
            'message': notification_instance.content,
            'data': {
                'id': notification_instance.id,
                'category': notification_instance.category,
                'item_slug': notification_instance.content_object.slug if notification_instance.content_object else None
            }
        }
    )