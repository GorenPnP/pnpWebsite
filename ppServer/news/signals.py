from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from webPush.models import PushSettings, PushTag

from .models import *


@receiver(pre_save, sender=News)
def send_webpush(sender, instance, **kwargs):

    # on message create or set newly published
    if not instance or not instance.published: return

    old_instance = News.objects.filter(id=instance.id).first()
    if old_instance and old_instance.published: return

    # notify users
    users = User.objects.all()
    PushSettings.send_message(users, "Neuer Zeitungsartikel", instance.titel, PushTag.news)