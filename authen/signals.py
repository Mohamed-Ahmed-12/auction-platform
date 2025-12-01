from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from dashboard.events_queue import event_queue
import json

User = get_user_model()

@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, **kwargs):
    if created:
        data = json.dumps({"user_count": User.objects.count()})
        async_to_sync(event_queue.put)(data)
