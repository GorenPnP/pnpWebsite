from django.contrib import admin

from push_notifications.models import APNSDevice, GCMDevice, WNSDevice

from .models import *

# unregister unused models from push_notifications
if admin.site.is_registered(APNSDevice): admin.site.unregister(APNSDevice)
if admin.site.is_registered(GCMDevice): admin.site.unregister(GCMDevice)
if admin.site.is_registered(WNSDevice): admin.site.unregister(WNSDevice)


# register own models
class PushSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', "chat", "news", "quiz", "changelog", "polls",)
    search_fields = ["user__username"]
    list_filter = ["chat", "news", "quiz", "changelog", "polls"]

    readonly_fields = ["user"]
    fieldsets = [
        (None, {'fields': ['user']}),
        ('Themen', {'fields': ["chat", "news", "quiz", "changelog", "polls"]})
    ]

admin.site.register(PushSettings, PushSettingsAdmin)