from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.forms.widgets import Widget as Widget
from django.http.request import HttpRequest
from django.utils.html import format_html

from ..models import *


class RelInlineAdmin(admin.TabularInline):
    """ base permissions for Rel.. models """

    extra = 1
    show_change_link = False

    def _is_visible(self, request, obj = ...) -> bool:
        return request.spieler.is_spielleiter or not obj or ("trägt seine chars ein" in request.spieler.groups and obj.eigentümer == request.spieler.instance)

    def has_add_permission(self, request: HttpRequest, obj: Charakter = None) -> bool:
        return self._is_visible(request, obj)

    def has_change_permission(self, request: HttpRequest, obj = ...) -> bool:
        return self._is_visible(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj = ...) -> bool:
        return request.spieler.is_spielleiter

    def has_view_permission(self, request: HttpRequest, obj = ...) -> bool:
        return self._is_visible(request, obj)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        related_char_id = request.resolver_match.kwargs['object_id']
        return super().get_queryset(request).prefetch_related("char__eigentümer").filter(char__id=related_char_id)

class ReadonlyRelInlineAdmin(RelInlineAdmin):
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=...) -> bool:
        return self._is_visible(request, obj)

    def has_view_permission(self, request: HttpRequest, obj=...) -> bool:
        return self._is_visible(request, obj)




class RelPersönlichkeitInline(RelInlineAdmin):
    model = RelPersönlichkeit

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("persönlichkeit")

class RelAttributInline(ReadonlyRelInlineAdmin):
    fields = ['attribut', 'aktuellerWert', 'aktuellerWert_temp', 'aktuellerWert_bonus', 'maxWert', 'maxWert_temp']
    readonly_fields = ['attribut']
    model = RelAttribut


    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("attribut")


class RelGruppeInLine(ReadonlyRelInlineAdmin):
    fields = ['gruppe', 'fg', "fg_temp"]
    readonly_fields = ['gruppe']
    model = RelGruppe


class RelFertigkeitInLine(ReadonlyRelInlineAdmin):
    fields = ['fertigkeit', 'fp', "fp_temp", 'fp_bonus']
    readonly_fields = ['fertigkeit']
    model = RelFertigkeit

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("fertigkeit__attribut")


class RelWesenkraftInLine(RelInlineAdmin):
    model = RelWesenkraft

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("wesenkraft")


class RelSpezialfertigkeitInLine(RelInlineAdmin):
    model = RelSpezialfertigkeit

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("spezialfertigkeit__attr1", "spezialfertigkeit__attr2")


class RelWissensfertigkeitInLine(RelInlineAdmin):
    model = RelWissensfertigkeit

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("wissensfertigkeit__attr1", "wissensfertigkeit__attr2", "wissensfertigkeit__attr3")


class AffektivitätInLine(RelInlineAdmin):
    model = Affektivität
    exclude = ['grad', 'umgang']


class RelGfsAbilityInLine(RelInlineAdmin):
    model = RelGfsAbility
    fields = ["ability", "notizen"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('ability')


class RelVorteilInLine(RelInlineAdmin):
    model = RelVorteil
    fields = ["teil", "attribut", "fertigkeit", "engelsroboter", "notizen", "ip", "is_sellable", "will_create"]
    exclude = ["anzahl"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit__attribut', 'engelsroboter')


class RelNachteilInLine(RelInlineAdmin):
    model = RelNachteil
    fields = ["teil", "attribut", "fertigkeit", "notizen", "ip", "is_sellable", "will_create"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('teil', 'attribut', 'fertigkeit__attribut')


class RelTalentInLine(RelInlineAdmin):
    model = RelTalent
    fields = ["talent"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('talent')

########## generic (st)shop ##############

class RelShopInLine(RelInlineAdmin):
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
                              'initiative_bonus', 'reaktion_bonus', 'natürlicher_schadenswiderstand_bonus', 'astralwiderstand_bonus', "manaoverflow_bonus"]}),

        ('Kampagne', {'fields': ["ep", 'ep_stufe', 'ep_stufe_in_progress', "skilltree_stufe", "processing_notes"]}),
        ('Währungen', {'fields': ['ap', 'fp', 'fg', 'sp', 'ip', 'tp', 'spF_wF', 'wp', 'zauberplätze', "geld", 'konzentration', "prestige", "verzehr"]}),
        ('Geschreibsel', {'fields': ['notizen', 'persönlicheZiele', 'sonstige_items']}),
    ]

    inlines = [
        # RelGfsInline,
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

    def _is_spielleiter_or_adds_chars(self, request, obj):
        return request.spieler.is_spielleiter or not obj or ("trägt seine chars ein" in request.spieler.groups and obj.eigentümer == request.spieler.instance)

    def _only_adds_chars(self, request):
        return not request.spieler.is_spielleiter and "trägt seine chars ein" in request.spieler.groups

    # permissions

    def has_add_permission(self, request: HttpRequest) -> bool:
        return self._is_spielleiter_or_adds_chars(request, None)

    def has_change_permission(self, request: HttpRequest, obj = None) -> bool:
        return self._is_spielleiter_or_adds_chars(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj = None) -> bool:
        return request.spieler.is_spielleiter

    def has_view_permission(self, request: HttpRequest, obj = None) -> bool:
        return self._is_spielleiter_or_adds_chars(request, obj)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('eigentümer', "gfs__wesen")
    
        if self._only_adds_chars(request): return qs.filter(eigentümer=request.spieler.instance)
        return qs

    # specials for "trägt seine chars ein"-group

    
    # set "eigentümer" to readonly if user has the "trägt seine chars ein"-group
    def get_readonly_fields(self, request: HttpRequest, obj = ...) -> list[str] or tuple[Any, ...]:
        fields = list(super().get_readonly_fields(request, obj))

        if self._only_adds_chars(request): return fields + ["eigentümer"]
        return fields
        
    
    # set "eigentümer" to logged-in-user if user has the "trägt seine chars ein"-group
    def save_form(self, request: Any, form: Any, change: Any) -> Any:
        char = super().save_form(request, form, change)

        if self._only_adds_chars(request):
            char.eigentümer = self.request.spieler.instance
            char.save()
        return char
