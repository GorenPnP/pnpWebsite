from django import template

from ..models import Account, Chatroom

register = template.Library()


@register.filter
def titel(chat: Chatroom, exclude_account: Account=None):
    return chat.get_titel(exclude_account)

@register.filter
def get_avatar_urls(chat: Chatroom, exclude_account=None):
    return chat.get_avatar_urls(exclude_account)