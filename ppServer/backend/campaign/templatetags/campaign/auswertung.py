from django import template
from django.forms import Form
from django.utils.html import format_html

from character.models import Charakter
from log.create_log import render_number

register = template.Library()

@register.filter
def stats_of(char: Charakter, form: Form):

    result = ""
    for field in form:

        # get char's value
        name = field.name
        if not hasattr(char, name): continue
        val = getattr(char, name)

        # .. is numeric
        if name != "zauberplätze":
            result += f"<p><b>{render_number(int(val))}</b> {field.label.replace(':', '')}</p>"
        
        # .. is zauberplätze
        else:
            val = val or {}
            if not val:
                result += f"<p><b>0</b> {field.label.replace(':', '')}</p>"
                continue

            val = "<br>".join([f"<b>{amount} Stufe {stufe}</b> Zauber" for stufe, amount in val.items()])
            result += f"<p>{val}</p>"

    return format_html(result)
