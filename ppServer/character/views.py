from typing import Any, Dict

from django.apps import apps
from django.contrib import messages
from django.db.models import Value, F
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

import django_tables2 as tables

from base.abstract_views import GenericTable
from log.create_log import render_number
from log.models import Log
from ppServer.decorators import verified_account
from ppServer.mixins import VerifiedAccountMixin

from .models import *


class CharacterListView(VerifiedAccountMixin, TemplateView):
    template_name = "character/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        char_qs = Charakter.objects.prefetch_related("eigentümer").filter(in_erstellung=False).order_by('name')
        if not self.request.spieler.is_spielleiter:
            char_qs = char_qs.filter(eigentümer=self.request.spieler.instance)

        return {
            'charaktere': char_qs,
            'topic': "Charaktere",
            "plus": "+ Charakter",
            "plus_url": reverse('create:gfs')
        }


class ShowView(VerifiedAccountMixin, DetailView):
    template_name = "character/show.html"
    model = Charakter

    def get(self, request, *args, **kwargs):
        if not self.request.spieler.is_spielleiter and not Charakter.objects.filter(pk=kwargs["pk"], eigentümer=self.request.spieler.instance).exists():
            return redirect("character:index")
        
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = self.get_object()

        return super().get_context_data(
            **kwargs,
            topic = char.name,
            app_index = "Charaktere",
            app_index_url = reverse("character:index"),
            plus = "History",
            plus_url = reverse("character:history", args=[char.id]),

            **self.get_personal(char),
            **self.get_resources(char),
            **self.get_calculated(char),
            **self.get_attr(char),
            **self.get_fert(char),
            **self.get_hp(char),
            **self.get_spF_wF(char),
            **self.get_teils(char),
            **self.get_wesenkraft(char),
            **self.get_talent(char),
            **self.get_gfs_ability(char),
            **self.get_affektivität(char),
            **self.get_inventory(char),
            **self.get_zauber(char),
            **self.get_ritual(char),
            **self.get_nahkampf(char),
            **self.get_fernkampf(char),
        )
    
    def get_object(self) -> Charakter:
        qs = Charakter.objects.prefetch_related(
            "gfs", "persönlichkeit", "religion", "beruf", "relfertigkeit_set__fertigkeit__attribut", "relgruppe_set",
            "relattribut_set__attribut", "relwesenkraft_set__wesenkraft", "reltalent_set__talent",
            "relgfsability_set__ability", "affektivität_set", "relvorteil_set__teil", "relnachteil_set__teil",
            "relzauber_set__item", "relrituale_runen_set__item", "relschusswaffen_set__item", "relwaffen_werkzeuge_set__item",
            "relmagazin_set__item", "relpfeil_bolzen_set__item", "relmagische_ausrüstung_set__item", "relrüstung_set__item",
            "relausrüstung_technik_set__item", "relfahrzeug_set__item", "releinbauten_set__item", "relalchemie_set__item",
            "reltinker_set__item", "relbegleiter_set__item",
            "relspezialfertigkeit_set__spezialfertigkeit__attr1", "relspezialfertigkeit_set__spezialfertigkeit__attr2", "relspezialfertigkeit_set__spezialfertigkeit__ausgleich",
            "relwissensfertigkeit_set__wissensfertigkeit__attr1", "relwissensfertigkeit_set__wissensfertigkeit__attr2", "relwissensfertigkeit_set__wissensfertigkeit__attr3", "relwissensfertigkeit_set__wissensfertigkeit__fertigkeit",
        )
        return super().get_object(qs)
    

    def get_personal(self, char):
        fields = [
                ["Name", char.name],
                ["Gfs (Stufe)", f"{char.gfs.titel if char.gfs is not None else '-'} ({char.skilltree_stufe})"],
                ["Persönlichkeit", ", ".join(char.persönlichkeit.all().values_list("titel", flat=True))],
                ["Geschlecht", char.geschlecht],
                ["Alter", char.alter],
                ["Größe", f"{char.größe} cm"],
                ["Gewicht", f"{char.gewicht} kg"],
                ["Religion", char.religion.titel if char.religion else ""],
                ["Augenfarbe", char.augenfarbe],
                ["Hautfarbe", char.hautfarbe],
                ["Haarfarbe", char.haarfarbe],
                ["Sexualität", char.sexualität],
                ["präferierter Arm", char.präf_arm],
                ["Beruf", char.beruf.titel if char.beruf else ""],
                ["Notizen", format_html(re.sub("\n", "<br>", char.notizen, 0, re.MULTILINE))],
                ["persönliche Ziele", format_html(re.sub("\n", "<br>", char.persönlicheZiele, 0, re.MULTILINE))],
        ]
        return {
            "personal__fields": [[k, v if v else "-"] for k, v in fields]
        }

    def get_resources(self, char):
        fields = [
            ["Geld", f"{render_number(char.geld)} Drachmen"],
            ["SP", char.sp],
            ["IP", char.ip],
            ["TP", char.tp],
            ["EP (Stufe)", f"{render_number(char.ep)} ({char.ep_stufe})"],
            ["Prestige", render_number(char.prestige)],
            ["Verzehr", render_number(char.verzehr)],
            ["Manifest", char.manifest - char.sonstiger_manifestverlust if char.manifest_fix is None else char.manifest_fix],
            ["Konzentration", char.konzentration if char.konzentration_fix is None else char.konzentration_fix],
            ["Krit-Angriff", char.crit_attack],
            ["Krit-Verteidigung", char.crit_defense],
        ]
        return {
            "resources__fields": [[k, v if v else 0] for k, v in fields]
        }
    
    def get_calculated(self, char):
        MA_relattr = char.relattribut_set.get(attribut__titel="MA")
        MA_raw = MA_relattr.aktuellerWert if MA_relattr.aktuellerWert_fix is None else MA_relattr.aktuellerWert_fix
        attrs = { rel.attribut.titel: rel.aktuell() for rel in char.relattribut_set.all() }
        fg = { rel.gruppe: rel.fg for rel in RelGruppe.objects.filter(char=char) }
        ferts = { rel.fertigkeit.titel: rel.fp + rel.fp_bonus + attrs[rel.fertigkeit.attribut.titel] + fg[rel.fertigkeit.gruppe] for rel in char.relfertigkeit_set.all() }

        num = lambda n: "{0:.1f}".format(n) if type(n) is float else n

        return {
            "calculated__fields": [
                ["Limits (k | g | m)", f'{num((attrs["SCH"] + attrs["ST"] + attrs["VER"] + attrs["GES"]) / 2) if char.limit_k_fix is None else char.limit_k_fix} | {num((attrs["IN"] + attrs["WK"] + attrs["UM"]) / 2) if char.limit_g_fix is None else char.limit_g_fix} | {num((attrs["MA"] + attrs["WK"]) / 2) if char.limit_m_fix is None else char.limit_m_fix}'],
                ["Initiative", num(attrs["SCH"]*2 + attrs["WK"] + attrs["GES"] + char.initiative_bonus)],
                ["Manaoverflow", num((attrs["WK"] + MA_raw)*3 + char.manaoverflow_bonus)],

                ["Astral-Widerstand", num(attrs["MA"] + attrs["WK"] + char.astralwiderstand_bonus)],
                ["Astrale Schadensverhinderung", f'{1+ num(math.floor(min(attrs["WK"], MA_raw) / 6)) + char.astralwiderstand_pro_erfolg_bonus}HP / Erfolg'],
                ["Reaktion", num(attrs["SCH"] + attrs["GES"] + char.reaktion_bonus)],
                ["nat. Schadenswiderstand", num(attrs["ST"] + attrs["VER"] + char.natürlicher_schadenswiderstand_bonus)],
                ["Schadenswiderstand Rüstung", char.natürlicher_schadenswiderstand_rüstung],
                ["nat. Schadensverhinderung", f'{1+ num(math.floor(min(attrs["ST"], attrs["VER"]) / 6) + char.natSchaWi_pro_erfolg_bonus)}HP / Erfolg'],
                ["Schadensverhinderung Rüstung", f'{char.natSchaWi_pro_erfolg_rüstung}HP / Erfolg'],
                ["Haltbarkeit der Rüstung", char.rüstung_haltbarkeit],
                ["Intuition", num((attrs["IN"] + 2*attrs["SCH"]) / 2)],
                ["Geh-/ Lauf-/ Sprintrate", f'{num(attrs["SCH"]*2)} | {num(attrs["SCH"]*4)} | {num(attrs["SCH"]*4 + ferts["Laufen"])} m / 6sek'],
                ["Bewegung Astral", f'{num(2*attrs["MA"]*(attrs["WK"] + attrs["SCH"]))}m / 6sek'],
                ["Schwimmen", f'{num(attrs["SCH"]*2/3 + ferts["Schwimmen"]/5)}m / 6sek'],
                ["Tauchen", f'{num(attrs["SCH"]*2/5 + ferts["Schwimmen"]/5)}m / 6sek'],
                ["Tragfähigkeit", f'{num(attrs["ST"]*3 + attrs["GES"])}kg'],
                ["Heben", f'{num(attrs["ST"]*4 + attrs["N"])}kg / Erfolg'],
                ["Ersticken", f'nach {num(attrs["ST"]*3 + attrs["VER"]*3)} sek'],
                ["Immunsystem (W100)", num(attrs["ST"]*4 + attrs["VER"]*3 + attrs["WK"]*2 + char.immunsystem_bonus)],
                ["Glück", char.glück],
                ["Sanität", char.sanität],
                ["Regeneration", f'{num(attrs["ST"] + attrs["WK"] + char.nat_regeneration_bonus)}HP / Tag'],
            ]
        }

    def get_attr(self, char):

        class AttrTable(tables.Table):
            class Meta:
                model = RelAttribut
                fields = ("attribut__titel", "aktuellerWert", "maxWert")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_attribut__titel(self, value, record):
                return f"{record.attribut.beschreibung} ({value})"

            def render_aktuellerWert(self, value, record):
                if record.aktuellerWert_fix is not None:
                    return record.aktuellerWert_fix
                return str(value) + (f"+{record.aktuellerWert_bonus}" if record.aktuellerWert_bonus else "")

            def render_maxWert(self, value, record):
                return value if record.maxWert_fix is None else record.maxWert_fix

        return {
            "attr__table": AttrTable(char.relattribut_set.all()),
        }

    def get_fert(self, char):
        class FertTable(tables.Table):
            class Meta:
                model = RelFertigkeit
                fields = ("fertigkeit__titel", "fertigkeit__attribut__titel", "fp", "fg", "fp_bonus", "pool", "fertigkeit__limit","fertigkeit__gruppe")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}
                row_attrs = {
                    "class": lambda record:
                        ("impro_possible" if record["impro_possible"] else " ") +
                        ("fert_impossible" if not record["impro_possible"] and record["fp"] == 0 else " ")
                }

            def render_fg(self, value):
                return format_html(f"<i>{value}</i>")

            def render_fp_bonus(self, value):
                return f"+{value}" if value else "-"

            def render_pool(self, value, record):
                return format_html(f"<b>{value}</b>") if record["impro_possible"] or record["fp"] else "-"

            def render_fertigkeit__limit(self, value):
                return [name for token, name in enums.limit_enum if token == value][0]

            def render_fertigkeit__gruppe(self, value):
                return [name for token, name in enums.gruppen_enum if token == value][0]

        gruppen = {rel.gruppe: rel.fg for rel in char.relgruppe_set.all()}
        qs_fert = char.relfertigkeit_set.all().prefetch_related("fertigkeit__attribut").annotate(
            fg=Value(1),
            pool=Value(1),
            impro_possible=F("fertigkeit__impro_possible"),
        ).values("fertigkeit__titel", "fertigkeit__attribut__titel", "fp", "fg", "fp_bonus", "pool", "fertigkeit__limit", "fertigkeit__gruppe", "impro_possible")

        for fert in qs_fert:
            fert["fg"] = gruppen[fert["fertigkeit__gruppe"]]

            relattr = char.relattribut_set.get(attribut__titel=fert["fertigkeit__attribut__titel"])
            aktuell = relattr.aktuell()
            fert["pool"] = sum([aktuell, fert["fp"], fert["fp_bonus"], fert["fg"]])

        return {
            "fert__table": FertTable(qs_fert),
        }

    def get_hp(self, char):
        khp = [
            char.relattribut_set.get(attribut__titel="ST").aktuell() * 5,
            char.ep_stufe * 2 + math.floor(char.larp_rang / 20),
            math.floor(char.rang / 10),
            char.HPplus_fix if char.HPplus_fix is not None else char.HPplus,
        ]
        ghp = [
            char.relattribut_set.get(attribut__titel="WK").aktuell() * 5,
            char.HPplus_geistig,
            math.ceil(char.larp_rang / 20),
        ]

        fields_khp = [
            ["HP durch Stärke", khp[0]],
            ["HP durch LARP-Ränge" if char.larp else "HP durch Stufe", khp[1]],
            ["HP durch Ränge", khp[2]],
            ["HP-Bonus", khp[3]],
            [format_html("<b>Körperliche HP</b>"), format_html(f"<b>{sum(khp)}</b>")],
        ]
        fields_ghp = [
            ["HP durch Willenskraft", ghp[0]],
            ["HP-Bonus", ghp[1]],
            [format_html("<b>geistige HP</b>"), format_html(f"<b>{sum(ghp)}</b>")],
        ]
        if char.larp:
            fields_ghp.insert(1, ["HP durch LARP-Ränge", ghp[2]])

        return {
            "hp__k_fields": fields_khp,
            "hp__g_fields": fields_ghp,
        }
    
    def get_spF_wF(self, char):
        attr = {rel.attribut.titel: rel.aktuell() for rel in char.relattribut_set.all()}
        fg = {rel.gruppe: rel.fg for rel in char.relgruppe_set.all()}
        fert = {rel.fertigkeit.titel: attr[rel.fertigkeit.attribut.titel] + fg[rel.fertigkeit.gruppe] + rel.fp + rel.fp_bonus for rel in char.relfertigkeit_set.prefetch_related("fertigkeit").all()}

        class SpezialTable(tables.Table):
            class Meta:
                model = RelSpezialfertigkeit
                fields = (
                    "spezialfertigkeit__titel", "spezialfertigkeit__attr1__titel", "spezialfertigkeit__attr2__titel", "gesamt",
                    "spezialfertigkeit__ausgleich", "korrektur", "wp", "w20_probe"
                )
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            spezialfertigkeit__attr1__titel = tables.Column(verbose_name="Attribut 1")
            spezialfertigkeit__attr2__titel = tables.Column(verbose_name="Attribut 2")

            def render_gesamt(self, value, record):
                return attr[record.spezialfertigkeit.attr1.titel] + attr[record.spezialfertigkeit.attr2.titel] -5

            def render_korrektur(self, value, record):
                return math.floor(sum([fert[f.titel] for f in record.spezialfertigkeit.ausgleich.all()]) / 2 + 0.5)
            
            def render_w20_probe(self, value, record):
                return attr[record.spezialfertigkeit.attr1.titel] + attr[record.spezialfertigkeit.attr2.titel] -5 + record.wp


        class WissenTable(tables.Table):
            class Meta:
                model = RelWissensfertigkeit
                fields = (
                    "wissensfertigkeit__titel", "attribute", "gesamt",
                    "wissensfertigkeit__fertigkeit", "wp", "schwellwert"
                )
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_attribute(self, value, record):
                return " + ".join([record.wissensfertigkeit.attr1.titel, record.wissensfertigkeit.attr2.titel, record.wissensfertigkeit.attr3.titel])

            def render_gesamt(self, value, record):
                return sum([
                    attr[record.wissensfertigkeit.attr1.titel],
                    attr[record.wissensfertigkeit.attr2.titel],
                    attr[record.wissensfertigkeit.attr3.titel]
                ])
            
            def render_schwellwert(self, value, record):
                return sum([
                    attr[record.wissensfertigkeit.attr1.titel],
                    attr[record.wissensfertigkeit.attr2.titel],
                    attr[record.wissensfertigkeit.attr3.titel],
                    sum([fert[rel.fertigkeit.titel] for rel in char.relfertigkeit_set.filter(fertigkeit__in=record.wissensfertigkeit.fertigkeit.all())]),
                    record.wp * Wissensfertigkeit.WISSENSF_STUFENFAKTOR
                ])


        spezi_qs = char.relspezialfertigkeit_set.all().annotate(
            gesamt=Value(1),
            korrektur=Value(1),
            w20_probe=Value(1),
            wp=F("stufe")
        )

        wissen_qs = char.relwissensfertigkeit_set.all().annotate(
            attribute=Value("attr"),
            gesamt=Value(1),
            wp=F("stufe"),
            schwellwert=Value(1)
        )

        return {
            "spF_wF_spezial": SpezialTable(spezi_qs),
            "spF_wF_wissen": WissenTable(wissen_qs),
        }

    def get_teils(self, char):
        class TeilTable(tables.Table):
            class Meta:
                model = RelTeil
                fields = ("teil__titel", "teil__beschreibung", "notiz")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_notiz(self, value, record):
                return record.full_addons() or "—"

        return {
            "vorteil__table": TeilTable(char.relvorteil_set.all().annotate(notiz=Value(" "))),
            "nachteil__table": TeilTable(char.relnachteil_set.all().annotate(notiz=Value(" "))),
        }

    def get_wesenkraft(self, char):
        class WesenkraftTable(tables.Table):
            class Meta:
                model = RelWesenkraft
                fields = ("wesenkraft__titel", "tier", "wesenkraft__probe", "wesenkraft__wirkung", "wesenkraft__manaverbrauch")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_wesenkraft__wirkung(self, value):
                regex = "Tier [0IVX]+:"
                return format_html(re.sub(regex, lambda match: f"<br><b>{match.group(0)}</b>", value))

        return {
            "wesenkraft__table": WesenkraftTable(char.relwesenkraft_set.all())
        }

    def get_talent(self, char):
        class TalentTable(tables.Table):
            class Meta:
                model = RelTalent
                fields = ("talent__titel", "talent__beschreibung")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

        return {
            "talent__table": TalentTable(char.reltalent_set.all())
        }

    def get_gfs_ability(self, char):
        class GfsAbilityTable(tables.Table):
            class Meta:
                model = RelGfsAbility
                fields = ("ability__name", "ability__beschreibung", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

        return {
            "gfs_ability__table": GfsAbilityTable(char.relgfsability_set.all())
        }

    def get_affektivität(self, char):
        class AffektivitätTable(tables.Table):
            class Meta:
                model = Affektivität
                fields = ("name", "wert", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

        return {
            "affektivität__table": AffektivitätTable(char.affektivität_set.all())
        }

    def get_inventory(self, char):
        class InventoryTable(tables.Table):
            class Meta:
                model = RelShop
                fields = ("anz", "item__name", "item__beschreibung", "notizen", "use")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            use = tables.Column(verbose_name="")

            def render_use(self, value, record):
                href = reverse("character:use_item", args=[record["model"], record["pk"]])
                return format_html(f"<a class='btn btn-sm btn-danger' href='{href}'>1 verbrauchen</a>")

        # helper function to format all relshop items the same way
        to_dict = lambda qs, model: qs.all()\
            .annotate(use=Value("-"), model=Value(model))\
            .values("anz", "item__name", "item__beschreibung", "notizen", "use", "model", "pk")

        qs = to_dict(char.relitem_set, "relitem").union(
            to_dict(char.relmagazin_set.all(), "relmagazin"),
            to_dict(char.relpfeil_bolzen_set.all(), "relpfeil_bolzen"),
            to_dict(char.relmagische_ausrüstung_set.all(), "relmagische_ausrüstung"),
            to_dict(char.relrüstung_set.all(), "relrüstung"),
            to_dict(char.relausrüstung_technik_set.all(), "relausrüstung_technik"),
            to_dict(char.relfahrzeug_set.all(), "relfahrzeug"),
            to_dict(char.releinbauten_set.all(), "releinbauten"),
            to_dict(char.relalchemie_set.all(), "relalchemie"),
            to_dict(char.reltinker_set.all(), "reltinker"),
            to_dict(char.relbegleiter_set.all(), "relbegleiter"),
        )

        return {
            "inventory__table": InventoryTable(qs),
            "inventory__random_items": format_html(re.sub("\n", "<br>", char.sonstige_items, 0, re.MULTILINE))
        }

    def get_zauber(self, char):
        class ZauberTable(tables.Table):
            class Meta:
                model = RelZauber
                fields = ("item__name", "tier", "item__beschreibung", "item__manaverbrauch", "item__astralschaden")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__beschreibung(self, value):
                regex = "Tier [0IVX]+:"
                return format_html(re.sub(regex, lambda match: f"<br><b>{match.group(0)}</b>", value))

            def render_item__astralschaden(self, value, record):
                if record.item.astralsch_is_direct:
                    return f"{value} (direkt!)"
                return value

        return {
            "zauber__table": ZauberTable(char.relzauber_set.all())
        }

    def get_ritual(self, char):
        class RitualTable(tables.Table):
            class Meta:
                model = RelRituale_Runen
                fields = ("anz", "item__name", "stufe", "item__beschreibung", "item__kategorie")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

        return {
            "ritual__table": RitualTable(char.relrituale_runen_set.all())
        }

    def get_nahkampf(self, char):
        class WaffenTable(tables.Table):
            class Meta:
                model = RelWaffen_Werkzeuge
                fields = ("anz", "item__name", "item__bs", "item__zs", "item__dk", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__bs(self, value, record):
                return f"{value} (ab {record.item.erfolge})"

        return {
            "nahkampf__table": WaffenTable(char.relwaffen_werkzeuge_set.all())
        }

    def get_fernkampf(self, char):
        class SchusswaffenTable(tables.Table):
            class Meta:
                model = RelSchusswaffen
                fields = ("anz", "item__name", "item__bs", "item__zs", "item__dk", "item__präzision", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__bs(self, value, record):
                return f"{value} (ab {record.item.erfolge})"

        return {
            "fernkampf__table": SchusswaffenTable(char.relschusswaffen_set.all())
        }


class HistoryView(VerifiedAccountMixin, tables.SingleTableMixin, TemplateView):

    class Table(GenericTable):
        class Meta:
            model = Log
            fields = ["spieler", "art", "notizen", "kosten", "timestamp"]
            attrs = GenericTable.Meta.attrs

    template_name = "character/history.html"
    model = Log
    table_class=Table
    
    def get_table_data(self):
        char = get_object_or_404(Charakter, pk=self.kwargs["pk"])
        return Log.objects.filter(char=char, art__in=("s", "u", "i", "j"))
    

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = get_object_or_404(Charakter, pk=self.kwargs["pk"])

        return super().get_context_data(
            **kwargs,
            topic = "History",
            app_index=char.name,
            app_index_url=reverse("character:show", args=[char.id]),
            priotable=char.processing_notes["priotable"] if "priotable" in char.processing_notes else None,
        )


@verified_account
def use_relshop(request, relshop_model, pk):

    try:
        Model = apps.get_model('character', relshop_model)
        # assert model
        if not issubclass(Model, RelShop): raise LookupError()
    except LookupError:
        messages.error(request, "Anfrage fehlerhaft")
        return redirect("character:index")

    # assert user requesting to use an item
    if not request.spieler.is_spielleiter and not Model.objects.filter(pk=pk, char__eigentümer=request.spieler.instance).exists():
        messages.error(request, "Es ist nicht dein Charakter, von dem du Items benutzen willst.")
        return redirect("character:index")

    # assert item existance
    rel_shop = Model.objects.prefetch_related("char__eigentümer", "item").filter(pk=pk).first()
    if not rel_shop:
        messages.error(request, "Item konnte nicht im Inventar gefunden werden.")
        return redirect("character:index")

    char = rel_shop.char
    item_name = rel_shop.item.name

    # use item
    if rel_shop.anz == 1:
        rel_shop.delete()
    else:
        rel_shop.anz -= 1
        rel_shop.save(update_fields=["anz"])

    # log usage
    Log.objects.create(
        spieler=request.spieler.instance,
        char=char,
        art="j", # Inventar-Item verbraucht
        kosten="",
        notizen=f"1x {item_name}",
    )

    messages.success(request, f'Du hast von "{item_name}" 1 verbraucht')
    return redirect(reverse("character:show", args=[char.id]))