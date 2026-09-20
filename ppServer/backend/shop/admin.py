import locale
from typing import Any

from django.contrib import admin
from django.db.models import OuterRef, F
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html

from character.models import CustomPermission
from ppServer.utils import ConcatSubquery

from .models import *


class SchussMunitionInLine(admin.TabularInline):
    model = Fernkampfwaffe.munition.through
    extra = 1


############# FirmaShop ##################
class FirmaShopInLine(admin.TabularInline):
    extra = 1


class FirmaItemInLine(FirmaShopInLine):
    model = FirmaItem


class FirmaNahkampfwaffeInLine(FirmaShopInLine):
    model = FirmaNahkampfwaffe


class FirmaMunitionInLine(FirmaShopInLine):
    model = FirmaMunition


class FirmaFernkampfwaffeInLine(FirmaShopInLine):
    model = FirmaFernkampfwaffe


class FirmaMagische_AusrüstungInLine(FirmaShopInLine):
    model = FirmaMagische_Ausrüstung


class FirmaRitual_RuneInLine(FirmaShopInLine):
    model = FirmaRitual_Rune


class FirmaRüstungInLine(FirmaShopInLine):
    model = FirmaRüstung


class FirmaAusrüstung_TechnikInLine(FirmaShopInLine):
    model = FirmaAusrüstung_Technik


class FirmaFahrzeugInLine(FirmaShopInLine):
    model = FirmaFahrzeug


class FirmaEinbauteInLine(FirmaShopInLine):
    model = FirmaEinbaute


class FirmaZauberInLine(FirmaShopInLine):
    model = FirmaZauber


class FirmaAlchemieInLine(FirmaShopInLine):
    model = FirmaAlchemie

class FirmaBegleiterInLine(FirmaShopInLine):
    model = FirmaBegleiter


class FirmaEngelsroboterInLine(FirmaShopInLine):
    model = FirmaEngelsroboter



######### BaseAdmin ##################
class BaseAdmin(admin.ModelAdmin):
    search_fields = ['name', "beschreibung__contains"]
    list_editable = ["has_implementation"]

    def _firmashop_modelset(self) -> str:
        return f"{self.firma_shop_model._meta.model_name}_set"

    def info(self, obj):
        return "frei editierbar" if obj.frei_editierbar else self.get_empty_value_display()

    def billigste(self, obj):
        return obj.cheapest()


    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related(f"{self._firmashop_modelset()}__firma")

    def get_readonly_fields(self, request: HttpRequest, obj = ...):
        # spielleitung
        if request.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            return super().get_readonly_fields(request, obj)
        
        # spieler (create OR frei_editierbar)
        if not obj or obj.frei_editierbar:
            return ["frei_editierbar"]
        
        # spieler, not frei_editierbar
        return [field.name for field in self.opts.local_fields if field.name != "icon"]


########### ShopAdmin ###############

class ItemAdmin(BaseAdmin):
    change_list_template = "shop/admin/change_list_itemtransfer.html"

    shop_model = Item
    firma_shop_model = FirmaItem

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]

    inlines = [FirmaItemInLine]


class NahkampfwaffeAdmin(BaseAdmin):

    shop_model = Nahkampfwaffe
    firma_shop_model = FirmaNahkampfwaffe

    list_display = ('name', 'beschreibung', "ab_stufe", "reichweite", "wirkbereich", "händigkeit", "fertigkeit", "schaden", 'bs', 'zs', 'dk', 'schadensart', 'billigste',
                    'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', 'bs', 'zs', 'dk', 'schadensart', 'händigkeit', "frei_editierbar"]
    list_editable = ["schaden", "reichweite", "wirkbereich", "händigkeit", "fertigkeit", 'kategorie']

    inlines = [FirmaNahkampfwaffeInLine]


class MunitionAdmin(BaseAdmin):

    shop_model = Munition
    firma_shop_model = FirmaMunition

    list_display = ('name', 'beschreibung', "ab_stufe", 'schuss', 'bs', 'zs', 'schaden', 'schadensart', 'wirkbereich', 'billigste', 'info', "has_implementation")
    # list_filter = ['schuss', "frei_editierbar"]
    list_editable = ['schaden', 'wirkbereich']

    inlines = [FirmaMunitionInLine]


