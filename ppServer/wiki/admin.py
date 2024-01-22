from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import *

class RuleAdmin(admin.ModelAdmin):
    list_display = ["nr", "titel", "_text"]
    list_editable = ["nr"]
    list_display_links = ["titel"]

    def _text(self, obj):
        return format_html(obj.text_rendered)

    
    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.groups.filter(name__iexact="spielleiter").exists()

admin.site.register(Rule, RuleAdmin)
