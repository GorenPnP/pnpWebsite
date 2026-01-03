from django import template

register = template.Library()

@register.filter
def vote(qs: list, outcome: str):
    max = 0
    curr = 0
    for vote in qs:
        max += 1
        if vote["vote"] == outcome: curr += 1

    return  "{:.1f}".format(100.0 * curr / max)