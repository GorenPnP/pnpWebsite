from django import template
from django.db.models import Sum

from character.models import Spieler
from httpChat.models import Account

register = template.Library()


@register.filter
def newMessages(spieler: Spieler) -> int:

    # should never happen
    if not spieler: return "-"

    return Account.objects\
        .load_unread_messages()\
        .filter(spieler=spieler)\
        .aggregate(Sum("unread_messages"))["unread_messages__sum"]
