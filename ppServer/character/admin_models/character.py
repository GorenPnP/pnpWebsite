from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.forms.widgets import Widget as Widget
from django.http.request import HttpRequest
from django.utils.html import format_html

from ppServer.utils import get_filter
from effect.models import RelEffect

from ..models import *


class RelInlineAdmin(admin.TabularInline):
    """ base permissions for Rel.. models """

    extra = 1
    show_change_link = False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        related_char_id = getattr(request.resolver_match.kwargs, 'object_id', None)
        
        qs = super().get_queryset(request).prefetch_related("char__eigentümer")
        return qs.filter(char__id=related_char_id) if related_char_id else qs

class ReadonlyRelInlineAdmin(RelInlineAdmin):
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RelKlasseInline(RelInlineAdmin):
    model = RelKlasse

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("klasse")

class RelAttributInline(ReadonlyRelInlineAdmin):
    fields = ['attribut', 'aktuellerWert', "aktuellerWert_fix", 'aktuellerWert_temp', 'aktuellerWert_bonus', 'maxWert', "maxWert_fix", 'maxWert_temp']
    readonly_fields = ['attribut']
    model = RelAttribut


    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("attribut")


class RelGruppeInLine(ReadonlyRelInlineAdmin):
    fields = ['gruppe', 'fg', "fg_temp"]
    readonly_fields = ['gruppe']
    model = RelGruppe


class RelFertigkeitInLine(ReadonlyRelInlineAdmin):
    fields = ['fertigkeit', 'fp', "fp_temp", 'fp_bonus']
    readonly_fields = ['fertigkeit']
    model = RelFertigkeit

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("fertigkeit")


class RelWesenkraftInLine(RelInlineAdmin):
    model = RelWesenkraft

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("wesenkraft")


class RelSpezialfertigkeitInLine(RelInlineAdmin):
    model = RelSpezialfertigkeit

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spezialfertigkeit__attr1", "spezialfertigkeit__attr2")
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        queryset = formset.form.base_fields["spezialfertigkeit"].queryset.prefetch_related("attr1", "attr2")
        formset.form.base_fields["spezialfertigkeit"].queryset = queryset
        return formset


class RelWissensfertigkeitInLine(RelInlineAdmin):
    model = RelWissensfertigkeit

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("wissensfertigkeit__attr1", "wissensfertigkeit__attr2", "wissensfertigkeit__attr3")
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        queryset = formset.form.base_fields["wissensfertigkeit"].queryset.prefetch_related("attr1", "attr2", "attr3")
        formset.form.base_fields["wissensfertigkeit"].queryset = queryset
        return formset


class AffektivitätInLine(RelInlineAdmin):
    model = Affektivität
    exclude = ['grad', 'umgang']


class RelGfsAbilityInLine(RelInlineAdmin):
    model = RelGfsAbility
    fields = ["ability", "notizen"]

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('ability')

class RelKlasseAbilityInLine(RelInlineAdmin):
    model = RelKlasseAbility
    fields = ["ability", "notizen"]

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('ability')


class RelVorteilInLine(RelInlineAdmin):
    model = RelVorteil
    fields = ["teil", "attribut", "fertigkeit", "engelsroboter", "notizen", "ip", "is_sellable", "will_create"]
    exclude = ["anzahl"]

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit', 'engelsroboter')


class RelNachteilInLine(RelInlineAdmin):
    model = RelNachteil
    fields = ["teil", "attribut", "fertigkeit", "notizen", "ip", "is_sellable", "will_create"]

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit')


class RelTalentInLine(RelInlineAdmin):
    model = RelTalent
    fields = ["talent"]

    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('talent')


class RelEffectInLine(RelInlineAdmin):
    model = RelEffect
    fields = [
        "wertaenderung", "target_fieldname", "target_attribut", "target_fertigkeit", "source_vorteil", "source_nachteil",
        "source_talent", "source_gfsAbility", "source_klasse", "source_klasseAbility", "source_shopBegleiter",
        "source_shopMagischeAusrüstung", "source_shopRüstung", "source_shopAusrüstungTechnik", "source_shopEinbauten", "is_active"
    ]
    extra = 0

    def get_queryset(self, request) -> QuerySet[Any]:
        related_char_id = getattr(request.resolver_match.kwargs, 'object_id', None)

        qs = self.model.objects.prefetch_related(
            'target_attribut__attribut', 'target_attribut__char__eigentümer',
            'target_fertigkeit__fertigkeit', 'target_fertigkeit__char__eigentümer',
            'source_vorteil__teil', 'source_vorteil__char',
            'source_nachteil__teil', 'source_nachteil__char',
            "source_talent__talent", "source_talent__char",
            "source_gfsAbility__ability", "source_gfsAbility__char__eigentümer",
            "source_klasse__klasse", "source_klasse__char__eigentümer",
            "source_klasseAbility__ability", "source_klasseAbility__char",
            "source_shopBegleiter__item", "source_shopMagischeAusrüstung__item", "source_shopRüstung__item", "source_shopAusrüstungTechnik__item", "source_shopEinbauten__item"
        )
        return qs.filter(target_char__id=related_char_id) if related_char_id else qs

    def get_readonly_fields(self, request: HttpRequest, obj):
        if request.spieler.is_spielleitung:
            return filter(lambda item: item not in ['wertaenderung', 'is_active'], self.fields)
        else:
            return self.fields
        
    def has_add_permission(self, request: HttpRequest, obj) -> bool:
        return False

