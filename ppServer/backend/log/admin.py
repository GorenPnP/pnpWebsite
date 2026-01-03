from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import *

class LogAdmin(admin.ModelAdmin):
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("char", "spieler")

admin.site.register(Log, LogAdmin)