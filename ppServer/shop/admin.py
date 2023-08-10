from typing import Any, List, Optional, Tuple, Union
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import *
from mining.models import Item as MiningItem


class SchussMagazineInLine(admin.TabularInline):
    model = Schusswaffen.magazine.through
    extra = 1


class SchussPfeileBolzenInLine(admin.TabularInline):
    model = Schusswaffen.pfeile_bolzen.through
    extra = 1


############# FirmaShop ##################
class FirmaShopInLine(admin.TabularInline):
    extra = 1


class FirmaItemInLine(FirmaShopInLine):
    model = FirmaItem


class FirmaWaffen_WerkzeugeInLine(FirmaShopInLine):
    model = FirmaWaffen_Werkzeuge


class FirmaMagazinInLine(FirmaShopInLine):
    model = FirmaMagazin


class FirmaPfeil_BolzenInLine(FirmaShopInLine):
    model = FirmaPfeil_Bolzen


class FirmaSchusswaffenInLine(FirmaShopInLine):
    model = FirmaSchusswaffen


class FirmaMagische_AusrüstungInLine(FirmaShopInLine):
    model = FirmaMagische_Ausrüstung


class FirmaRituale_RunenInLine(FirmaShopInLine):
    model = FirmaRituale_Runen


class FirmaRüstungenInLine(FirmaShopInLine):
    model = FirmaRüstungen


class FirmaAusrüstung_TechnikInLine(FirmaShopInLine):
    model = FirmaAusrüstung_Technik


class FirmaFahrzeugInLine(FirmaShopInLine):
    model = FirmaFahrzeug


class FirmaEinbautenInLine(FirmaShopInLine):
    model = FirmaEinbauten


class FirmaZauberInLine(FirmaShopInLine):
    model = FirmaZauber


class FirmaVergessenerZauberInLine(FirmaShopInLine):
    model = FirmaVergessenerZauber

class FirmaAlchemieInLine(FirmaShopInLine):
    model = FirmaAlchemie

class MiningItemInLine(admin.TabularInline):
    model = MiningItem

class FirmaBegleiterInLine(FirmaShopInLine):
    model = FirmaBegleiter


class FirmaEngelsroboterInLine(FirmaShopInLine):
    model = FirmaEngelsroboter



######### BaseAdmin ##################
class BaseAdmin(admin.ModelAdmin):
    search_fields = ['name']

    def illegal_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).illegal:
            return "illegal"
        return None

    def frei_editierbar_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).frei_editierbar:
            return "frei_editierbar"
        return None

    def lizenz_benötigt_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).lizenz_benötigt:
            return "Lizenz benötigt"
        return None

    def billigste(self, obj):
        offers = self.firma_shop_model.objects.filter(item=obj)
        if not offers: return None

        return sorted([o.getPrice() for o in offers])[0]


    def get_readonly_fields(self, request: HttpRequest, obj = ...):
        # spielleiter
        if request.user.groups.filter(name__iexact="spielleiter").exists():
            return super().get_readonly_fields(request, obj)
        
        # spieler (create OR frei_editierbar)
        if not obj or obj.frei_editierbar:
            return ["frei_editierbar"]
        
        # spieler, not frei_editierbar
        return [field.name for field in self.opts.local_fields if field.name != "icon"]


########### ShopAdmin ###############

class ItemAdmin(BaseAdmin):

    shop_model = Item
    firma_shop_model = FirmaItem

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'illegal', 'lizenz_benötigt', "frei_editierbar"
                   ]

    inlines = [FirmaItemInLine]


