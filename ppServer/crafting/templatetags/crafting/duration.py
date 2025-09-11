from datetime import timedelta

from django import template
from django.utils.duration import _get_duration_components

register = template.Library()

@register.filter
def duration(td: timedelta):
    days, hours, minutes, seconds, microseconds = _get_duration_components(td)
    return f"{days} Tage {hours:02d} h {minutes:02d} min" if days else f"{hours:02d} h {minutes:02d} min"
