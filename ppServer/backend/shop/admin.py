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


##################### InLines #########################

def get_SlotInLine(m: type[Slot]) -> type[admin.TabularInline]:
    class Admin(admin.TabularInline):
        model=m
        fields = ["tag", "num"]
        extra = 1

    return Admin

def get_InLine(m: type[models.Model]) -> type[admin.TabularInline]:
    class Admin(admin.TabularInline):
        model = m
        extra = 1

    return Admin


################# BaseAdmin #########################

class BaseAdmin(admin.ModelAdmin):
    search_fields = ['name', "beschreibung__contains"]
    exclude = ['slots', 'possible_upgrades']
    list_editable = ["has_implementation", "beschreibung", "frei_editierbar"]

    def get_readonly_fields(self, request: HttpRequest, obj = ...):
        # spielleitung
        if request.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            return super().get_readonly_fields(request, obj)
        
        # spieler (create OR frei_editierbar)
        if not obj or obj.frei_editierbar:
            return ["frei_editierbar"]
        
        # spieler, not frei_editierbar
        return [field.name for field in self.opts.local_fields if field.name != "icon"]


################### ShopAdmins #######################

class ItemAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]


class NahkampfwaffeAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", "reichweite", "wirkbereich", "händigkeit", "fertigkeit", "schaden", 'bs', 'zs', 'dk', 'schadensart', 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', 'bs', 'zs', 'dk', 'schadensart', 'händigkeit', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["schaden", "reichweite", "wirkbereich", "händigkeit", "fertigkeit", 'kategorie']

    inlines = [get_SlotInLine(SlotNahkampfwaffe), get_InLine(Nahkampfwaffe.possible_upgrades.through)]


class MunitionAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'bs', 'zs', 'schaden', 'schadensart', 'wirkbereich', 'price', 'frei_editierbar', "has_implementation")
    # list_filter = ['schuss', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ['schaden', 'wirkbereich']


class FernkampfwaffeAdmin(BaseAdmin):
    exclude = BaseAdmin.exclude + ['munition']
    list_display = ('name', 'beschreibung', "ab_stufe", 'schuss', 'munition_', 'feuerrate', "reichweite", "händigkeit", 'dk', 'präzision', 'price',
                    'kategorie', 'fertigkeit', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', 'dk', 'präzision', 'fertigkeit__titel', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ['feuerrate', "reichweite", "händigkeit",]

    inlines = [get_InLine(Fernkampfwaffe.munition.through), get_SlotInLine(SlotFernkampfwaffe), get_InLine(Fernkampfwaffe.possible_upgrades.through)]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("munition")

    def munition_(self, obj):
        return ", ".join([m.__str__() for m in obj.munition.all()])

class Magische_AusrüstungAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]


class Ritual_RuneAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", "schaden", "schadensart", "wirkbereich", "manaverbrauch", 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["schaden", "schadensart", "wirkbereich", "manaverbrauch"]

    inlines = [get_SlotInLine(SlotRitual_Rune)]


class RüstungAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'damage_speciality', 'kategorie', 'schutz', 'haltbarkeit', 'price', 'frei_editierbar', "has_implementation")
    # list_filter = ['schutz', 'haltbarkeit', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ['damage_speciality', 'kategorie']

    inlines = [get_SlotInLine(SlotRüstung), get_InLine(Rüstung.possible_upgrades.through)]


class TechnikAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'kategorie', 'price',
                    'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]


class FahrzeugAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'geschwindigkeit', 'hp', 'erfolge',
                    'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', 'geschwindigkeit', 'hp', 'erfolge', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["kategorie"]


class EinbauteAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'manifestverlust', 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', 'manifestverlust', "frei_editierbar"]

    inlines = [get_SlotInLine(SlotEinbaute), get_InLine(Einbaute.possible_upgrades.through)]


class ZauberAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", "schaden", "wirkbereich", "wirkdauer", 'astralschaden', 'manaverbrauch', "verteidigung", 'schadensart', 'price',
                    'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', 'astralschaden', 'manaverbrauch', "verteidigung", 'schadensart', "frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["schaden", "wirkbereich", "wirkdauer"]

    inlines = [get_SlotInLine(SlotZauber), get_InLine(Zauber.possible_upgrades.through)]


class AlchemieAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", 'price', 'kategorie', 'frei_editierbar', "has_implementation")
    # list_filter = ['kategorie', "frei_editierbar"]


