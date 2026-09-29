from django import template
from django.apps import apps
from django.urls import reverse

from ...models import BaseShop

register = template.Library()

@register.filter
def get_curr_price(item: BaseShop) -> int or None:
    FirmaShop = apps.get_model("shop", f"firma{item._meta.model_name}")
    prices = [fs.getPrice() for fs in FirmaShop.objects.filter(item=item)]
    return min(prices) if len(prices) else None