from django import template

from ...models import Charakter, Tag

register = template.Library()

@register.filter
def hasTag(char: Charakter, tag: Tag) -> bool:
    return tag.id in [tag.id for tag in char.tags.all()]