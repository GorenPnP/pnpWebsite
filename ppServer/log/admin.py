from django.contrib import admin

from shop.admin import hide_on_shop_angucken
from .models import *


class LogAdmin(hide_on_shop_angucken):
    list_display = ["char", "art", "notizen", "kosten", "spieler", "timestamp"]
    ordering = ["-timestamp", "char", "art"]

admin.site.register(Log, LogAdmin)
