from django.contrib import admin


from .admin_models.character import CharakterAdmin
from .admin_models.gfs import *
from .models import *



class WesenkraftZusatzWesenspInLine(admin.TabularInline):
    model = Wesenkraft.skilled_gfs.through
    extra = 1


class SpezialAusgleichInLine(admin.TabularInline):
    model = Spezialfertigkeit.ausgleich.through
    extra = 1


class WissenFertInLine(admin.TabularInline):
    model = Wissensfertigkeit.fertigkeit.through
    extra = 1





class SpielerAdmin(admin.ModelAdmin):
    fields = ["name", "geburtstag"]
    list_display = ["name", "geburtstag"]




class WesenAdmin(admin.ModelAdmin):
    list_display = ('komplexität', 'titel',)
    search_fields = ('komplexität', 'titel',)


class PersönlichkeitAdmin(admin.ModelAdmin):
    list_display = ('titel', 'positiv', 'negativ')
    search_fields = ('titel', 'positiv', 'negativ')


class AttributAdmin(admin.ModelAdmin):
    list_display = ('titel', 'beschreibung')
    search_fields = ['titel', 'beschreibung']


class FertigkeitAdmin(admin.ModelAdmin):

    list_display = ('titel', 'attribut', 'gruppe', 'impro_possible', 'limit', 'beschreibung')
    search_fields = ['titel', 'attribut__titel', 'limit']
    list_filter = ['attribut', 'gruppe', 'impro_possible', 'limit']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribut')


class WesenkraftAdmin(admin.ModelAdmin):

    fields = ['titel', 'probe', 'wirkung', 'manaverbrauch', "skilled_gfs"]
    inlines = [WesenkraftZusatzWesenspInLine]

    list_display = ['titel', 'probe', 'manaverbrauch', 'wirkung', 'skilled_gfs_']
    search_fields = ['titel', 'skilled_gfs']
    list_filter = ['skilled_gfs']

    def skilled_gfs_(self, obj):
        return ", ".join([gfs.titel for gfs in obj.skilled_gfs.all()])

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('skilled_gfs')


class SpezialfertigkeitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['titel', 'attr1', 'attr2']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    inlines = [SpezialAusgleichInLine]

    list_display = ('titel', 'attr1', 'attr2', 'ausgleich_', 'beschreibung')
    list_filter = ['attr1', 'attr2', 'ausgleich']
    search_fields = ['titel', 'attr1__titel', 'attr2__titel']

    def ausgleich_(self, obj):
        return ', '.join([a.titel for a in obj.ausgleich.all()])

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attr1', 'attr2', 'ausgleich')


class WissensfertigkeitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['titel', 'attr1', 'attr2', 'attr3']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    inlines = [WissenFertInLine]

    list_display = ('titel', 'attr1', 'attr2', 'attr3', 'fertigkeit_', 'beschreibung')
    list_filter = ['attr1', 'attr2', 'attr3', 'fertigkeit']
    search_fields = ['titel', 'attr1__titel', 'attr2__titel', 'attr3__titel']

    def fertigkeit_(self, obj):
        return ', '.join([a.titel for a in obj.fertigkeit.all()])

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attr1', 'attr2', 'attr3', 'fertigkeit')


class VorNachteilAdmin(admin.ModelAdmin):

    list_display = ('titel', 'ip', 'beschreibung', "needs_implementation", "has_implementation", "wann_wählbar", "is_sellable", "_max_amount", "needs_ip", "needs_attribut", "needs_fertigkeit", "needs_engelsroboter", "needs_notiz")
    list_editable = ("needs_implementation", "has_implementation")
    list_filter = ['ip', "wann_wählbar"]
    search_fields = ['titel', 'ip', "wann_wählbar"]

    def _max_amount(self, obj):
        return obj.max_amount or "unbegrenzt"


class BerufAdmin(admin.ModelAdmin):
    list_display = ['titel', 'beschreibung']
    search_fields = ['titel']
    list_filter = ['titel']


class ReligionAdmin(admin.ModelAdmin):
    list_display = ['titel', 'beschreibung']
    search_fields = ['titel']
    list_filter = ['titel']


class TalentAdmin(admin.ModelAdmin):
    list_display = ["titel", "tp", "beschreibung", "kategorie", "bedingung_"]

    def bedingung_(self, obj):
        return ", ".join([t.titel for t in obj.bedingung.all()])


admin.site.register(Spieler, SpielerAdmin)

admin.site.register(Wesen, WesenAdmin)
admin.site.register(Persönlichkeit, PersönlichkeitAdmin)

admin.site.register(Attribut, AttributAdmin)
admin.site.register(Fertigkeit, FertigkeitAdmin)
admin.site.register(Wesenkraft, WesenkraftAdmin)
admin.site.register(Spezialfertigkeit, SpezialfertigkeitAdmin)
admin.site.register(Religion, ReligionAdmin)
admin.site.register(Beruf, BerufAdmin)
admin.site.register(Nachteil, VorNachteilAdmin)
admin.site.register(Vorteil, VorNachteilAdmin)
admin.site.register(Wissensfertigkeit, WissensfertigkeitAdmin)

admin.site.register(Talent, TalentAdmin)





# admin models of different files
admin.site.register(Charakter, CharakterAdmin)
admin.site.register(Gfs, GfsAdmin)
admin.site.register(GfsAbility, GfsAbilityAdmin)
admin.site.register(SkilltreeBase, admin.ModelAdmin)
admin.site.register(GfsSkilltreeEntry, GfsSkilltreeEntryAdmin)
admin.site.register(GfsStufenplanBase, GfsStufenplanBaseAdmin)