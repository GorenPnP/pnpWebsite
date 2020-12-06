from django.contrib import admin

from .models import *


class StoryAdmin(admin.ModelAdmin):
    list_display = ['titel', 'file_', 'beschreibung']

    def file_(self, obj):
        return ', '.join([f.file.name for f in obj.files.all()])


class MapAdmin(admin.ModelAdmin):

    exclude = ['width', 'height']
    list_display = ['titel', 'file_', 'beschreibung']

    def file_(self, obj):
        return ', '.join([f.file.name for f in obj.files.all()])


class FileAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return File.objects.filter(show_in_admin=True)


admin.site.register(File, FileAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Map, MapAdmin)
