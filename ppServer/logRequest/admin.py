from django.contrib import admin

from .models import Request

class RequestAdmin(admin.ModelAdmin):
    list_display = ['zeit', 'methode', 'pfad', 'user', 'antwort', 'user_agent']
    list_display_links = ["zeit", "pfad"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Request, RequestAdmin)