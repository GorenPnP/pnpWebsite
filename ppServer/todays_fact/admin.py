from django.contrib import admin

from .models import Fact, History

class HistoryAdmin(admin.ModelAdmin):
    list_display = ("date", "fact")

# Register your models here.
admin.site.register(Fact)
admin.site.register(History, HistoryAdmin)
