from typing import Any
from django.contrib import admin
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest

from ppServer.utils import ConcatSubquery

from .models import *

class TopicAdmin(admin.ModelAdmin):

    exclude = ['width', 'height']
    list_display = ['titel', 'file_', 'beschreibung', 'sichtbarkeit_eingeschränkt']

    def file_(self, obj):
        return obj.filenames or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            filenames = ConcatSubquery(File.objects.filter(topic=OuterRef("id")).values("file"), ", ")
        )


admin.site.register(File)
admin.site.register(Topic, TopicAdmin)
