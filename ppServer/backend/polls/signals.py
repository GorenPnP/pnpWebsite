from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from webPush.models import PushSettings, PushTag

from .models import *


@receiver(post_save, sender=Question)
def send_webpush(sender, instance, **kwargs):
    if not kwargs['created']: return

    # notify users
    text = instance.text[:50]
    if len(instance.text) > 50: text += "..."

    users = get_user_model().objects.all()
    PushSettings.send_message(users, "Neue Umfrage", f"{text} (ab {instance.pub_date:%d.%m.%Y %H:%M} verfügbar)", PushTag.polls)