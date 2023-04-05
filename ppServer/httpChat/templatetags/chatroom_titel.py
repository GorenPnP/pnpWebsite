from django import template

from ..models import Account, Chatroom

register = template.Library()


@register.filter
def titel(chat: Chatroom, exclude_account: Account=None):
    return chat.get_titel(exclude_account)