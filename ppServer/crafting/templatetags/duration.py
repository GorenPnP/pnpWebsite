from django import template

register = template.Library()

@register.filter
def duration(td, smallest_is_minutes=True):
    # time intervals in seconds
    t_min = 60
    t_h = t_min * 60
    t_d = t_h * 24

    total_seconds = int(td.total_seconds())
    if smallest_is_minutes: total_seconds *= 60

    minutes = (total_seconds % t_h) // t_min
    hours = (total_seconds % t_d) // t_h
    days = total_seconds // t_d
    return '{} d {} h {} min'.format(days, hours, minutes)
