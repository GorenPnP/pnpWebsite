from django.contrib import admin
from django.db.models import Case, When
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import *


class CardAdmin(admin.ModelAdmin):

    list_display = ('account_name', 'account_owner', 'money', 'pay', 'active', 'has_char', 'id', "card_id")
    search_fields = ['char__name', 'char__eigentümer__name', 'name', 'spieler__name', 'id', "card_id"]
    list_filter = ['active']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("char__eigentümer", "spieler").annotate(has_char=Case(When(char=None, then=False), default=True))

    @admin.display(ordering="has_char", boolean=True, description="verbunden mit Charakter")
    def has_char(self, obj):
        return obj.has_char

    def pay(self, obj):
        return format_html('<a href="{0}">Bezahlen</a>'.format(reverse("cards:transaction", args=[obj.id]))) if obj.active else "-"


class TransactionAdmin(admin.ModelAdmin):
    change_list_template = "cards/admin/change_list_transaction.html"

    list_display = ('sender', 'receiver', 'amount', 'reason', 'timestamp')
    search_fields = ['sender__id', "sender__card_id", 'sender__name', "sender__spieler__name", "sender__char__name", "sender__char__eigentümer__name",
                     "receiver__id", "receiver__card_id", 'receiver__name', "receiver__spieler__name", "receiver__char__name", "receiver__char__eigentümer__name",
                     'amount', 'reason']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("sender__spieler", "sender__char__eigentümer", "receiver__spieler", "receiver__char__eigentümer")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Card, CardAdmin)
admin.site.register(Transaction, TransactionAdmin)
