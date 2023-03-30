import datetime

from django import template
from pytz import utc


register = template.Library()


@register.filter
def weekday(date: datetime):
    if utc.localize(datetime.datetime.now()) - datetime.timedelta(days=6) < date:
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        return weekdays[date.weekday()]
    
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    return "{}. {} {}".format(date.day, months[date.month-1], date.year)


@register.filter
def previousMessageWasAtAnotherDay(messages, index):
    if not index: return True

    return messages[index-1].created_at.strftime("%d. %B %Y") != messages[index].created_at.strftime("%d. %B %Y")