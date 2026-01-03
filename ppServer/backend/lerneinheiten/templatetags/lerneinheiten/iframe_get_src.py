from django import template

from django.utils.html import format_html

register = template.Library()

@register.filter
def iframe_get_src(iframe: str):
    for parts in iframe.split(" "):
        if parts.startswith("src"):
            return parts[5:-1]