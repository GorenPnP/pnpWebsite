from typing import Any

from django.db.models import Q
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import *


class WesenkraftZusatzWesenspInLine(admin.TabularInline):
    model = Wesenkraft.skilled_gfs.through
    extra = 1


class GfsImageInLine(admin.TabularInline):
    model = GfsImage
    fields = ["order", "img", "text"]
    extra = 1

class GfsAttributInLine(admin.TabularInline):
    model = GfsAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribut')


class GfsFertigkeitInLine(admin.TabularInline):
    model = GfsFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('fertigkeit')


class GfsVorteilInLine(admin.TabularInline):
    model = GfsVorteil
    extra = 1


class GfsNachteilInLine(admin.TabularInline):
    model = GfsNachteil
    extra = 1


class GfsWesenkraftInLine(admin.TabularInline):
    model = GfsWesenkraft
    extra = 1


class GfsZauberInLine(admin.TabularInline):
    model = GfsZauber
    extra = 1


class GfsStufenplanInLine(admin.TabularInline):
    model = GfsStufenplan
    fields = ["basis", "vorteile", "zauber", "wesenkräfte", "ability"]
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('basis', 'vorteile', 'wesenkräfte', 'ability')


class SpezialAusgleichInLine(admin.TabularInline):
    model = Spezialfertigkeit.ausgleich.through
    extra = 1


class WissenFertInLine(admin.TabularInline):
    model = Wissensfertigkeit.fertigkeit.through
    extra = 1


class RelPersönlichkeitInline(admin.TabularInline):
    model = RelPersönlichkeit
    extra = 1


class RelAttributInline(admin.TabularInline):
    fields = ['attribut', 'aktuellerWert', 'aktuellerWert_temp', 'aktuellerWert_bonus', 'maxWert', 'maxWert_temp']
    readonly_fields = ['attribut']
    model = RelAttribut
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribut')


class RelGruppeInLine(admin.TabularInline):
    fields = ['gruppe', 'fg', "fg_temp"]
    readonly_fields = ['gruppe']
    model = RelGruppe
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RelFertigkeitInLine(admin.TabularInline):
    fields = ['fertigkeit', 'fp', "fp_temp", 'fp_bonus']
    readonly_fields = ['fertigkeit']
    model = RelFertigkeit
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('fertigkeit')


class RelWesenkraftInLine(admin.TabularInline):
    model = RelWesenkraft
    extra = 1


class RelSpezialfertigkeitInLine(admin.TabularInline):
    model = RelSpezialfertigkeit
    extra = 1


class RelWissensfertigkeitInLine(admin.TabularInline):
    model = RelWissensfertigkeit
    extra = 1


class AffektivitätInLine(admin.TabularInline):
    model = Affektivität
    extra = 1
    exclude = ['grad', 'umgang']


class RelGfsAbilityInLine(admin.TabularInline):
    model = RelGfsAbility
    fields = ["ability", "notizen"]
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('ability')


class RelVorteilInLine(admin.TabularInline):
    model = RelVorteil
    fields = ["teil", "attribut", "fertigkeit", "engelsroboter", "notizen", "ip", "is_sellable", "will_create"]
    exclude = ["anzahl"]
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit', 'engelsroboter')


class RelNachteilInLine(admin.TabularInline):
    model = RelNachteil
    fields = ["teil", "attribut", "fertigkeit", "notizen", "ip", "is_sellable", "will_create"]
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit')
    

class RelTalentInLine(admin.TabularInline):
    model = RelTalent
    fields = ["talent"]
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('talent')

########## generic (st)shop ##############

