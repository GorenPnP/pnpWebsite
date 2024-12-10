import json
from django import forms

from crispy_forms.bootstrap import AppendedText, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, LayoutObject, TEMPLATE_PACK

from campaign.forms import ZauberplätzeWidget

from .models import *
from.form_utils import FormSet, PopulatedFormSet


AttributFormSet = PopulatedFormSet(Charakter, RelAttribut, "attribut", "attribut", ["attribut", "aktuellerWert", "aktuellerWert_bonus", "aktuellerWert_fix", "maxWert", "maxWert_fix"])
FertigkeitFormSet = PopulatedFormSet(Charakter, RelFertigkeit, "fertigkeit", "fertigkeit", ["fertigkeit", "fp", "fp_bonus"])
GruppenFormSet = PopulatedFormSet(Charakter, RelGruppe, "gruppe", "gruppe", ["gruppe", "fg"])
AffektivitätenFormSet = FormSet(Charakter, Affektivität, "affekt", ["name", "wert", "notizen"])
KlassenFormSet = FormSet(Charakter, RelKlasse, "klasse", ["klasse", "stufe"])
KlassenAbilityFormSet = FormSet(Charakter, RelKlasseAbility, "kl_ability", ["ability", "notizen"])
GfsAbilityFormSet = FormSet(Charakter, RelGfsAbility, "gfs_ability", ["ability", "notizen"])
SpezialfertigkeitenFormSet = FormSet(Charakter, RelSpezialfertigkeit, "spF", ["spezialfertigkeit", "stufe"])
WissensfertigkeitenFormSet = FormSet(Charakter, RelWissensfertigkeit, "wF", ["wissensfertigkeit", "stufe"])
VorteilFormSet = FormSet(Charakter, RelVorteil, "vorteil", ["teil", "attribut", "fertigkeit", "engelsroboter", "ip", "notizen"])
NachteilFormSet = FormSet(Charakter, RelNachteil, "nachteil", ["teil", "attribut", "fertigkeit", "engelsroboter", "ip", "notizen"])
TalentFormSet = FormSet(Charakter, RelTalent, "talent", ["talent"])
WesenkraftFormSet = FormSet(Charakter, RelWesenkraft, "wesenkraft", ["wesenkraft", "tier"])

# Shop
shop_fields = ["anz", "item", "stufe", "notizen"]
ShopItemFormSet = FormSet(Charakter, RelItem, "item", shop_fields)
ShopWaffenWerkzeugeFormSet = FormSet(Charakter, RelWaffen_Werkzeuge, "waffenWerkzeuge", shop_fields)
ShopMagazineFormSet = FormSet(Charakter, RelMagazin, "magazin", shop_fields)
ShopPfeilBolzenFormSet = FormSet(Charakter, RelPfeil_Bolzen, "pfeil_bolzen", shop_fields)
ShopSchusswaffenFormSet = FormSet(Charakter, RelSchusswaffen, "schusswaffe", shop_fields)
ShopMagAusrüstungFormSet = FormSet(Charakter, RelMagische_Ausrüstung, "mag_ausr", shop_fields)
ShopRitualeRunenFormSet = FormSet(Charakter, RelRituale_Runen, "rituale_runen", shop_fields)
ShopRüstungFormSet = FormSet(Charakter, RelRüstung, "rüstung", shop_fields)
ShopAusrüstungTechnikFormSet = FormSet(Charakter, RelAusrüstung_Technik, "ausr_technik", [*shop_fields, "selbst_eingebaut"])
ShopFahrzeugFormSet = FormSet(Charakter, RelFahrzeug, "fahrzeug", shop_fields)
ShopEinbautenFormSet = FormSet(Charakter, RelEinbauten, "einbauten", shop_fields)
ShopZauberFormSet = FormSet(Charakter, RelZauber, "zauber", [*shop_fields, "tier"])
ShopVergesseneZauberFormSet = FormSet(Charakter, RelVergessenerZauber, "verg_zauber", shop_fields)
ShopBegleiterFormSet = FormSet(Charakter, RelBegleiter, "begleiter", shop_fields)
ShopEngelsroboterFormSet = FormSet(Charakter, RelEngelsroboter, "engelsroboter", shop_fields)

# see https://dev.to/zxenia/django-inline-formsets-with-class-based-views-and-crispy-forms-14o6
class Formset(LayoutObject):

    def __init__(self, formset_name_in_context):
        self.formset_name_in_context = formset_name_in_context
        self.fields = []

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        formset = context[self.formset_name_in_context]
        return formset.render(template_name="character/_formset.html")