class TinkerAdmin(BaseAdmin):
    list_display = ('icon_', 'name', 'beschreibung', "profitable_flip", "wooble_buy_price", "wooble_sell_price", "werte", "ab_stufe", 'price', 'kategorie', 'frei_editierbar', "has_implementation", "has_implementation", "minecraft_mod_id")
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
    list_display = ('name', 'beschreibung', "ab_stufe", "hp", "physische_reaktion", "astrale_reaktion", "astraler_widerstand", "physischer_widerstand", 'price', 'frei_editierbar', "has_implementation")
    # list_filter = ["frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["hp", "physische_reaktion", "astrale_reaktion", "astraler_widerstand", "physischer_widerstand"]

    inlines = [get_SlotInLine(SlotBegleiter), get_InLine(Begleiter.possible_upgrades.through)]


class EngelsroboterAdmin(BaseAdmin):
    list_display = ('name', 'beschreibung', "ab_stufe", "hp", "physische_reaktion", "astrale_reaktion", "astraler_widerstand", "physischer_widerstand", 'ST', 'UM', 'MA', 'IN', 'price', 'frei_editierbar', "has_implementation")
    # list_filter = ["frei_editierbar"]
    list_editable = BaseAdmin.list_editable + ["hp", "physische_reaktion", "astrale_reaktion", "astraler_widerstand", "physischer_widerstand"]


################### Firma & Modifier ########################

class FirmaAdmin(admin.ModelAdmin):
    list_display = ('_icon', 'name', 'beschreibung')
    list_display_links = ("name",)

    def _icon(self, obj):
        return format_html(f'<img src="{obj.icon.url}" style="max-width: 32px; max-height:32px;" loading="lazy" />') if obj.icon else self.get_empty_value_display()


class ModifierAdmin(admin.ModelAdmin):
    list_display = ['factor', '_firmen', '_kategorien', 'active']
    exclude = ['kategorien', 'firmen']
    list_filter = ['kategorien', 'firmen']

    inlines = [get_InLine(Modifier.kategorien.through), get_InLine(Modifier.firmen.through)]
    
    def _firmen(self, obj):
        return obj.firmennames or self.get_empty_value_display()

    def _kategorien(self, obj):
        return ", ".join([e.__str__() for e in obj.kategorien.all()]) or self.get_empty_value_display()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("kategorien").annotate(
            firmennames = ConcatSubquery(Firma.objects.filter(modifier=OuterRef("id")).values("name"), ", "),
        )


################### Upgrade ########################

class TagAdmin(admin.ModelAdmin):
    list_display = ('_icon', 'name')
    list_display_links = ("name",)

    def _icon(self, obj):
        return format_html(f'<img src="{obj.icon.url}" style="max-width: 32px; max-height:32px;" loading="lazy" />') if obj.icon else self.get_empty_value_display()


class UpgradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'beschreibung', 'ab_stufe', 'price', 'field', 'tag', 'prerequisite')
    list_editable = ["prerequisite"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("prerequisite")

    def field(self, obj):
        return f"{obj.get_influenced_field_display() or self.get_empty_value_display()}: {obj.field_value or self.get_empty_value_display()}"





admin.site.register(Item, ItemAdmin)
admin.site.register(Nahkampfwaffe, NahkampfwaffeAdmin)
admin.site.register(Munition, MunitionAdmin)
admin.site.register(Fernkampfwaffe, FernkampfwaffeAdmin)
admin.site.register(Magische_Ausrüstung, Magische_AusrüstungAdmin)
admin.site.register(Ritual_Rune, Ritual_RuneAdmin)
admin.site.register(Rüstung, RüstungAdmin)
admin.site.register(Technik, TechnikAdmin)
admin.site.register(Fahrzeug, FahrzeugAdmin)
admin.site.register(Einbaute, EinbauteAdmin)
admin.site.register(Zauber, ZauberAdmin)
admin.site.register(Alchemie, AlchemieAdmin)
admin.site.register(Tinker, TinkerAdmin)
admin.site.register(Begleiter, BegleiterAdmin)
admin.site.register(Engelsroboter, EngelsroboterAdmin)

admin.site.register(Firma, FirmaAdmin)
admin.site.register(Modifier, ModifierAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Upgrade, UpgradeAdmin)