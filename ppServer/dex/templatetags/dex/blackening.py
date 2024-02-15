from random import randint

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def blackening():
    """
    generates 1-5 divs with class 'blackening'.
    sample-style:
        .blackening {background-color: black; color: transparent; height: 1em; margin-block: .5em;}
    
    """
    lines = [f"<div class='blackening' style='width: {randint(1, 100)}%'></div>" for _ in range(randint(1, 5))]
    return format_html("".join(lines))