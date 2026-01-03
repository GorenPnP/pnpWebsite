from django.contrib import admin

from .models import *


class GfsCharacterizationAdmin(admin.ModelAdmin):
    list_display = ['gfs', 'state', 'social', 'magical', 'can_punch', 'can_shoot', 'gets_pricy_skills', 'can_fly', 'attitude']
    list_editable = ['state', 'social', 'magical', 'can_punch', 'can_shoot', 'gets_pricy_skills', 'can_fly', 'attitude']

class PriotableAdmin(admin.ModelAdmin):
    list_display = ['priority', 'cost', 'ip', 'ap', 'sp', 'konzentration', 'fp', 'fg', 'zauber', 'drachmen', 'spF_wF']
    list_editable = ['cost', 'ip', 'ap', 'sp', 'konzentration', 'fp', 'fg', 'zauber', 'drachmen', 'spF_wF']


admin.site.register(Priotable, PriotableAdmin)
admin.site.register(GfsCharacterization, GfsCharacterizationAdmin)
