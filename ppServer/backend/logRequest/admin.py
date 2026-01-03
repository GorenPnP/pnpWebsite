from django.contrib import admin
from django.utils.html import format_html

from .models import Request

class RequestAdmin(admin.ModelAdmin):
    list_display = ['zeit', 'methode', '_pfad', 'user', 'antwort', 'user_agent']
    list_display_links = ["zeit"]

    def _pfad(self, obj):
        return format_html('<a href="{0}">{0}</a>'.format(obj.pfad))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Request, RequestAdmin)