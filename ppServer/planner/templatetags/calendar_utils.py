from datetime import date
from random import randint, random

from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.simple_tag
def concat_all(*args):
    """concatenate all args"""
    return ''.join(map(str, args))

@register.filter
@stringfilter
def is_past(iso_date: str, specific_date: date = date.today()) -> bool:
    return date.fromisoformat(iso_date) < specific_date

@register.filter
@stringfilter
def is_future(iso_date: str, specific_date: date = date.today()) -> bool:
    return date.fromisoformat(iso_date) > specific_date

@register.filter
@stringfilter
def is_same_day(iso_date: str, specific_date: date = date.today()) -> bool:
    return date.fromisoformat(iso_date) == specific_date

@register.filter
def isoformat(date_obj: date) -> str:
    return date_obj.isoformat()


@register.filter
@stringfilter
def day_state(iso_date: str) -> str:
    date.fromisoformat(iso_date) < date.today()

    states = ["", "", "", "blocked", "open", "half", "full"]
    
    return states[randint(0, len(states)-1)]


@register.filter
@stringfilter
def leading_zeros(value: str, desired_digits: int) -> str:
    return value.zfill(desired_digits)