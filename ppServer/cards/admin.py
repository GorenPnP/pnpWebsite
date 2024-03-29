from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import *


class CardAdmin(admin.ModelAdmin):

    list_display = ('name', 'spieler', 'money', 'active', 'pay', 'id', "card_id")
    search_fields = ['name', 'spieler__name', 'id', "card_id"]
    list_filter = ['name', 'spieler', 'active']

    def pay(self, obj):
        return format_html('<a href="{0}">Bezahlen</a>'.format(reverse("cards:transaction", args=[obj.id]))) if obj.active else "-"


class TransactionAdmin(admin.ModelAdmin):
    change_list_template = "cards/admin/change_list_transaction.html"

    list_display = ('sender', 'receiver', 'amount', 'reason', 'timestamp')
    search_fields = ['sender__id', "sender__card_id", 'sender__name', "sender__spieler__name",
                     "receiver__id", "receiver__card_id", 'receiver__name', "receiver__spieler__name",
                     'amount', 'reason', 'timestamp']
    list_filter = ['sender', 'receiver']


    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Card, CardAdmin)
admin.site.register(Transaction, TransactionAdmin)
