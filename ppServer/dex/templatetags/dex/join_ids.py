from django import template

register = template.Library()

@register.filter
def join_ids(id1: any, id2: any):
    return "-".join([str(id1), str(id2)])
