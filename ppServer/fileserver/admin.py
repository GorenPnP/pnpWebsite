from django.contrib import admin

from .models import *

class TopicAdmin(admin.ModelAdmin):

    exclude = ['width', 'height']
    list_display = ['titel', 'file_', 'beschreibung', 'sichtbarkeit_eingeschränkt']

    def file_(self, obj):
        return ', '.join([f.file.name for f in obj.files.all()])


class FileAdmin(admin.ModelAdmin):
    pass


admin.site.register(File, FileAdmin)
admin.site.register(Topic, TopicAdmin)
