from django.contrib import admin

from .models import *


class WesenkraftZusatzWesenspInLine(admin.TabularInline):
    model = Wesenkraft.zusatz_gfsspezifisch.through
    extra = 1


class GfsAttributInLine(admin.TabularInline):
    model = GfsAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class GfsFertigkeitInLine(admin.TabularInline):
    model = GfsFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class GfsVorteilInLine(admin.TabularInline):
    model = GfsVorteil
    extra = 1


class GfsNachteilInLine(admin.TabularInline):
    model = GfsNachteil
    extra = 1


class GfsWesenkraftInLine(admin.TabularInline):
    model = GfsWesenkraft
    extra = 1


class GfsStufenplanInLine(admin.TabularInline):
    model = GfsStufenplan
    fields = ["basis", "vorteile", "zauber", "wesenkräfte", "special_ability", "special_ability_description"]
    extra = 0

class GfsSkilltreeInLine(admin.TabularInline):
    model = SkilltreeEntryGfs
    fields = ["context", "text"]
    extra = 0


class ProfessionAttributInLine(admin.TabularInline):
    model = ProfessionAttribut
    fields = ["attribut", "aktuellerWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ProfessionFertigkeitInLine(admin.TabularInline):
    model = ProfessionFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ProfessionSpezialInLine(admin.TabularInline):
    model = ProfessionSpezialfertigkeit
    fields = ["spezial"]
    extra = 1


class ProfessionWissenInLine(admin.TabularInline):
    model = ProfessionWissensfertigkeit
    fields = ["wissen"]
    extra = 1


class ProfessionSkilltreeInLine(admin.TabularInline):
    model = SkilltreeEntryProfession
    fields = ["context", "text"]
    extra = 0


class ProfessionStufenplanInLine(admin.TabularInline):
    model = ProfessionStufenplan
    fields = ["basis", "tp", "weiteres"]
    extra = 0


class SpezialAusgleichInLine(admin.TabularInline):
    model = Spezialfertigkeit.ausgleich.through
    extra = 1


class WissenFertInLine(admin.TabularInline):
    model = Wissensfertigkeit.fertigkeit.through
    extra = 1


class RelSpeziesInline(admin.TabularInline):
    model = RelSpezies
    extra = 1


class RelPersönlichkeitInline(admin.TabularInline):
    model = RelPersönlichkeit
    extra = 1


class RelAttributInline(admin.TabularInline):
    fields = ['attribut', 'aktuellerWert', 'aktuellerWert_bonus', 'maxWert', 'maxWert_bonus', 'fg']
    readonly_fields = ['attribut', 'aktuellerWert_bonus', 'maxWert_bonus']
    model = RelAttribut
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RelFertigkeitInLine(admin.TabularInline):
    fields = ['fertigkeit', 'fp', 'fp_bonus']
    readonly_fields = ['fertigkeit']
    model = RelFertigkeit
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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


class RelVorteilInLine(admin.TabularInline):
    model = RelVorteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 1


class RelNachteilInLine(admin.TabularInline):
    model = RelNachteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 1

class RelTalentInLine(admin.TabularInline):
    model = RelTalent
    fields = ["talent"]
    extra = 1

########## generic (st)shop ##############

class RelShopInLine(admin.TabularInline):
    extra = 1
    fields = ["anz", "item", "notizen"]


class RelStShopInLine(admin.TabularInline):
    extra = 1
    fields = ["anz", "stufe", "item", "notizen"]


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


class RelRituale_RunenInLine(RelStShopInLine):
    model = RelRituale_Runen


class RelRüstungInLine(RelShopInLine):
    model = RelRüstung


class RelAusrüstung_TechnikInLine(RelShopInLine):
    model = RelAusrüstung_Technik
    fields = ["anz", "item", "notizen", "selbst_eingebaut"]


class RelFahrzeugInLine(RelShopInLine):
    model = RelFahrzeug


class RelEinbautenInLine(RelShopInLine):
    model = RelEinbauten


class RelZauberInLine(RelShopInLine):
    model = RelZauber


class RelVergessenerZauberInLine(RelShopInLine):
    model = RelVergessenerZauber


class RelAlchemieInLine(RelShopInLine):
    model = RelAlchemie


class RelTinkerInLine(RelShopInLine):
    model = RelTinker


class RelBegleiterInLine(RelShopInLine):
    model = RelBegleiter



class CharakterAdmin(admin.ModelAdmin):

    class Meta:
        model = Charakter

    fieldsets = [
        ("Settings (Finger weg)", {'fields': ['eigentümer', "in_erstellung", "ep_system", "larp"]}),
        ('Basic', {'fields': ['name', "gfs", "profession", "gewicht", "größe", 'alter', 'geschlecht', 'sexualität', 'beruf', "präf_arm",
                              'religion', "hautfarbe", "haarfarbe", "augenfarbe"]}),
        ("Manifest", {"fields": ["manifest", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust"]}),
        ('HP', {'fields': ['rang', 'HPplus']}),
        ("Basischaden im Waffenlosen Kampf", {"fields": ["wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"]}),
        ('Ressourcen', {'fields': ['sp', "geld", 'ip', 'tp', "nutzt_magie", 'useEco', 'eco', 'morph']}),
        ('Geschreibsel', {'fields': ['persönlicheZiele', 'notizen', 'sonstige_items']}),
    ]

    inlines = [
               RelPersönlichkeitInline,
               RelSpeziesInline, RelWesenkraftInLine,
               RelAttributInline, RelFertigkeitInLine,
               RelSpezialfertigkeitInLine,
               RelWissensfertigkeitInLine, RelVorteilInLine,
               RelNachteilInLine, RelTalentInLine,
               AffektivitätInLine, RelBegleiterInLine,
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
               RelBegleiterInLine
    ]

    list_display = ['name', 'eigentümer', "gfs", "wesen_", "profession", "ep_system", "larp", "in_erstellung"]

    list_filter = ['larp', 'ep_system', 'eigentümer']
    search_fields = ['name', 'eigentümer__name']

    save_on_top = True

    def wesen_(self, obj):
        return ', '.join([w.titel for w in obj.spezies.all()])

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name__iexact="spieler"):
            return ['eigentümer', "in_erstellung", "ep_system", "larp", "gfs", 'HPplus', 'ip',
                    "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"]
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        if request.user.groups.filter(name__iexact="spieler"):
            return Charakter.objects.filter(eigentümer__name__exact=request.user.username)
        else:
            return super().get_queryset(request)


class AttributAdmin(admin.ModelAdmin):
    list_display = ('titel', 'beschreibung')
    search_fields = ['titel', 'beschreibung']


class FertigkeitAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {'fields': ['titel', 'limit', 'attr1', 'attr2']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    list_display = ('titel', 'attr1', 'attr2', 'limit', 'beschreibung')
    search_fields = ['titel', 'attr1__titel', 'attr2__titel', 'limit']
    list_filter = ['attr1', 'attr2', 'limit']


class WesenkraftAdmin(admin.ModelAdmin):

    fields = ['titel', 'min_rang', 'probe', 'wirkung', 'manaverbrauch', 'wesen', "zusatz_manifest"]
    inlines = [WesenkraftZusatzWesenspInLine]

    list_display = ['titel', 'min_rang', 'probe', 'wirkung', 'wesen']
    search_fields = ['titel', 'wesen']
    list_filter = ['wesen']


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


class SpeziesAdmin(admin.ModelAdmin):
    list_display = ('komplexität', 'titel',)
    search_fields = ('komplexität', 'titel',)

class GfsAdmin(admin.ModelAdmin):
    list_display = ('titel', 'ap', 'difficulty', 'vorteil_', 'nachteil_',
                    "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "wesenkraft_", "startmanifest",)
    list_filter = ['ap', 'startmanifest', "wesenschaden_waff_kampf"]
    search_fields = ('titel', 'ap')

    list_editable = ['wesenschaden_waff_kampf', 'wesenschaden_andere_gestalt', 'difficulty']

    inlines = [GfsAttributInLine, GfsFertigkeitInLine,
               GfsVorteilInLine, GfsNachteilInLine,
               GfsWesenkraftInLine, GfsSkilltreeInLine,
               GfsStufenplanInLine]

    def vorteil_(self, obj):
        return ', '.join([a.titel for a in obj.vorteile.all()])

    def nachteil_(self, obj):
        return ', '.join([a.titel for a in obj.nachteile.all()])

    def wesenkraft_(self, obj):
        return ', '.join([a.titel for a in obj.wesenkraft.all()])


class GfsSkilltreeAdmin(admin.ModelAdmin):
    list_display = ('gfs', 'stufe_', 'text')

    list_editable = ['text']

    def stufe_(self, obj):
        return obj.context.stufe

class GfsStufenplanAdmin(admin.ModelAdmin):
    list_display = ('gfs_', 'stufe_', 'special_ability', 'special_ability_description')

    list_editable = ['special_ability', 'special_ability_description']

    def stufe_(self, obj):
        return obj.basis.stufe

    def gfs_(self, obj):
        return obj.gfs.titel

class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('titel', 'beschreibung_')
    search_fields = ('titel',)

    inlines = [ProfessionAttributInLine, ProfessionFertigkeitInLine,
               ProfessionSpezialInLine, ProfessionWissenInLine,
               ProfessionSkilltreeInLine, ProfessionStufenplanInLine]

    def beschreibung_(self, obj):
        str = obj.beschreibung[:100]
        if len(obj.beschreibung) > 100:
            str += "..."
        return str


class PersönlichkeitAdmin(admin.ModelAdmin):
    list_display = ('titel', 'positiv', 'negativ')
    search_fields = ('titel', 'positiv', 'negativ')


class VorNachteilAdmin(admin.ModelAdmin):

    list_display = ('titel', 'ip', 'beschreibung', "wann_wählbar")
    list_filter = ['ip', "wann_wählbar"]
    search_fields = ['titel', 'ip', "wann_wählbar"]


class BegleiterAdmin(admin.ModelAdmin):
    list_display = ['name', 'beschreibung']
    search_fields = ['name']
    list_filter = ['name']


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


class RangRankingEntryAdmin(admin.ModelAdmin):
    exclude = []
    list_display = ["order", "ranking", "min_rang", "max_rang"]


class SkilltreeEntryWesenAdmin(admin.ModelAdmin):
    list_display = ["wesen", "context"]
    list_filter = ["wesen", "context"]


class StufenplanAdmin(admin.ModelAdmin):
    list_editable = ["ep", "ap", "ap_max", "fp", "fg", "zauber", "spezial", "wissensp"]
    list_display = ["wesen", "stufe", "ep", "vorteile_", "ap", "ap_max", "fp", "fg", "zauber", "wesenkräfte_",
                    "spezial", "wissensp", "special_ability", "special_ability_description"]
    list_filter = ["wesen", "stufe"]

    def vorteile_(self, obj):
        return ', '.join([a.titel for a in obj.vorteile.all()])

    def wesenkräfte_(self, obj):
        return ', '.join([a.titel for a in obj.wesenkräfte.all()])


class GfsStufenplanBaseAdmin(admin.ModelAdmin):
    list_display = ["stufe", "ep", "ap", "fp", "fg", "tp"]
    list_editable = ["ep", "ap", "fp", "fg", "tp"]


class ProfessionStufenplanBaseAdmin(admin.ModelAdmin):
    list_display = ["stufe", "ep"]


class TalentAdmin(admin.ModelAdmin):
    list_display = ["titel", "tp", "beschreibung", "kategorie"]


admin.site.register(Charakter, CharakterAdmin)
admin.site.register(Spezies, SpeziesAdmin)
admin.site.register(Gfs, GfsAdmin)
admin.site.register(Profession, ProfessionAdmin)
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
admin.site.register(Begleiter, BegleiterAdmin)

admin.site.register(SkilltreeBase, admin.ModelAdmin)
admin.site.register(Talent, TalentAdmin)

admin.site.register(GfsStufenplanBase, GfsStufenplanBaseAdmin)
admin.site.register(ProfessionStufenplanBase, ProfessionStufenplanBaseAdmin)

admin.site.register(RangRankingEntry, RangRankingEntryAdmin)
admin.site.register(Spieler, SpielerAdmin)

admin.site.register(SkilltreeEntryGfs, GfsSkilltreeAdmin)
admin.site.register(GfsStufenplan, GfsStufenplanAdmin)