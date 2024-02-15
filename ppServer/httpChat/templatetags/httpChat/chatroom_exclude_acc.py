from django import template

from httpChat.models import Account, Chatroom

register = template.Library()


@register.filter
def get_avatar_urls(chat: Chatroom, exclude_account=None):
    return chat.get_avatar_urls(exclude_account)