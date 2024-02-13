from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.templatetags.new_messages import newMessages
from character.middleware import RequestSpieler
from webPush.models import PushSettings, PushTag

from .models import *


@receiver(post_save, sender=Message)
# @receiver(post_save, sender=ChatroomAccount)  # manually called in .views.py
def send_webpush(sender, instance, **kwargs):
    if sender == Message and not kwargs['created']: return

    if sender == Message:
        spieler_ids = set(instance.chatroom.accounts.all().values_list("spieler", flat=True))
    elif sender == ChatroomAccount:
        spieler_ids = [instance.account.spieler.id]
    

    # send message for spieler
    for spieler in Spieler.objects.filter(id__in=spieler_ids):
        request_spieler = RequestSpieler()
        request_spieler.instance = spieler
        num_messages = newMessages(request_spieler)

        # if they have unread messages
        if num_messages != 0:
            user = User.objects.filter(username=spieler.name).first()
            PushSettings.send_message([user], "Ungelesene Chat-Nachrichten", f"Du hast {num_messages} ungelesene Nachrichten", PushTag.chat)