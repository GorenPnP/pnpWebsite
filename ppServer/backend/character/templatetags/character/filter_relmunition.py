from django import template
from django.db.models import QuerySet, Q

from ...models.relshop import RelMunition, RelFernkampfwaffe

register = template.Library()

@register.filter
def filterRelMunition(rels: QuerySet[RelMunition], relFernkampfwaffe: RelFernkampfwaffe) -> QuerySet[RelMunition]:
    return rels.filter(Q(char=relFernkampfwaffe.char) & Q(item__pk__in=relFernkampfwaffe.item.munition.all()))