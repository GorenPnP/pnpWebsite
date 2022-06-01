from django.contrib import admin

from .models import *


class NewCharakterAttributInLine(admin.TabularInline):
    model = NewCharakterAttribut
    extra = 0


class NewCharakterFertInLine(admin.TabularInline):
    model = NewCharakterFertigkeit
    extra = 0


class NewCharakterVorteilInLine(admin.TabularInline):
    model = NewCharakterVorteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 0


class NewCharakterNachteilInLine(admin.TabularInline):
    model = NewCharakterNachteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 0


class NewCharakterSpezialfertigkeitInLine(admin.TabularInline):
    model = NewCharakterSpezialfertigkeit
    extra = 0


class NewCharakterWissensfertigkeitInLine(admin.TabularInline):
    model = NewCharakterWissensfertigkeit
    extra = 0


class NewCharakterTalentInLine(admin.TabularInline):
    model = NewCharakterTalent
    extra = 0


class NewCharakterZauberInLine(admin.TabularInline):
    model = NewCharakterZauber
    extra = 0


class NewCharakterAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Settings (Finger weg)", {'fields': ['eigentümer', "ep_system", "larp", "gfs", "profession"]}),
        ("Aus der Prioritätentabelle", {"fields": ["zauber", "ap", "sp", "konzentration", "fp", "fg", "geld", "ip", "spF_wF"]}),
    ]

    list_display = ["eigentümer", "gfs", "profession", "ip", 'ap', 'sp', "konzentration", "fp", "fg", "geld", "zauber", "spF_wF", "larp"]
    inlines = [NewCharakterAttributInLine, NewCharakterFertInLine,
               NewCharakterVorteilInLine, NewCharakterNachteilInLine,
               NewCharakterSpezialfertigkeitInLine, NewCharakterWissensfertigkeitInLine,
               NewCharakterTalentInLine,
               NewCharakterZauberInLine
               ]

    def get_queryset(self, request):
        if request.user.groups.filter(name__iexact="spieler"):
            return NewCharakter.objects.filter(eigentümer__name__exact=request.user.username)
        else:
            return super().get_queryset(request)


class GfsCharacterizationAdmin(admin.ModelAdmin):
    list_display = ['gfs', 'state', 'social', 'magical', 'can_punch', 'can_shoot', 'gets_pricy_skills', 'can_fly', 'attitude']
    list_editable = ['state', 'social', 'magical', 'can_punch', 'can_shoot', 'gets_pricy_skills', 'can_fly', 'attitude']

class PriotableAdmin(admin.ModelAdmin):
    list_display = ['priority', 'ip', 'ap', 'sp', 'konzentration', 'fp', 'fg', 'zauber', 'drachmen', 'spF_wF']
    list_editable = ['ip', 'ap', 'sp', 'konzentration', 'fp', 'fg', 'zauber', 'drachmen', 'spF_wF']


admin.site.register(NewCharakter, NewCharakterAdmin)
admin.site.register(Priotable, PriotableAdmin)
admin.site.register(GfsCharacterization, GfsCharacterizationAdmin)