class RelRamschInLine(RelInlineAdmin):
    model = RelRamsch

########## generic (st)shop ##############

class RelShopInLine(RelInlineAdmin):
    fields = ["anz", "item", "notizen"]

    def get_queryset(self, request) -> QuerySet[Any]:
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
    fields = ["anz", "stufe", "item", "notizen"]


class RelRituale_RunenInLine(RelShopInLine):
    model = RelRituale_Runen
    fields = ["anz", "stufe", "item", "notizen"]

class RelRüstungInLine(RelShopInLine):
    model = RelRüstung


class RelAusrüstung_TechnikInLine(RelShopInLine):
    model = RelAusrüstung_Technik
    fields = ["anz", "stufe", "item", "notizen", "selbst_eingebaut"]


class RelFahrzeugInLine(RelShopInLine):
    model = RelFahrzeug


class RelEinbautenInLine(RelShopInLine):
    model = RelEinbauten
    fields = ["anz", "stufe", "item", "notizen"]


class RelZauberInLine(RelShopInLine):
    fields = fields = ["anz", "item", "tier", "notizen"]
    model = RelZauber


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
        ("Settings (Finger weg)", {'fields': ['eigentümer', "in_erstellung", "reduced_rewards_until_klasse_stufe", "larp", "gfs", "tags"]}),
        ('Roleplay', {'fields': ['image', 'name', "gewicht", "größe", 'alter', 'geschlecht', 'sexualität', 'persönlichkeit', 'beruf', "präf_arm",
                              'religion', "hautfarbe", "haarfarbe", "augenfarbe"]}),

        ("Manifest", {"fields": ["manifest", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "manifest_fix"]}),
        ('HP', {'fields': ['rang', 'larp_rang', 'HPplus', 'HPplus_fix', 'HPplus_geistig']}),
        ('Kampf', {'fields': ['wesenschaden_waff_kampf', 'wesenschaden_andere_gestalt', 'crit_attack', 'crit_defense',
                              'initiative_bonus', 'reaktion_bonus', 'natürlicher_schadenswiderstand_bonus',
                              'natSchaWi_pro_erfolg_bonus', 'astralwiderstand_bonus', 'astralwiderstand_pro_erfolg_bonus',
                              "manaoverflow_bonus", "nat_regeneration_bonus", "immunsystem_bonus"]}),
        ('Rüstung', {'fields': ['natürlicher_schadenswiderstand_rüstung', 'natSchaWi_pro_erfolg_rüstung', 'rüstung_haltbarkeit']}),
        ('Kampagne', {'fields': ["ep", 'ep_stufe', 'ep_stufe_in_progress', "skilltree_stufe", "processing_notes"]}),
        ('Währungen', {'fields': ['ap', 'fp', 'fg', 'sp', "sp_fix", 'ip', 'tp', 'spF_wF', 'wp', 'zauberplätze', "geld", 'konzentration', "konzentration_fix", "prestige", "verzehr", "glück", "sanität", "limit_k_fix", "limit_g_fix", "limit_m_fix"]}),
        ('Geschreibsel', {'fields': ['notizen', 'persönlicheZiele', 'sonstige_items']}),
    ]

    inlines = [
        RelKlasseInline,
        RelWesenkraftInLine,
        RelAttributInline,
        RelGruppeInLine,
        RelFertigkeitInLine,
        RelSpezialfertigkeitInLine,
        RelWissensfertigkeitInLine, RelVorteilInLine,
        RelNachteilInLine, RelTalentInLine,
        AffektivitätInLine,
        RelGfsAbilityInLine,
        RelKlasseAbilityInLine,

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
        RelEngelsroboterInLine,
        RelRamschInLine,

        RelEffectInLine
    ]

    list_display = ['image_', 'name', 'eigentümer', "gfs", "ep_stufe", "larp", "in_erstellung"]

    list_filter = ['in_erstellung', 'larp', get_filter(Spieler, "name", ['eigentümer__name'])]
    search_fields = ['name', 'eigentümer__name']
    list_display_links = ["name"]

    save_on_top = True

    def has_module_permission(self, request):
        return request.spieler.is_spielleitung


    def image_(self, obj):
        return format_html(f"<img src='{obj.image.url}' style='max-width: 32px; max-height:32px;'>") if obj.image else "-"
    
    def get_queryset(self, request) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('eigentümer', "gfs", "tags")
