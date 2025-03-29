from datetime import timedelta

from django import template
from django.utils.duration import duration_string

register = template.Library()

@register.filter
def duration(td: timedelta):
    return duration_string(td) + " [dd ]hh:mm:ss[.6microseconds]"

