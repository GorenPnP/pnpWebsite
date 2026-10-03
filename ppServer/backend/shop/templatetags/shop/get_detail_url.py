from django import template
from django.apps import apps
from django.urls import reverse

from ...models import BaseShop

register = template.Library()

@register.filter
def get_detail_url(item: BaseShop, view: str = "shop:detail") -> str:
    if item.frei_editierbar:
        return reverse('admin:shop_{}_change'.format(item._meta.model_name), args=(item.pk,))

    return reverse(view, args=[item._meta.model, item.pk])
