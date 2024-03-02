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
        .load_unread_messages()\
        .prefetch_related("spieler")\
        .filter(spieler=spieler.instance)\
        .aggregate(Sum("unread_messages"))["unread_messages__sum"]
