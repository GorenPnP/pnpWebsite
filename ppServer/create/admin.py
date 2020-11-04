from django.contrib import admin

from shop.admin import hide_on_shop_angucken
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


class NewCharakterAdmin(hide_on_shop_angucken):
    fieldsets = [
        ("Settings (Finger weg)", {'fields': ['eigentümer', "ep_system", "larp", "gfs", "profession"]}),
        ("Aus der Prioritätentabelle", {"fields": ["zauber", "ap", "sp", "fp", "fg", "geld", "ip"]}),
        ]

    list_display = ["eigentümer", "gfs", "profession", "ip", 'ap', 'sp', "fp", "fg", "geld", "zauber", "larp"]
    inlines = [NewCharakterAttributInLine, NewCharakterFertInLine,
               NewCharakterVorteilInLine, NewCharakterNachteilInLine,
               NewCharakterSpezialfertigkeitInLine, NewCharakterWissensfertigkeitInLine,
               NewCharakterTalentInLine,
               NewCharakterZauberInLine
               ]

    def get_queryset(self, request):
        if request.user.groups.filter(name__iexact="shop angucken"):
            return NewCharakter.objects.filter(eigentümer__name__exact=request.user.username)
        else:
            return super().get_queryset(request)


admin.site.register(NewCharakter, NewCharakterAdmin)