class FernkampfwaffeAdmin(BaseAdmin):

    shop_model = Fernkampfwaffe
    firma_shop_model = FirmaFernkampfwaffe

    exclude = ['munition', 'st_munition']
    list_display = ('name', 'beschreibung', "ab_stufe", 'bs', 'zs', 'schaden', 'feuerrate', "reichweite", "wirkbereich", "händigkeit", 'dk', 'präzision', 'schadensart', 'billigste',
                    'kategorie', 'fertigkeit', 'info', "has_implementation")
    # list_filter = ['kategorie', 'bs', 'zs', 'schaden', 'dk', 'präzision', 'schadensart', 'fertigkeit__titel', "frei_editierbar"]
    list_editable = ['schaden', 'feuerrate', "reichweite", "wirkbereich", "händigkeit",]

    inlines = [SchussMunitionInLine, FirmaFernkampfwaffeInLine]


class Magische_AusrüstungAdmin(BaseAdmin):

    shop_model = Magische_Ausrüstung
    firma_shop_model = FirmaMagische_Ausrüstung

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]

    inlines = [FirmaMagische_AusrüstungInLine]


class Ritual_RuneAdmin(admin.ModelAdmin):

    shop_model = Ritual_Rune
    firma_shop_model = FirmaRitual_Rune

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste',
                     'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]
    list_editable = ("has_implementation",)
    search_fields = ["name", "beschreibung__contains"]

    inlines = [FirmaRitual_RuneInLine]

    def info(self, obj):
        return "frei editierbar" if obj.frei_editierbar else self.get_empty_value_display()
    
    def billigste(self, obj):
        return obj.cheapest()

    def get_readonly_fields(self, request: HttpRequest, obj = ...):
        # spielleitung
        if request.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            return super().get_readonly_fields(request, obj)
        
        # spieler (create OR frei_editierbar)
        if not obj or obj.frei_editierbar:
            return ["frei_editierbar"]
        
        # spieler, not frei_editierbar
        return [field.name for field in self.opts.local_fields if field.name != "icon"]


class RüstungAdmin(BaseAdmin):

    shop_model = Rüstung
    firma_shop_model = FirmaRüstung

    list_display = ('name', 'beschreibung', "ab_stufe", 'schutz', 'haltbarkeit', 'billigste',
                    'info', "has_implementation")
    # list_filter = ['schutz', 'haltbarkeit', "frei_editierbar"]

    inlines = [FirmaRüstungInLine]


class Ausrüstung_TechnikAdmin(BaseAdmin):

    shop_model = Ausrüstung_Technik
    firma_shop_model = FirmaAusrüstung_Technik

    list_display = ('name', 'beschreibung', "ab_stufe", 'manifestverlust', 'kategorie', 'billigste',
                    'info', "has_implementation")
    # list_filter = ['kategorie', 'manifestverlust', "frei_editierbar"]

    inlines = [FirmaAusrüstung_TechnikInLine]


class FahrzeugAdmin(BaseAdmin):

    shop_model = Fahrzeug
    firma_shop_model = FirmaFahrzeug

    list_display = ('name', 'beschreibung', "ab_stufe", 'schnelligkeit', 'rüstung', 'erfolge',
                    'billigste', 'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', 'schnelligkeit', 'rüstung', 'erfolge', "frei_editierbar"]

    inlines = [FirmaFahrzeugInLine]


class EinbauteAdmin(BaseAdmin):

    shop_model = Einbaute
    firma_shop_model = FirmaEinbaute

    list_display = ('name', 'beschreibung', "ab_stufe", #'manifestverlust',
     'billigste',
                    'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', 'manifestverlust', "frei_editierbar"]

    inlines = [FirmaEinbauteInLine]


