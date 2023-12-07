from django import template
from django.db.models.query import QuerySet

register = template.Library()

@register.filter
def dice(dices: QuerySet, separator = " + "):
    return separator.join([d.__str__() for d in dices.all()]).upper()
