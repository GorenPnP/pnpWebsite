from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import *

class ChangelogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "_text"]

    @admin.display(ordering="text_rendered")
    def _text(self, obj):
        return format_html(obj.text_rendered)

    
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.spieler.is_spielleitung

admin.site.register(Changelog, ChangelogAdmin)
