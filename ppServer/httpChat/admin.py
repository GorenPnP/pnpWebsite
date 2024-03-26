from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html

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
    list_display = ["_avatar", "name", "spieler"]
    list_display_links = ["_avatar", "name"]
    exclude = ["slug"]

    def _avatar(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px; border-radius:50%" />'.format(obj.avatar.url)) if obj.avatar else self.get_empty_value_display()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spieler")


class ChatroomAdmin(admin.ModelAdmin):

    list_display = ('titel', "_accounts")
    search_fields = ('titel', )

    inlines = [AccountInLineAdmin, MessageInLineAdmin]

    def _accounts(self, obj):
        return obj.accountsnames or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            accountsnames = ConcatSubquery(Account.objects.filter(chatroom=OuterRef("id")).values("name"), ", ")
        )


admin.site.register(Account, AccountAdmin)
admin.site.register(Chatroom, ChatroomAdmin)