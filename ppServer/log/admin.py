from django.contrib import admin

from .models import *


class LogAdmin(admin.ModelAdmin):
    list_display = ["char", "art", "notizen", "kosten", "spieler", "timestamp"]
    ordering = ["-timestamp", "char", "art"]

admin.site.register(Log, LogAdmin)
