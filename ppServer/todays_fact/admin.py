from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Fact, History

class HistoryAdmin(admin.ModelAdmin):
    list_display = ("date", "fact")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("fact")

# Register your models here.
admin.site.register(Fact)
admin.site.register(History, HistoryAdmin)