class CrispyZauberWidget(ZauberplätzeWidget):
    def decompress(self, value):
        value = json.loads(value) if value else {}
        return [value[str(i)] if str(i) in value else None for i in range(self.MIN_STUFE, self.MAX_STUFE+1)]

    def value_from_datadict(self, data, files, name):
        return json.dumps(super().value_from_datadict(data, files, name))

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Charakter
        fields = [
            "image", "name", "gewicht", "größe", "alter", "geschlecht", "sexualität", "beruf", "präf_arm", "religion", "hautfarbe", "haarfarbe", "augenfarbe", "gfs", "persönlichkeit",
            "manifest", "manifest_fix", "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust",
            "ap", "fp", "fg", "sp", "sp_fix", "ip", "tp", "zauberplätze", "geld", "konzentration", "konzentration_fix", "prestige", "verzehr", "glück", "sanität", "limit_k_fix", "limit_g_fix", "limit_m_fix",
            "ep", "ep_stufe", "skilltree_stufe",
            "HPplus_geistig", "HPplus", "HPplus_fix", "rang",
            "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "crit_attack", "crit_defense", "initiative_bonus", "reaktion_bonus", "natürlicher_schadenswiderstand_bonus", "natürlicher_schadenswiderstand_rüstung", "natSchaWi_pro_erfolg_bonus", "natSchaWi_pro_erfolg_rüstung", "rüstung_haltbarkeit", "astralwiderstand_bonus", "astralwiderstand_pro_erfolg_bonus", "manaoverflow_bonus", "nat_regeneration_bonus", "immunsystem_bonus",
    	    "notizen", "persönlicheZiele", "sonstige_items", "affektivitäten",
            "klassen", "klassen_fähigkeiten", "vorteile", "nachteile", "talente", "wesenkräfte",
            "attribute", "fertigkeiten","gruppen", "spezialfertigkeiten", "wissensfertigkeiten", "gfs_fähigkeiten",
            "items", "waffenWerkzeuge", "magazine", "pfeile_bolzen", "schusswaffen", "magischeAusrüstung", "rituale_runen", "rüstungen", "ausrüstungTechnik", "fahrzeuge", "einbauten", "zauber", "vergessene_zauber", "begleiter", "engelsroboter",
        ]

    zauberplätze = forms.JSONField(initial=dict, label="Zauberslots", required=False, widget=CrispyZauberWidget(attrs={'class': 'zauberplätze-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = ["name", "gfs", "ap", "fp", "fg", "sp", "ip", "tp", "geld", "konzentration"]
        for fieldname in required_fields:
            self.fields[fieldname].initial = 0 if fieldname in ["ap", "fp", "fg", "sp", "ip", "tp", "geld", "konzentration"] else None
            self.fields[fieldname].required = True

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Persönliches',
                    Fieldset(
                        "Aussehen & Merkmale",
                        "image", "name", AppendedText('gewicht', 'kg'), AppendedText('größe', 'cm'), AppendedText('alter', 'Jahre'), "hautfarbe", "haarfarbe", "augenfarbe", "geschlecht", "sexualität", "präf_arm", "persönlichkeit", "beruf", "religion",
                    ),
                    Fieldset(
                        "Geschreibsel",
                        "persönlicheZiele", "notizen",
                    ),
                    Fieldset(
                        "Affektivitäten",
                        Formset("affektivitäten"),
                    ),
                ),
                Tab(
                    "Gfs",
                    "gfs", "skilltree_stufe",
                    Fieldset(
                        "Gfs-Fähigkeiten",
                        Formset("gfs_fähigkeiten"),
                    ),
                    Fieldset(
                        "Wesenkräfte",
                        Formset("wesenkräfte"),
                    )
                ),
                Tab(
                    "Klassen",
                    Fieldset(
                        "Eigene Klassen",
                        Formset("klassen"),
                    ),
                    Fieldset(
                        "Klassen-Fähigkeiten",
                        Formset("klassen_fähigkeiten"),
                    ),
                ),
                Tab(
                    "Punkte",
                    Fieldset(
                        "Kampagne",
                        "ep", "ep_stufe",
                        "ap", "fp", "fg", "sp", "sp_fix", "ip", "tp", "zauberplätze",
                    ),
                    Fieldset(
                        "Ingame",
                        "geld", "konzentration", "konzentration_fix", "prestige", "verzehr", "glück", "sanität",
                    ),
                    Fieldset(
                        "Manifest",
                        AppendedText('manifest', '/ 10'), "sonstiger_manifestverlust", "notizen_sonstiger_manifestverlust", "manifest_fix",
                    ),
                ),
                Tab(
                    "Kampf & Boni",
                    Fieldset(
                        "Schaden machen",
                        "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "crit_attack",
                    ),
                    Fieldset(
                        "Schaden verhindern",
                        "crit_defense", "natürlicher_schadenswiderstand_rüstung", "natSchaWi_pro_erfolg_rüstung", "rüstung_haltbarkeit",
                    ),
                    Fieldset(
                        "HP",
                        "rang", "HPplus", "HPplus_fix", "HPplus_geistig"
                    ),
                    Fieldset(
                        "Boni",
                        "initiative_bonus", "reaktion_bonus", "natürlicher_schadenswiderstand_bonus", "natSchaWi_pro_erfolg_bonus", "astralwiderstand_bonus", "astralwiderstand_pro_erfolg_bonus", "manaoverflow_bonus", "nat_regeneration_bonus", "immunsystem_bonus"
                    ),
                ),
                Tab(
                    "Attribute",
                    Formset("attribute"),
                ),
                Tab(
                    "Fertigkeiten",
                    Fieldset(
                        "FP",
                        Formset("fertigkeiten"),
                    ),
                    Fieldset(
                        "FG",
                        Formset("gruppen"),
                    ),
                    Fieldset(
                        "Limits",
                        "limit_k_fix", "limit_g_fix", "limit_m_fix",
                    ),
                ),
                Tab(
                    "Spezial-& Wissensfertigkeiten",
                    HTML("<small class='d-block mb-4'>Stufe 0 bedeutet gerade bekommen, aber noch nicht gelernt.</small>"),
                    Fieldset(
                        "Spezialfertigkeiten",
                        Formset("spezialfertigkeiten"),
                    ),
                    Fieldset(
                        "Wissensfertigkeiten",
                        Formset("wissensfertigkeiten"),
                    ),
                ),
                Tab(
                    "Vor- & Nachteile",
                    HTML("<small class='d-block mb-4'>'Attribut', 'Fertigkeit', 'Engelsroboter' und 'Ip' spezifizieren den Effekt vom Vor-/Nachteil. Bitte nur ausfüllen, wenn es nötig ist. Im Zweifel gerne auch noch mal die Beschreibung lesen :)</small>"),
                    Fieldset(
                        "Vorteile",
                        Formset("vorteile"),
                    ),
                    Fieldset(
                        "Nachteile",
                        Formset("nachteile"),
                    ),
                ),
                Tab(
                    "Talente",
                    Formset("talente"),
                ),
                Tab(
                    "Inventar",
                    HTML("<small class='d-block mb-4'>'Stufe' bitte nur für Objekte ausfüllen bei denen es Sinn macht, z.B. Holoboard Stufe 3.</small>"),
                    Fieldset(
                        "Items",
                        Formset("items"),
                    ),
                    Fieldset(
                        "Waffen & Werkzeuge",
                        Formset("waffenWerkzeuge"),
                    ),
                    Fieldset(
                        "Schusswaffen",
                        Formset("schusswaffen"),
                    ),
                    Fieldset(
                        "Munition - Magazine",
                        Formset("magazine"),
                    ),
                    Fieldset(
                        "Munition - Pfeile & Bolzen",
                        Formset("pfeile_bolzen"),
                    ),
                    Fieldset(
                        "Magische Ausrüstung",
                        Formset("magischeAusrüstung"),
                    ),
                    Fieldset(
                        "Rituale & Runen",
                        Formset("rituale_runen"),
                    ),
                    Fieldset(
                        "Rüstungen",
                        Formset("rüstungen"),
                    ),
                    Fieldset(
                        "Ausrüstung / Technik",
                        Formset("ausrüstungTechnik"),
                    ),
                    Fieldset(
                        "Einbauten (Cyber- & Bioware)",
                        Formset("einbauten"),
                    ),
                    Fieldset(
                        "Fahrzeuge",
                        Formset("fahrzeuge"),
                    ),
                    Fieldset(
                        "Zauber",
                        Formset("zauber"),
                    ),
                    Fieldset(
                        "Vergessene Zauber",
                        Formset("vergessene_zauber"),
                    ),
                    Fieldset(
                        "Begleiter",
                        Formset("begleiter"),
                    ),
                    Fieldset(
                        "Engelsroboter",
                        Formset("engelsroboter"),
                    ),
                    Fieldset(
                        "Sonstiges",
                        "sonstige_items",
                    ),
                ),
                css_class="mb-4"
            ),
            Submit("submit", 'Charakter anlegen', css_class='btn-default mt-5'),
        )