class RelShopInLine(admin.TabularInline):
    extra = 1
    fields = ["anz", "item", "notizen"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('item')


################## Shop ############################

class RelItemlInLine(RelShopInLine):
    model = RelItem


class RelWaffen_WerkzeugelInLine(RelShopInLine):
    model = RelWaffen_Werkzeuge


class RelMagazinInLine(RelShopInLine):
    model = RelMagazin


class RelPfeil_BolzenInLine(RelShopInLine):
    model = RelPfeil_Bolzen


class RelSchusswaffenInLine(RelShopInLine):
    model = RelSchusswaffen


class RelMagische_AusrüstungInLine(RelShopInLine):
    model = RelMagische_Ausrüstung


class RelRituale_RunenInLine(RelShopInLine):
    model = RelRituale_Runen
    fields = ["anz", "stufe", "item", "notizen"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('item')


class RelRüstungInLine(RelShopInLine):
    model = RelRüstung


class RelAusrüstung_TechnikInLine(RelShopInLine):
    model = RelAusrüstung_Technik
    fields = ["anz", "item", "notizen", "selbst_eingebaut"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('item')


class RelFahrzeugInLine(RelShopInLine):
    model = RelFahrzeug


class RelEinbautenInLine(RelShopInLine):
    model = RelEinbauten


class RelZauberInLine(RelShopInLine):
    fields = fields = ["anz", "item", "tier", "notizen"]
    model = RelZauber

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('item')


class RelVergessenerZauberInLine(RelShopInLine):
    model = RelVergessenerZauber


class RelAlchemieInLine(RelShopInLine):
    model = RelAlchemie


class RelTinkerInLine(RelShopInLine):
    model = RelTinker


class RelBegleiterInLine(RelShopInLine):
    model = RelBegleiter


class RelEngelsroboterInLine(RelShopInLine):
    model = RelEngelsroboter



class CharakterAdmin(admin.ModelAdmin):

    class Meta:
        model = Charakter

    fieldsets = [
        ("Settings (Finger weg)", {'fields': ['eigentümer', "in_erstellung", "larp", "gfs"]}),
        ('Roleplay', {'fields': ['image', 'name', "gewicht", "größe", 'alter', 'geschlecht', 'sexualität', 'beruf', "präf_arm",
                              'religion', "hautfarbe", "haarfarbe", "augenfarbe"]}),
        
        ("Manifest", {"fields": ["manifest", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust"]}),
        ('HP', {'fields': ['rang', 'larp_rang', 'HPplus', 'HPplus_fix', 'HPplus_geistig']}),
        ('Kampf', {'fields': ['wesenschaden_waff_kampf', 'wesenschaden_andere_gestalt', 'crit_attack', 'crit_defense',
                              'initiative_bonus', 'reaktion_bonus', 'natürlicher_schadenswiderstand_bonus', 'astralwiderstand_bonus']}),

        ('Kampagne', {'fields': ["ep", 'ep_stufe', 'ep_stufe_in_progress', "skilltree_stufe", "processing_notes"]}),
        ('Währungen', {'fields': ['ap', 'fp', 'fg', 'sp', 'ip', 'tp', 'spF_wF', 'wp', 'zauberplätze', "geld", 'konzentration', "prestige", "verzehr"]}),
        ('Geschreibsel', {'fields': ['notizen', 'persönlicheZiele', 'sonstige_items']}),
    ]

    inlines = [
               RelPersönlichkeitInline,
               RelWesenkraftInLine,
               RelAttributInline,
               RelGruppeInLine,
               RelFertigkeitInLine,
               RelSpezialfertigkeitInLine,
               RelWissensfertigkeitInLine, RelVorteilInLine,
               RelNachteilInLine, RelTalentInLine,
               AffektivitätInLine,
               RelGfsAbilityInLine,

               RelItemlInLine,
               RelWaffen_WerkzeugelInLine,
               RelMagazinInLine,
               RelPfeil_BolzenInLine,
               RelSchusswaffenInLine,
               RelMagische_AusrüstungInLine,
               RelRituale_RunenInLine,
               RelRüstungInLine,
               RelAusrüstung_TechnikInLine,
               RelFahrzeugInLine,
               RelEinbautenInLine,
               RelZauberInLine,
               RelVergessenerZauberInLine,
               RelAlchemieInLine,
               RelTinkerInLine,
               RelBegleiterInLine,
               RelEngelsroboterInLine
    ]

    list_display = ['image_', 'name', 'eigentümer', "gfs", "larp", "in_erstellung"]

    list_filter = ['in_erstellung', 'larp', 'eigentümer']
    search_fields = ['name', 'eigentümer__name']
    list_display_links = ["name"]

    save_on_top = True


    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"


    # utils for groups

    def _is_spielleiter_or_adds_chars(self, request):
        return request.user.groups.filter(name__in=["spielleiter", "trägt seine chars ein"]).exists()

    def _only_adds_chars(self, request):
        request.user.groups.filter(~Q(name="spielleiter") & Q(name="trägt seine chars ein")).exists()

    # permissions

    def has_add_permission(self, request: HttpRequest) -> bool:
        return self._is_spielleiter_or_adds_chars(request) and super().has_add_permission(request)

    def has_change_permission(self, request: HttpRequest, obj = ...) -> bool:
        return self._is_spielleiter_or_adds_chars(request) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj = ...) -> bool:
        return request.user.groups.filter(name="spielleiter").exists() and super().has_delete_permission(request, obj)

    def has_view_permission(self, request: HttpRequest, obj = ...) -> bool:
        return self._is_spielleiter_or_adds_chars(request) and super().has_view_permission(request, obj)
    

    # specials for "trägt seine chars ein"-group

    # display only own chars if user has "trägt seine chars ein"-group
    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('eigentümer', "gfs__wesen")

        if self._only_adds_chars(request): return qs.filter(eigentümer__name=request.user.username)
        return qs
    
    # set "eigentümer" to readonly if user has the "trägt seine chars ein"-group
    def get_readonly_fields(self, request: HttpRequest, obj: Any or None = ...) -> list[str] or tuple[Any, ...]:
        fields = list(super().get_readonly_fields(request, obj))

        if not self._only_adds_chars(request): return fields
        return fields + ["eigentümer"]
    
    # set "eigentümer" to logged-in-user if user has the "trägt seine chars ein"-group
    def save_form(self, request: Any, form: Any, change: Any) -> Any:
        char = super().save_form(request, form, change)

        if self._adds_own_chars(request):
            spieler = get_object_or_404(Spieler, name=request.user.username)
            char.eigentümer = spieler
            char.save()
        return char


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


class SpeziesAdmin(admin.ModelAdmin):
    list_display = ('komplexität', 'titel',)
    search_fields = ('komplexität', 'titel',)

class GfsAdmin(admin.ModelAdmin):
    list_display = ('icon_', 'titel', 'ap', "wesen", 'difficulty', 'vorteil_', 'nachteil_', 'zauber_',
                    "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "wesenkraft_", "startmanifest",)
    list_filter = ["wesen", 'ap', 'startmanifest', "wesenschaden_waff_kampf"]
    search_fields = ('titel', 'ap')

    list_editable = ["wesen", 'wesenschaden_waff_kampf', 'wesenschaden_andere_gestalt', 'difficulty']
    list_display_links = ["icon_", "titel"]

    inlines = [GfsImageInLine, GfsAttributInLine, GfsFertigkeitInLine,
               GfsVorteilInLine, GfsNachteilInLine,
               GfsWesenkraftInLine, GfsZauberInLine,
               GfsStufenplanInLine]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('nachteile', 'vorteile', 'wesenkraft', 'gfszauber_set__item')
    
    def icon_(self, obj):
        return format_html(f'<img src="{obj.icon.url}" style="max-width: 32px; max-height:32px;" />' if obj.icon else "-")

    def vorteil_(self, obj):
        return ', '.join([a.titel for a in obj.vorteile.all()]) or None

    def nachteil_(self, obj):
        return ', '.join([a.titel for a in obj.nachteile.all()]) or None

    def zauber_(self, obj):
        return ', '.join([a.item.name for a in obj.gfszauber_set.all()]) or None

    def wesenkraft_(self, obj):
        return ', '.join([a.titel for a in obj.wesenkraft.all()]) or None


class GfsAbilityAdmin(admin.ModelAdmin):
    list_display = ("name", "beschreibung", "needs_implementation", "has_choice")
    list_editable = ["needs_implementation", "has_choice"]

    search_fields = ("name", "beschreibung")


class PersönlichkeitAdmin(admin.ModelAdmin):
    list_display = ('titel', 'positiv', 'negativ')
    search_fields = ('titel', 'positiv', 'negativ')


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


class SpielerAdmin(admin.ModelAdmin):
    #readonly_fields = ["name"]
    fields = ["name", "geburtstag"]
    list_display = ["name", "geburtstag"]


class SkilltreeEntryWesenAdmin(admin.ModelAdmin):
    list_display = ["wesen", "context"]
    list_filter = ["wesen", "context"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('wesen')


class GfsStufenplanBaseAdmin(admin.ModelAdmin):
    list_display = ["stufe", "ep", "ap", "fp", "fg", "tp"]
    list_editable = ["ep", "ap", "fp", "fg", "tp"]


class TalentAdmin(admin.ModelAdmin):
    list_display = ["titel", "tp", "beschreibung", "kategorie", "bedingung_"]

    def bedingung_(self, obj):
        return ", ".join([t.titel for t in obj.bedingung.all()])


class GfsSkilltreeEntryAdmin(admin.ModelAdmin):
    class IsCorrectlyFormattedFilter(admin.SimpleListFilter):
        title = 'correctly_formatted'
        parameter_name = 'correctly_formatted'

        def lookups(self, request, model_admin):
            return (
                ("y", "Korrekt"),
                ("n", "Falsch"),
            )

        def queryset(self, request, queryset):
            if self.value() is None: return queryset
            value = self.value() == "y"

            ids = []
            for e in queryset:
                is_correct = "error" not in e.__repr__().lower()
                if (value and is_correct) or (not value and not is_correct): ids.append(e.id)

            return queryset.filter(id__in=ids)

    list_display = ["context_", "entry", "operation", "correctly_formatted"]

    search_fields = ["gfs__titel", "base__stufe", "text", "vorteil__titel", "nachteil__titel", "spezialfertigkeit__titel", "wissensfertigkeit__titel", "amount", "stufe", "wesenkraft__titel"]
    list_filter = ["gfs", "base__stufe", "operation", IsCorrectlyFormattedFilter]

    def context_(self, obj):
        return f"{obj.gfs.titel} St. {obj.base.stufe}"

    def entry(self, obj):
        return obj.__repr__()
    
    def correctly_formatted(self, obj):
        return "error" not in obj.__repr__().lower()
    correctly_formatted.boolean = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'gfs', 'base', 'fertigkeit', 'vorteil', 'nachteil', 'wesenkraft', 'spezialfertigkeit', 'wissensfertigkeit', 'magische_ausrüstung'
        )


admin.site.register(Charakter, CharakterAdmin)
admin.site.register(Wesen, SpeziesAdmin)
admin.site.register(Gfs, GfsAdmin)
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

admin.site.register(SkilltreeBase, admin.ModelAdmin)
admin.site.register(Talent, TalentAdmin)

admin.site.register(GfsAbility, GfsAbilityAdmin)
admin.site.register(GfsStufenplanBase, GfsStufenplanBaseAdmin)

admin.site.register(Spieler, SpielerAdmin)

admin.site.register(GfsSkilltreeEntry, GfsSkilltreeEntryAdmin)
