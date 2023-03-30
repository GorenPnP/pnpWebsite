from typing import Any, Optional

from django.contrib import admin
from django.http.request import HttpRequest

from .models import *

class MessageInLineAdmin(admin.TabularInline):
    model = Message
    
    # def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
    #     return False
    
    # def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = ...) -> bool:
    #     return False
    
    # def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = ...) -> bool:
    #     return False


class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "spieler"]
    exclude = ["slug"]


class ChatroomAdmin(admin.ModelAdmin):

    list_display = ('titel', "_owners", "_admins", "_basic_users")
    search_fields = ('titel', )
    exclude = ["slug"]

    inlines = [MessageInLineAdmin]

    def _owners(self, obj):
        return ", ".join([a.__str__() for a in obj.owners.all()]) or "-"
    def _admins(self, obj):
        return ", ".join([a.__str__() for a in obj.admins.all()]) or "-"
    def _basic_users(self, obj):
        return ", ".join([a.__str__() for a in obj.basic_users.all()]) or "-"


admin.site.register(Account, AccountAdmin)
admin.site.register(Chatroom, ChatroomAdmin)