from django import template

from dex.monster.models import Typ

register = template.Library()

@register.filter
def attack_strength(type: Typ):
    return type.stark_gegen.count() - type.schwach_gegen.count() - 2* type.trifft_nicht.count()

@register.filter
def def_strength(type: Typ):
    return -1* type.stark.count() + type.schwach.count() + 2* type.miss.count()