class Waffen_WerkzeugeAdmin(BaseAdmin):

    shop_model = Waffen_Werkzeuge
    firma_shop_model = FirmaWaffen_Werkzeuge

    list_display = ('name', 'beschreibung', "ab_stufe", 'erfolge', 'bs', 'zs', 'dk', 'billigste',
                    'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'erfolge', 'bs', 'zs', 'dk', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaWaffen_WerkzeugeInLine]


class MagazinAdmin(BaseAdmin):

    shop_model = Magazin
    firma_shop_model = FirmaMagazin

    list_display = ('name', 'beschreibung', "ab_stufe", 'schuss', 'billigste', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['schuss', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaMagazinInLine]


class Pfeil_BolzenAdmin(BaseAdmin):

    shop_model = Pfeil_Bolzen
    firma_shop_model = FirmaPfeil_Bolzen

    list_display = ('name', 'beschreibung', "ab_stufe", 'bs', 'zs', 'billigste', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['bs', 'zs', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaPfeil_BolzenInLine]


class SchusswaffenAdmin(BaseAdmin):

    shop_model = Schusswaffen
    firma_shop_model = FirmaSchusswaffen

    exclude = ['magazine', 'st_magazine', 'pfeile_bolzen', 'st_pfeile_bolzen']
    list_display = ('name', 'beschreibung', "ab_stufe", 'erfolge', 'bs', 'zs', 'dk', 'präzision', 'billigste',
                    'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'erfolge', 'bs', 'zs', 'dk', 'präzision', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [SchussMagazineInLine, SchussPfeileBolzenInLine,
               FirmaSchusswaffenInLine]


class Magische_AusrüstungAdmin(BaseAdmin):

    shop_model = Magische_Ausrüstung
    firma_shop_model = FirmaMagische_Ausrüstung

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaMagische_AusrüstungInLine]


class Rituale_RunenAdmin(admin.ModelAdmin):

    shop_model = Rituale_Runen
    firma_shop_model = FirmaRituale_Runen

    list_display = ('name', 'beschreibung', "ab_stufe", # 'billigste',
                     'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaRituale_RunenInLine]

    def illegal_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).illegal:
            return "illegal"
        return None

    def lizenz_benötigt_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).lizenz_benötigt:
            return "Lizenz benötigt"
        return None

    def frei_editierbar_(self, obj):
        if self.shop_model.objects.get(pk=obj.pk).frei_editierbar:
            return "frei_editierbar"
        return None
    

    def get_readonly_fields(self, request: HttpRequest, obj = ...):
        # spielleiter
        if request.user.groups.filter(name__iexact="spielleiter").exists():
            return super().get_readonly_fields(request, obj)
        
        # spieler (create OR frei_editierbar)
        if not obj or obj.frei_editierbar:
            return ["frei_editierbar"]
        
        # spieler, not frei_editierbar
        return [field.name for field in self.opts.local_fields if field.name != "icon"]


class RüstungenAdmin(BaseAdmin):

    shop_model = Rüstungen
    firma_shop_model = FirmaRüstungen

    list_display = ('name', 'beschreibung', "ab_stufe", 'schutz', 'stärke', 'haltbarkeit', 'billigste',
                    'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['schutz', 'stärke', 'haltbarkeit', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaRüstungenInLine]


class Ausrüstung_TechnikAdmin(BaseAdmin):

    shop_model = Ausrüstung_Technik
    firma_shop_model = FirmaAusrüstung_Technik

    list_display = ('name', 'beschreibung', "ab_stufe", 'manifestverlust', 'kategorie', 'billigste',
                    'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'manifestverlust', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaAusrüstung_TechnikInLine]


class FahrzeugAdmin(BaseAdmin):

    shop_model = Fahrzeug
    firma_shop_model = FirmaFahrzeug

    list_display = ('name', 'beschreibung', "ab_stufe", 'schnelligkeit', 'rüstung', 'erfolge',
                    'billigste', 'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'schnelligkeit', 'rüstung', 'erfolge', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaFahrzeugInLine]


class EinbautenAdmin(BaseAdmin):

    shop_model = Einbauten
    firma_shop_model = FirmaEinbauten

    list_display = ('name', 'beschreibung', "ab_stufe", #'manifestverlust',
     'billigste',
                    'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', #'manifestverlust',
    'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaEinbautenInLine]


class ZauberAdmin(BaseAdmin):

    shop_model = Zauber
    firma_shop_model = FirmaZauber

    list_display = ('name', 'beschreibung', "ab_stufe", 'schaden', 'astralschaden', "astralsch_is_direct", 'manaverbrauch', "verteidigung", 'billigste',
                    'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'schaden', 'astralschaden', "astralsch_is_direct", 'manaverbrauch', "verteidigung", 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    list_editable = ["verteidigung", "astralsch_is_direct"]

    inlines = [FirmaZauberInLine]


class VergessenerZauberAdmin(BaseAdmin):

    shop_model = VergessenerZauber
    firma_shop_model = FirmaVergessenerZauber

    list_display = ('name', 'beschreibung', "ab_stufe", 'schaden', 'astralschaden', 'manaverbrauch', 'billigste',
                    'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['schaden', 'astralschaden', 'manaverbrauch', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaVergessenerZauberInLine]


class AlchemieAdmin(BaseAdmin):

    shop_model = Alchemie
    firma_shop_model = FirmaAlchemie

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['kategorie', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaAlchemieInLine]


class TinkerAdmin(BaseAdmin):

    shop_model = Tinker
    firma_shop_model = FirmaTinker

    list_display = ('icon_', 'name', 'beschreibung', "minecraft_mod_id", "werte", "ab_stufe", 'billigste', 'kategorie', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_display_links = ('icon_', 'name')
    list_filter = ['kategorie', 'illegal', 'lizenz_benötigt', "frei_editierbar"]

    fields = ['icon', 'name', 'beschreibung', 'ab_stufe', 'illegal', 'lizenz_benötigt', 'frei_editierbar', 'werte', 'kategorie']

    inlines = [MiningItemInLine]


    def icon_(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" />'.format(obj.icon.url)) if obj.icon else "-"
    icon_.allow_tags = True


class BegleiterAdmin(BaseAdmin):

    shop_model = Begleiter
    firma_shop_model = FirmaBegleiter

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaBegleiterInLine]


class EngelsroboterAdmin(BaseAdmin):

    shop_model = Engelsroboter
    firma_shop_model = FirmaEngelsroboter

    list_display = ('name', 'beschreibung', "ab_stufe", 'ST', 'UM', 'MA', 'IN', 'billigste', 'illegal_', 'lizenz_benötigt_', "frei_editierbar_")
    list_filter = ['illegal', 'lizenz_benötigt', "frei_editierbar"]

    inlines = [FirmaEngelsroboterInLine]



class FirmaAdmin(admin.ModelAdmin):
    list_display = ('name', 'beschreibung')



class ShopCategoryInline(admin.TabularInline):
    model = Modifier.kategorien.through
    verbose_name = 'Kategorie'
    verbose_name_plural = 'Kategorien'
    extra = 1
class FirmaInLine(admin.TabularInline):
    model = Modifier.firmen.through
    verbose_name = 'Firma'
    verbose_name_plural = 'Firmen'
    extra = 1
class ModifierAdmin(admin.ModelAdmin):
    list_display = ['prio', 'price_modification', '_firmen', '_kategorien', 'active']
    exclude = ['kategorien', 'firmen']
    list_filter = ['kategorien', 'firmen']

    inlines = [ShopCategoryInline, FirmaInLine]

    def price_modification(self, obj):
        return '{} {}'.format('*' if obj.is_factor_not_addition else '+', obj.price_modifier)
    
    def _firmen(self, obj):
        if not obj.firmen.count(): return '-'
        return ", ".join([e.name for e in obj.firmen.all()])

    def _kategorien(self, obj):
        if not obj.kategorien.count(): return '-'
        return ", ".join([e.__str__() for e in obj.kategorien.all()])

admin.site.register(Item, ItemAdmin)
admin.site.register(Waffen_Werkzeuge, Waffen_WerkzeugeAdmin)
admin.site.register(Magazin, MagazinAdmin)
admin.site.register(Pfeil_Bolzen, Pfeil_BolzenAdmin)
admin.site.register(Schusswaffen, SchusswaffenAdmin)
admin.site.register(Magische_Ausrüstung, Magische_AusrüstungAdmin)
admin.site.register(Rituale_Runen, Rituale_RunenAdmin)
admin.site.register(Rüstungen, RüstungenAdmin)
admin.site.register(Ausrüstung_Technik, Ausrüstung_TechnikAdmin)
admin.site.register(Fahrzeug, FahrzeugAdmin)
admin.site.register(Einbauten, EinbautenAdmin)
admin.site.register(Zauber, ZauberAdmin)
admin.site.register(VergessenerZauber, VergessenerZauberAdmin)
admin.site.register(Alchemie, AlchemieAdmin)
admin.site.register(Tinker, TinkerAdmin)
admin.site.register(Begleiter, BegleiterAdmin)
admin.site.register(Engelsroboter, EngelsroboterAdmin)

admin.site.register(Firma, FirmaAdmin)
admin.site.register(Modifier, ModifierAdmin)