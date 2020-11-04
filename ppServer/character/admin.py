from django.contrib import admin

from .models import *
from shop.admin import hide_on_shop_angucken, ViewOnlyAdmin, ViewOnlyInLine, NotDeleteAdmin
from shop.admin import hide_on_shop_angucken


class WesenkraftZusatzWesenspInLine(ViewOnlyInLine):
    model = Wesenkraft.zusatz_wesenspezifisch.through
    extra = 1


class SpeziesAttributInLine(ViewOnlyInLine):
    model = SpeziesAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request):
        return False


class SpeziesStufenplanInLine(ViewOnlyInLine):
    model = Stufenplan
    fields = ["stufe", "ep", "vorteile", "ap", "ap_max", "fp", "fg", "zauber", "wesenkräfte",
            "spezial", "wissensp", "weiteres"]
    extra = 0


class GfsAttributInLine(ViewOnlyInLine):
    model = GfsAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request):
        return False


class GfsFertigkeitInLine(ViewOnlyInLine):
    model = GfsFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request):
        return False


class GfsVorteilInLine(ViewOnlyInLine):
    model = GfsVorteil
    extra = 1


class GfsNachteilInLine(ViewOnlyInLine):
    model = GfsNachteil
    extra = 1


class GfsWesenkraftInLine(ViewOnlyInLine):
    model = GfsWesenkraft
    extra = 1


class GfsStufenplanInLine(ViewOnlyInLine):
    model = GfsStufenplan
    fields = ["basis", "vorteile", "zauber", "wesenkräfte", "weiteres"]
    extra = 0

class GfsSkilltreeInLine(ViewOnlyInLine):
    model = SkilltreeEntryGfs
    fields = ["context", "text"]
    extra = 0


class ProfessionAttributInLine(ViewOnlyInLine):
    model = ProfessionAttribut
    fields = ["attribut", "aktuellerWert", "maxWert"]
    readonly_fields = ["attribut"]
    extra = 0

    def has_add_permission(self, request):
        return False


class ProfessionFertigkeitInLine(ViewOnlyInLine):
    model = ProfessionFertigkeit
    fields = ["fertigkeit", "fp"]
    readonly_fields = ["fertigkeit"]
    extra = 0

    def has_add_permission(self, request):
        return False


class ProfessionSpezialInLine(ViewOnlyInLine):
    model = ProfessionSpezialfertigkeit
    fields = ["spezial"]
    extra = 1


class ProfessionWissenInLine(ViewOnlyInLine):
    model = ProfessionWissensfertigkeit
    fields = ["wissen"]
    extra = 1


class ProfessionTalentInLine(ViewOnlyInLine):
    model = ProfessionTalent
    fields = ["talent"]
    extra = 1


class ProfessionSkilltreeInLine(ViewOnlyInLine):
    model = SkilltreeEntryProfession
    fields = ["context", "text"]
    extra = 0


class ProfessionStufenplanInLine(ViewOnlyInLine):
    model = ProfessionStufenplan
    fields = ["basis", "tp", "weiteres"]
    extra = 0


class SpezialAusgleichInLine(ViewOnlyInLine):
    model = Spezialfertigkeit.ausgleich.through
    extra = 1


class WissenFertInLine(ViewOnlyInLine):
    model = Wissensfertigkeit.fertigkeit.through
    extra = 1


class RelSpeziesInline(ViewOnlyInLine):
    model = RelSpezies
    extra = 1


class RelAttributInline(ViewOnlyInLine):
    fields = ['attribut', 'aktuellerWert', 'aktuellerWert_bonus', 'maxWert', 'maxWert_bonus', 'fg']
    readonly_fields = ['attribut']
    model = RelAttribut
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RelFertigkeitInLine(ViewOnlyInLine):
    fields = ['fertigkeit', 'fp', 'fp_bonus']
    readonly_fields = ['fertigkeit']
    model = RelFertigkeit
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RelWesenkraftInLine(ViewOnlyInLine):
    model = RelWesenkraft
    extra = 1


class RelSpezialfertigkeitInLine(ViewOnlyInLine):
    model = RelSpezialfertigkeit
    extra = 1


class RelWissensfertigkeitInLine(ViewOnlyInLine):
    model = RelWissensfertigkeit
    extra = 1


class AffektivitätInLine(admin.TabularInline):
    model = Affektivität
    extra = 1
    exclude = ['grad', 'umgang']


class RelBegleiterInLine(admin.TabularInline):
    model = RelBegleiter
    extra = 1


class RelVorteilInLine(ViewOnlyInLine):
    model = RelVorteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 1


class RelNachteilInLine(ViewOnlyInLine):
    model = RelNachteil
    fields = ["anzahl", "teil", "notizen"]
    extra = 1