class ZauberAdmin(BaseAdmin):

    shop_model = Zauber
    firma_shop_model = FirmaZauber

    list_display = ('name', 'beschreibung', "ab_stufe", 'astralschaden', 'manaverbrauch', "verteidigung", 'schadensart', 'billigste',
                    'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', 'astralschaden', 'manaverbrauch', "verteidigung", 'schadensart', "frei_editierbar"]

    list_editable = ["verteidigung", "has_implementation", 'schadensart']

    inlines = [FirmaZauberInLine]


class AlchemieAdmin(BaseAdmin):

    shop_model = Alchemie
    firma_shop_model = FirmaAlchemie

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'kategorie', 'info', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]

    inlines = [FirmaAlchemieInLine]


class TinkerAdmin(BaseAdmin):

    shop_model = Tinker
    firma_shop_model = FirmaTinker

    list_display = ('icon_', 'name', 'beschreibung', "profitable_flip", "wooble_buy_price", "wooble_sell_price", "werte", "ab_stufe", 'billigste', 'kategorie', 'info', "has_implementation", "has_implementation", "minecraft_mod_id")
    list_display_links = ('icon_', 'name')
    # list_filter = ['kategorie', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["wooble_buy_price", "wooble_sell_price"]

    fields = ['icon', 'name', 'beschreibung', 'ab_stufe', 'frei_editierbar', 'werte', 'kategorie', "wooble_buy_price", "wooble_sell_price"]


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            profitable_flip = F("wooble_sell_price") - F("wooble_buy_price")
        )

    def icon_(self, obj):
        return format_html('<img src="{0}" style="max-width: 32px; max-height:32px;" loading="lazy" />'.format(obj.icon.url)) if obj.icon else "-"
    icon_.allow_tags = True

    @admin.display(ordering="profitable_flip", description="Flip (Verkaufspreis - Kaufpreis)")
    def profitable_flip(self, obj):
        locale.setlocale(locale.LC_NUMERIC, "de_DE.utf8")
        return format_html(f"<b>{obj.profitable_flip:+n}</b><small> = {obj.wooble_sell_price:n} - {obj.wooble_buy_price:n}</small>")


class BegleiterAdmin(BaseAdmin):

    shop_model = Begleiter
    firma_shop_model = FirmaBegleiter

    list_display = ('name', 'beschreibung', "ab_stufe", 'billigste', 'info', "has_implementation")
    # list_filter = ["frei_editierbar"]

    inlines = [FirmaBegleiterInLine]


class EngelsroboterAdmin(BaseAdmin):

    shop_model = Engelsroboter
    firma_shop_model = FirmaEngelsroboter

    list_display = ('name', 'beschreibung', "ab_stufe", 'ST', 'UM', 'MA', 'IN', 'billigste', 'info', "has_implementation")
    # list_filter = ["frei_editierbar"]

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
        return obj.firmennames or self.get_empty_value_display()

    def _kategorien(self, obj):
        return ", ".join([e.__str__() for e in obj.kategorien.all()]) or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("kategorien").annotate(
            firmennames = ConcatSubquery(Firma.objects.filter(modifier=OuterRef("id")).values("name"), ", "),
        )

admin.site.register(Item, ItemAdmin)
admin.site.register(Nahkampfwaffe, NahkampfwaffeAdmin)
admin.site.register(Munition, MunitionAdmin)
admin.site.register(Fernkampfwaffe, FernkampfwaffeAdmin)
admin.site.register(Magische_Ausrüstung, Magische_AusrüstungAdmin)
admin.site.register(Ritual_Rune, Ritual_RuneAdmin)
admin.site.register(Rüstung, RüstungAdmin)
admin.site.register(Ausrüstung_Technik, Ausrüstung_TechnikAdmin)
admin.site.register(Fahrzeug, FahrzeugAdmin)
admin.site.register(Einbaute, EinbauteAdmin)
admin.site.register(Zauber, ZauberAdmin)
admin.site.register(Alchemie, AlchemieAdmin)
admin.site.register(Tinker, TinkerAdmin)
admin.site.register(Begleiter, BegleiterAdmin)
admin.site.register(Engelsroboter, EngelsroboterAdmin)

admin.site.register(Firma, FirmaAdmin)
admin.site.register(Modifier, ModifierAdmin)