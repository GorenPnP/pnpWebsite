from time_space.models.net import Net
from django.contrib import admin

class NetAdmin(admin.ModelAdmin):
	fields = ["text"]


admin.site.register(Net, NetAdmin)
