import datetime
import locale
from typing import Any

from django import template
from pytz import utc


register = template.Library()


@register.filter
def weekday(date: datetime):
    locale.setlocale(locale.LC_ALL, 'de_DE')
    if utc.localize(datetime.datetime.now()) - datetime.timedelta(days=6) < date:
        return date.strftime("%A")
    return date.strftime("%d. %B %Y")


@register.filter
def previousMessageWasAtAnotherDay(messages: list[Any], index):
    if not index: return True

    return messages[index-1].created_at.strftime("%d. %B %Y") != messages[index].created_at.strftime("%d. %B %Y")