class RelTalentInLine(ViewOnlyInLine):
    model = RelTalent
    fields = ["talent"]
    extra = 1

########## generic (st)shop ##############

class RelShopInLine(ViewOnlyInLine):
    extra = 1
    fields = ["anz", "item", "notizen"]


class RelStShopInLine(ViewOnlyInLine):
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


class RelAlchemieInLine(RelShopInLine):
    model = RelAlchemie


class RelTinkerInLine(RelShopInLine):
    model = RelTinker



class CharakterAdmin(NotDeleteAdmin):

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
        ('Verwandlungen', {'fields': ['verwandlungen']}),
    ]

    inlines = [
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
               RelAlchemieInLine,
               RelTinkerInLine,
    ]

    list_display = ['name', 'eigentümer', "gfs", "wesen_", "profession", "ep_system", "larp", "in_erstellung"]

    list_filter = ['larp', 'ep_system', 'eigentümer']
    search_fields = ['name', 'eigentümer__name']

    save_on_top = True

    def wesen_(self, obj):
        return ', '.join([w.titel for w in obj.spezies.all()])

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name__iexact="shop angucken"):
            return ["manifest", "rang", "HPplus", "sp", "geld", "nutzt_magie", "useEco", "eigentümer",
                    "ep_system", "larp", "in_erstellung", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"]
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        if request.user.groups.filter(name__iexact="shop angucken"):
            return Charakter.objects.filter(eigentümer__name__exact=request.user.username)
        else:
            return super().get_queryset(request)

    def has_add_permission(self, request):
        if request.user.groups.filter(name__iexact="shop angucken"):
            return False
        return super().has_add_permission(request)


class AttributAdmin(ViewOnlyAdmin):
    list_display = ('titel', 'beschreibung')
    search_fields = ['titel', 'beschreibung']


class FertigkeitAdmin(ViewOnlyAdmin):

    fieldsets = [
        (None, {'fields': ['titel', 'limit', 'attr1', 'attr2']}),
        ('Beschreibung', {'fields': ['beschreibung']})
    ]

    list_display = ('titel', 'attr1', 'attr2', 'limit', 'beschreibung')
    search_fields = ['titel', 'attr1__titel', 'attr2__titel', 'limit']
    list_filter = ['attr1', 'attr2', 'limit']


class WesenkraftAdmin(hide_on_shop_angucken):

    fields = ['titel', 'min_rang', 'probe', 'wirkung', 'wesen', "zusatz_manifest"]
    inlines = [WesenkraftZusatzWesenspInLine]

    list_display = ['titel', 'min_rang', 'probe', 'wirkung', 'wesen']
    search_fields = ['titel', 'wesen']
    list_filter = ['wesen']


class SpezialfertigkeitAdmin(hide_on_shop_angucken):
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


class WissensfertigkeitAdmin(hide_on_shop_angucken):
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


class SpeziesAdmin(hide_on_shop_angucken):
    list_display = ('titel', 'beschreibung_')
    search_fields = ('titel',)

    inlines = [SpeziesAttributInLine #, SpeziesStufenplanInLine
    ]

    def beschreibung_(self, obj):
        str = obj.beschreibung[:100]
        if len(obj.beschreibung) > 100: str += "..."
        return str


class GfsAdmin(hide_on_shop_angucken):
    list_display = ('titel', 'ap', 'beschreibung_', 'vorteil_', 'nachteil_',
                    "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "wesenkraft_", "startmanifest",)
    list_filter = ['ap', 'startmanifest', "wesenschaden_waff_kampf"]
    search_fields = ('titel', 'ap')

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

    def beschreibung_(self, obj):
        str = obj.beschreibung[:100]
        if len(obj.beschreibung) > 100:
            str += "..."
        return str


class ProfessionAdmin(hide_on_shop_angucken):
    list_display = ('titel', 'beschreibung_')
    search_fields = ('titel',)

    inlines = [ProfessionAttributInLine, ProfessionFertigkeitInLine,
               ProfessionSpezialInLine, ProfessionWissenInLine,
               ProfessionTalentInLine, ProfessionSkilltreeInLine,
               ProfessionStufenplanInLine]

    def beschreibung_(self, obj):
        str = obj.beschreibung[:100]
        if len(obj.beschreibung) > 100:
            str += "..."
        return str


class VorNachteilAdmin(hide_on_shop_angucken):

    list_display = ('titel', 'ip', 'beschreibung', "wann_wählbar")
    list_filter = ['ip', "wann_wählbar"]
    search_fields = ['titel', 'ip', "wann_wählbar"]


class BegleiterAdmin(NotDeleteAdmin):
    list_display = ['name', 'beschreibung']
    search_fields = ['name']
    list_filter = ['name']


class BerufAdmin(NotDeleteAdmin):
    list_display = ['titel', 'beschreibung']
    search_fields = ['titel']
    list_filter = ['titel']


class ReligionAdmin(NotDeleteAdmin):
    list_display = ['titel', 'beschreibung']
    search_fields = ['titel']
    list_filter = ['titel']


class SpielerAdmin(hide_on_shop_angucken):
    #readonly_fields = ["name"]
    fields = ["name", "geburtstag"]
    list_display = ["name", "geburtstag"]


class RangRankingEntryAdmin(hide_on_shop_angucken):
    exclude = []
    list_display = ["order", "ranking", "min_rang", "max_rang"]


class SkilltreeEntryWesenAdmin(hide_on_shop_angucken):
    list_display = ["wesen", "context"]
    list_filter = ["wesen", "context"]


class StufenplanAdmin(hide_on_shop_angucken):
    list_editable = ["ep", "ap", "ap_max", "fp", "fg", "zauber", "spezial", "wissensp"]#, "weiteres"]
    list_display = ["wesen", "stufe", "ep", "vorteile_", "ap", "ap_max", "fp", "fg", "zauber", "wesenkräfte_",
                    "spezial", "wissensp", "weiteres"]
    list_filter = ["wesen", "stufe"]

    def vorteile_(self, obj):
        return ', '.join([a.titel for a in obj.vorteile.all()])

    def wesenkräfte_(self, obj):
        return ', '.join([a.titel for a in obj.wesenkräfte.all()])


class GfsStufenplanBaseAdmin(hide_on_shop_angucken):
    list_display = ["stufe", "ep", "ap", "fp", "fg"]


class ProfessionStufenplanBaseAdmin(hide_on_shop_angucken):
    list_display = ["stufe", "ep"]


class TalentAdmin(hide_on_shop_angucken):
    list_display = ["titel", "tp", "beschreibung", "kategorie"]


admin.site.register(Charakter, CharakterAdmin)
admin.site.register(Spezies, SpeziesAdmin)
admin.site.register(Gfs, GfsAdmin)
admin.site.register(Profession, ProfessionAdmin)
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

admin.site.register(SkilltreeBase, hide_on_shop_angucken)
#admin.site.register(SkilltreeEntryWesen, SkilltreeEntryWesenAdmin)
#admin.site.register(SkilltreeEntryKategorie, hide_on_shop_angucken)
admin.site.register(Talent, TalentAdmin)

admin.site.register(GfsStufenplanBase, GfsStufenplanBaseAdmin)
admin.site.register(ProfessionStufenplanBase, ProfessionStufenplanBaseAdmin)

admin.site.register(RangRankingEntry, RangRankingEntryAdmin)
admin.site.register(Spieler, SpielerAdmin)

#admin.site.register(Stufenplan, StufenplanAdmin)

#admin.site.register(RelFirmaItem, hide_on_shop_angucken)
#admin.site.register(RelFirmaWaffen_Werkzeuge, hide_on_shop_angucken)
#admin.site.register(RelFirmaMagazin, hide_on_shop_angucken)
#admin.site.register(RelFirmaPfeil_Bolzen, hide_on_shop_angucken)
#admin.site.register(RelFirmaSchusswaffen, hide_on_shop_angucken)
#admin.site.register(RelFirmaMagische_Ausrüstung, hide_on_shop_angucken)
#admin.site.register(RelFirmaRüstung, hide_on_shop_angucken)
#admin.site.register(RelFirmaAusrüstung_Technik, hide_on_shop_angucken)
#admin.site.register(RelFirmaFahrzeug, hide_on_shop_angucken)
#admin.site.register(RelFirmaEinbauten, hide_on_shop_angucken)
#admin.site.register(RelFirmaZauber, hide_on_shop_angucken)

#admin.site.register(RelFirmaStItem, hide_on_shop_angucken)
#admin.site.register(RelFirmaStWaffen_Werkzeuge, hide_on_shop_angucken)
#admin.site.register(RelFirmaStMagazin, hide_on_shop_angucken)
#admin.site.register(RelFirmaStPfeil_Bolzen, hide_on_shop_angucken)
#admin.site.register(RelFirmaStSchusswaffen, hide_on_shop_angucken)
#admin.site.register(RelFirmaStMagische_Ausrüstung, hide_on_shop_angucken)
#admin.site.register(RelFirmaStRüstung, hide_on_shop_angucken)
#admin.site.register(RelFirmaStAusrüstung_Technik, hide_on_shop_angucken)
#admin.site.register(RelFirmaStFahrzeug, hide_on_shop_angucken)
#admin.site.register(RelFirmaStEinbauten, hide_on_shop_angucken)
#admin.site.register(RelFirmaStZauber, hide_on_shop_angucken)
