from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from webPush.models import PushSettings, PushTag

from .models import *


@receiver(post_save, sender=Changelog)
def send_webpush(sender, instance, **kwargs):
    if kwargs['created']:
        text = instance.text[:77]
        if len(instance.text) > 77: text += "..."

        PushSettings.send_message(User.objects.all(), "Update der Website", text, PushTag.changelog)