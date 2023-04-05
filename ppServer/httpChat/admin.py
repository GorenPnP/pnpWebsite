from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import *

class AccountInLineAdmin(admin.TabularInline):
    model = Chatroom.accounts.through

class MessageInLineAdmin(admin.TabularInline):
    model = Message
    fields = ["author", "text", "created_at"]
    readonly_fields = ["created_at"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).filter(type="m") # Message.choices[0][0] == is a message, not information or sth.



class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "spieler"]
    exclude = ["slug"]


class ChatroomAdmin(admin.ModelAdmin):

    list_display = ('titel', "_accounts")
    search_fields = ('titel', )

    inlines = [AccountInLineAdmin, MessageInLineAdmin]

    def _accounts(self, obj):
        return ", ".join([a.__str__() for a in obj.accounts.all()]) or "-"


admin.site.register(Account, AccountAdmin)
admin.site.register(Chatroom, ChatroomAdmin)