from django import template
from django.apps import apps
from django.urls import reverse

from ...models import BaseShop

register = template.Library()

@register.filter
def get_detail_url(item: BaseShop) -> str:
    return reverse('shop:detail', args=[item._meta.model, item.pk])
