from django import template
from django.db.models import F, Subquery, OuterRef, Q, Count, Sum

from character.middleware import RequestSpieler
from httpChat.models import Account, ChatroomAccount

register = template.Library()


@register.filter
def newMessages(spieler: RequestSpieler) -> int:

    # should never happen
    if not spieler or not spieler.instance: return "-"

    return Account.objects\
            .prefetch_related("spieler", "chatroom_set", "chatroom_set__message_set")\
            .filter(spieler=spieler.instance)\
            .annotate(
                new_messages = Count("chatroom__message", distinct=True, filter=
                    ~Q(chatroom__message__author__id=F("id")) &         # .exclude(author=account)
                    Q(chatroom__message__type="m") &                    # type is a written message, no info or sth.
                    Q(chatroom__message__created_at__gte=Subquery(    # message that is younger than the last time the account opened the chatroom
                        ChatroomAccount.objects.filter(account__id=OuterRef("id"), chatroom=OuterRef("chatroom"))[:1].values("latest_access")
                    ))
                )
            )\
            .aggregate(Sum("new_messages"))["new_messages__sum"]