from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Exists
from django.db.models.signals import post_save
from django.db.models.functions import Coalesce
from django.dispatch import receiver

from httpChat.models import ChatroomAccount
from webPush.models import PushSettings, PushTag

from .models import *


@receiver(post_save, sender=Message)
# @receiver(post_save, sender=ChatroomAccount)  # manually called in .views.py
def send_webpush(sender, instance, **kwargs):
    if sender == Message and not kwargs['created']: return

    # get spieler impacted by a change
    if sender == Message:
        spieler_qs = Spieler.objects.prefetch_related("account__chatroom__message").filter(account__chatroom__message=instance)
    elif sender == ChatroomAccount:
        spieler_qs = Spieler.objects.filter(pk=instance.account.spieler.id)

    # get their count of unread messages
    unread_message_qs = Account.objects.load_unread_messages().prefetch_related("spieler").filter(spieler__id=OuterRef("id"))
    impacted_spieler = spieler_qs.annotate(
            num_messages = Coalesce(SumSubquery("unread_messages", queryset=unread_message_qs, output_field=models.IntegerField()), 0)
        )\
        .filter(num_messages__gt=0)\
        .values("name", "num_messages")

    spieler_dict = {spieler["name"]: spieler for spieler in impacted_spieler }


    # send notification about unread messages
    for user in get_user_model().objects.filter(username__in=spieler_dict.keys()):

        accounts = Account.objects.prefetch_related("spieler").filter(spieler__name=user.username)

        messages = Message.objects\
            .prefetch_related("author")\
            .annotate(
                unseen = Exists(ChatroomAccount.objects.filter(account__in=accounts, chatroom__id=OuterRef("chatroom__id"), latest_access__lte=OuterRef("created_at"))),
            )\
            .filter(
                ~Q(author__in=accounts) &   # .exclude(author=account)
                Q(type="m") &               # type is a written message, no info or sth.
                Q(unseen=True)              # message that is younger than the last time any owned account opened the chatroom
            )

        num_messages = spieler_dict[user.username]['num_messages']
        # >= 5 Messages: m Nachrichten aus n Chats
        if num_messages >= 5:
            chatrooms = messages.aggregate(e=Count('chatroom', distinct=True))['e']
            PushSettings.send_message([user], "Ungelesene Chat-Nachrichten", f"{num_messages} Nachrichten aus {chatrooms} Chat{'s' if chatrooms > 1 else ''}", PushTag.chat)
            continue

        # send more verbose pushie
        stringified_messages = [f"{msg.author}: {msg.text}" for msg in messages.order_by("-created_at")]
        PushSettings.send_message([user], "Ungelesene Chat-Nachrichten", "\n".join([msg[:27] + '...' if len(msg) >= 27 else msg for msg in stringified_messages]), PushTag.chat)




