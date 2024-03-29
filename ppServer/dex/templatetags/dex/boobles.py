from django import template

register = template.Library()


@register.inclusion_tag("dex/monster/booble.html", takes_context=True)
def base_booble(context):
    return {"amount": context["WEIGHT_BASE"], "extra_class": "booble--base"}

@register.inclusion_tag("dex/monster/booble.html", takes_context=True)
def trained_booble(context):
    return {"amount": context["WEIGHT_TRAINED"], "extra_class": "booble--trained"}

@register.inclusion_tag("dex/monster/booble.html", takes_context=True)
def skilled_booble(context):
    return {"amount": context["WEIGHT_SKILLED"], "extra_class": "booble--skilled"}