from django.contrib import admin

from .models import *

class LevelAdmin(admin.ModelAdmin):
	list_display = ["name", "width", "height"]


admin.site.register(Level, LevelAdmin)