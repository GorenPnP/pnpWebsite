from typing import Any
from django.contrib import admin, messages
from django.db.models import OuterRef
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from ppServer.utils import ConcatSubquery, get_filter

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


class KlasseStufenplanInLine(admin.TabularInline):
    model = KlasseStufenplan
    extra = 0





class SpielerAdmin(admin.ModelAdmin):
    fields = ["name", "geburtstag", "language"]
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
    list_filter = ['skilled_gfs__titel']

    @admin.display(ordering="skilled_gfsnames")
    def skilled_gfs_(self, obj):
        return obj.skilled_gfsnames or self.get_empty_value_display()

    def get_queryset(self, request):
        qs = Gfs.objects.filter(wesenkraft__id=OuterRef("id")).values("titel")

        return super().get_queryset(request).annotate(
            skilled_gfsnames = ConcatSubquery(qs, separator=", ")
        )


class SpezialfertigkeitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['titel', 'attr1', 'attr2']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    inlines = [SpezialAusgleichInLine]

    list_display = ('titel', 'attr1', 'attr2', 'fertigkeit_', 'beschreibung')
    list_filter = [
        get_filter(Attribut, "titel", ['attr1__titel', 'attr2__titel']),
        get_filter(Fertigkeit, "titel", ['ausgleich__titel']),
    ]
    search_fields = ['titel', 'attr1__titel', 'attr2__titel', "ausgleich__titel"]

    @admin.display(ordering="ausgleichnames")
    def fertigkeit_(self, obj):
        return obj.ausgleichnames

    def get_queryset(self, request):
        qs = Fertigkeit.objects.filter(spezialfertigkeit__id=OuterRef("id")).values("titel")

        return super().get_queryset(request).prefetch_related('attr1', 'attr2', "ausgleich").annotate(
            ausgleichnames = ConcatSubquery(qs, separator=", ")
        )


class WissensfertigkeitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['titel', 'attr1', 'attr2', 'attr3']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    inlines = [WissenFertInLine]

    list_display = ('titel', 'attr1', 'attr2', 'attr3', 'fertigkeit_', 'beschreibung')
    list_filter = [
        get_filter(Attribut, "titel", ["attr1__titel", "attr2__titel", "attr3__titel"]),
        get_filter(Fertigkeit, "titel", ["fertigkeit__titel"]),
    ]
    search_fields = ['titel', 'attr1__titel', 'attr2__titel', 'attr3__titel', 'fertigkeit__titel']

    @admin.display(ordering="fertigkeitnames")
    def fertigkeit_(self, obj):
        return obj.fertigkeitnames

    def get_queryset(self, request):
        qs = Fertigkeit.objects.filter(wissensfertigkeit__id=OuterRef("id")).values("titel")

        return super().get_queryset(request).prefetch_related('attr1', 'attr2', 'attr3').annotate(
            fertigkeitnames = ConcatSubquery(qs, separator=", ")
        )


class VorNachteilAdmin(admin.ModelAdmin):

    list_display = ('titel', 'ip', 'beschreibung', "has_implementation", "wann_wählbar", "is_sellable", "_max_amount", "needs_ip", "needs_attribut", "needs_fertigkeit", "needs_engelsroboter", "needs_notiz")
    list_editable = ("has_implementation",)
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
    list_display = ["titel", "tp", "beschreibung", "kategorie", "bedingung_", "has_implementation"]
    list_editable = ("has_implementation",)

    @admin.display(ordering="bedingungnames")
    def bedingung_(self, obj):
        return obj.bedingungnames or self.get_empty_value_display()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            bedingungnames = ConcatSubquery(Talent.objects.filter(id__in=OuterRef("bedingung")).values("titel"), ", ")
        )


class KlasseAdmin(admin.ModelAdmin):
    list_display = ["_icon", "titel", "beschreibung"]
    list_display_links = ["_icon", "titel"]
    search_fields = ["titel"]
    inlines = [KlasseStufenplanInLine]
    actions = ["create_stufenplans"]

    def _icon(self, obj):
        return format_html(f'<img src="{obj.icon.url}" style="max-width: 32px; max-height:32px;" />') if obj.icon else self.get_empty_value_display()

    @admin.action(description="Stufenpläne anlegen")
    def create_stufenplans(self, request, queryset):
        max_stufe = 30

        new_klassenstufenplans = []
        for klasse in queryset.prefetch_related("klassestufenplan_set"):
            existent_stufen = klasse.klassestufenplan_set.values_list("stufe", flat=True)
            for n in range(1, max_stufe+1):
                if n not in existent_stufen:
                    new_klassenstufenplans.append(KlasseStufenplan(stufe=n, klasse=klasse))

        KlasseStufenplan.objects.bulk_create(new_klassenstufenplans)
        messages.success(request, f"Stufenpläne aller Klassen bis Stufe {max_stufe} ergänzt")


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
admin.site.register(Klasse, KlasseAdmin)
admin.site.register(KlasseAbility)





# admin models of different files
admin.site.register(Charakter, CharakterAdmin)
admin.site.register(Gfs, GfsAdmin)
admin.site.register(GfsAbility, GfsAbilityAdmin)
admin.site.register(SkilltreeBase, admin.ModelAdmin)
admin.site.register(GfsSkilltreeEntry, GfsSkilltreeEntryAdmin)
admin.site.register(GfsStufenplanBase, GfsStufenplanBaseAdmin)
admin.site.register(GfsStufenplan, GfsStufenplanAdmin)