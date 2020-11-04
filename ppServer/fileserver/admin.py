from django.contrib import admin

from .models import *
from shop.admin import hide_on_shop_angucken


class StoryAdmin(hide_on_shop_angucken):
    list_display = ['titel', 'file_', 'beschreibung']

    def file_(self, obj):
        return ', '.join([f.file.name for f in obj.files.all()])


class MapAdmin(hide_on_shop_angucken):

    exclude = ['width', 'height']
    list_display = ['titel', 'file_', 'beschreibung']

    def file_(self, obj):
        return ', '.join([f.file.name for f in obj.files.all()])


class FileAdmin(hide_on_shop_angucken):

    def get_queryset(self, request):
        return File.objects.filter(show_in_admin=True)


admin.site.register(File, FileAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Map, MapAdmin)
