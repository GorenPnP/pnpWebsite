from math import floor

from django import template

register = template.Library()

@register.filter
def calc_stat(stat: int):
    return floor(stat / 5.0)