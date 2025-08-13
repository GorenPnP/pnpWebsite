from typing import Any, Dict

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.db.models import Value, F, CharField, OuterRef
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

import django_tables2 as tables

from base.abstract_views import GenericTable
from effect.models import RelEffect
from log.create_log import render_number
from log.models import Log
from ppServer.decorators import verified_account
from ppServer.mixins import VerifiedAccountMixin
from ppServer.utils import ConcatSubquery

from .forms import *
from .models import *


class CharacterListView(VerifiedAccountMixin, TemplateView):
    template_name = "character/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        char_qs = Charakter.objects.prefetch_related("eigentümer", "tags").filter(in_erstellung=False).order_by('name')
        if not self.request.spieler.is_spielleitung:
            char_qs = char_qs.filter(eigentümer=self.request.spieler.instance)

        return {
            'charaktere': char_qs,
            "num_all_chars": char_qs.count(),
            "tags": Tag.objects.filter(spieler=self.request.spieler.instance).annotate(num=Count("charakter")).order_by("name"),
            'topic': "Charaktere",
            "plus": "+ Charakter",
            "plus_url": reverse('create:gfs'),
        }
    
    def get(self, request, *args, **kwargs):
        tagname = self.request.GET["tag"] if "tag" in self.request.GET else None
        context = self.get_context_data(**kwargs)

        if tagname and Tag.objects.filter(name=tagname, spieler=self.request.spieler.instance).exists():
            context["charaktere"] = context["charaktere"].filter(tags__name=tagname)

        return self.render_to_response(context)
    
    def post(self, *args, **kwargs):
        create_tag_form = CreateTagForm({"name": self.request.POST.get("name"), "spieler": self.request.spieler.instance})
        create_tag_form.full_clean()
        if create_tag_form.is_valid():
            create_tag_form.save()

            messages.success(self.request, "Neuer Tag angelegt")
        else:
            messages.error(self.request, format_html(f"Tag konnte nicht angelegt werden: {create_tag_form.errors}"))
        return redirect(reverse("character:index"))


class ShowView(VerifiedAccountMixin, DetailView):
    template_name = "character/show.html"
    model = Charakter
    queryset = Charakter.objects.prefetch_related(
        "gfs", "persönlichkeit", "religion", "beruf", "relfertigkeit_set__fertigkeit__attribut", "relgruppe_set",
        "relklasse_set__klasse", "relklasseability_set__ability", "relattribut_set__attribut", "relwesenkraft_set__wesenkraft", "reltalent_set__talent",
        "relgfsability_set__ability", "affektivität_set",
        "relzauber_set__item", "relrituale_runen_set__item", "relschusswaffen_set__item", "relwaffen_werkzeuge_set__item",
        "relmagazin_set__item", "relpfeil_bolzen_set__item", "relmagische_ausrüstung_set__item", "relrüstung_set__item",
        "relausrüstung_technik_set__item", "relfahrzeug_set__item", "releinbauten_set__item", "relalchemie_set__item",
        "reltinker_set__item", "relbegleiter_set__item",
    )

    def get(self, request, *args, **kwargs):
        if not self.request.spieler.is_spielleitung and not Charakter.objects.filter(pk=kwargs["pk"], eigentümer=self.request.spieler.instance).exists():
            return redirect("character:index")
        
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        char = context["object"]
        self._rel_attribute = {rel.attribut.titel: rel for rel in char.relattribut_set.all()}
        self._gruppen_fg = {rel.gruppe: rel.fg for rel in char.relgruppe_set.all()}

        return {
            **context,
            "topic":  char.name,
            "app_index": "Charaktere",
            "app_index_url": reverse("character:index"),
            "plus": "History",
            "plus_url": reverse("character:history", args=[char.id]),

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
            **self.get_klasse_ability(char),
            **self.get_affektivität(char),
            **self.get_inventory(char),
            **self.get_zauber(char),
            **self.get_ritual(char),
            **self.get_nahkampf(char),
            **self.get_fernkampf(char),
            **self.get_effekte(char),
        }
    

    def get_personal(self, char):
        gfs = f"<a class='text-white' href='{reverse('wiki:stufenplan', args=[char.gfs.id])}'>{char.gfs.titel}</a>" if char.gfs is not None else '-'
        fields = [
                ["Name", char.name],
                ["Gfs (Stufe)", format_html(f"{gfs} ({char.skilltree_stufe})")],
                ["Klassen (Stufe)", ", ".join([f"{rel.klasse.titel} ({rel.stufe})" for rel in char.relklasse_set.all()]) or "-"],
                ["Persönlichkeit", char.persönlichkeit.titel if char.persönlichkeit else "-"],
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
        MA_relattr = self._rel_attribute["MA"]
        MA_raw = MA_relattr.aktuellerWert if MA_relattr.aktuellerWert_fix is None else MA_relattr.aktuellerWert_fix
        attrs = { attr_name: rel.aktuell() for attr_name, rel in self._rel_attribute.items() }
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

        qs_fert = char.relfertigkeit_set.all().prefetch_related("fertigkeit__attribut").annotate(
            fg=Value(1),
            pool=Value(1),
            impro_possible=F("fertigkeit__impro_possible"),
        ).values("fertigkeit__titel", "fertigkeit__attribut__titel", "fp", "fg", "fp_bonus", "pool", "fertigkeit__limit", "fertigkeit__gruppe", "impro_possible")

        for fert in qs_fert:
            fert["fg"] = self._gruppen_fg[fert["fertigkeit__gruppe"]]

            relattr = self._rel_attribute[fert["fertigkeit__attribut__titel"]]
            fert["pool"] = sum([relattr.aktuell(), fert["fp"], fert["fp_bonus"], fert["fg"]])

        return {
            "fert__table": FertTable(qs_fert),
        }

    def get_hp(self, char):
        khp = [
            self._rel_attribute["ST"].aktuell() * 5,
            math.floor(char.larp_rang / 20) if char.larp else char.ep_stufe * 2,
            math.floor(char.rang / 10),
            char.HPplus_fix if char.HPplus_fix is not None else char.HPplus,
        ]
        ghp = [
            self._rel_attribute["WK"].aktuell() * 5,
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
        attr = {attr_titel: rel.aktuell() for attr_titel, rel in self._rel_attribute.items()}
        fert = {rel.fertigkeit.titel: attr[rel.fertigkeit.attribut.titel] + self._gruppen_fg[rel.fertigkeit.gruppe] + rel.fp + rel.fp_bonus for rel in char.relfertigkeit_set.all()}

        class SpezialTable(tables.Table):
            class Meta:
                model = RelSpezialfertigkeit
                fields = (
                    "spezialfertigkeit__titel", "attribute", "gesamt",
                    "fertigkeiten", "korrektur", "wp", "w20_probe"
                )
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_gesamt(self, value, record):
                return sum([attr[attr_name] for attr_name in record.attribute.split(" + ")]) -5

            def render_korrektur(self, value, record):
                return math.floor(sum([fert[fert_name] for fert_name in record.fertigkeiten_names.split(";")]) / 2 + 0.5)
            
            def render_w20_probe(self, value, record):
                return sum([attr[attr_name] for attr_name in record.attribute.split(" + ")]) -5 + record.wp


        class WissenTable(tables.Table):
            class Meta:
                model = RelWissensfertigkeit
                fields = (
                    "wissensfertigkeit__titel", "attribute", "gesamt",
                    "fertigkeiten", "wp", "schwellwert"
                )
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_gesamt(self, value, record):
                return sum([attr[attr_name] for attr_name in record.attribute.split(" + ")])
            
            def render_schwellwert(self, value, record):
                return sum([
                    *[attr[attr_name] for attr_name in record.attribute.split(" + ")],
                    *[fert[fert_titel] for fert_titel in record.fertigkeiten_names.split(";")],
                    record.wp * Wissensfertigkeit.WISSENSF_STUFENFAKTOR
                ])


        spezi_qs = char.relspezialfertigkeit_set.prefetch_related("spezialfertigkeit").all().annotate(
            attribute=Concat("spezialfertigkeit__attr1__titel", Value(" + "), "spezialfertigkeit__attr2__titel", output_field=CharField()),
            fertigkeiten_names=ConcatSubquery(Fertigkeit.objects.filter(spezialfertigkeit=OuterRef("spezialfertigkeit")).values("titel"), separator=";"),
            fertigkeiten=ConcatSubquery(Fertigkeit.objects.filter(spezialfertigkeit=OuterRef("spezialfertigkeit")).annotate(text=Concat("titel", Value(" ("), "attribut__titel", Value(")"), output_field=CharField())).values("text"), separator=", "),
            gesamt=Value(1),
            korrektur=Value(1),
            w20_probe=Value(1),
            wp=F("stufe")
        )

        wissen_qs = char.relwissensfertigkeit_set.prefetch_related("wissensfertigkeit").all().annotate(
            attribute=Concat("wissensfertigkeit__attr1__titel", Value(" + "), "wissensfertigkeit__attr2__titel", Value(" + "), "wissensfertigkeit__attr3__titel", output_field=CharField()),
            fertigkeiten_names=ConcatSubquery(Fertigkeit.objects.filter(wissensfertigkeit=OuterRef("wissensfertigkeit")).values("titel"), separator=";"),
            fertigkeiten=ConcatSubquery(Fertigkeit.objects.filter(wissensfertigkeit=OuterRef("wissensfertigkeit")).annotate(text=Concat("titel", Value(" ("), "attribut__titel", Value(")"), output_field=CharField())).values("text"), separator=", "),
            gesamt=Value(1),
            wp=F("stufe"),
            schwellwert=Value(1),
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
            "vorteil__table": TeilTable(char.relvorteil_set.prefetch_related("teil", "attribut", "fertigkeit", "engelsroboter").all().annotate(notiz=Value(" "))),
            "nachteil__table": TeilTable(char.relnachteil_set.prefetch_related("teil", "attribut", "fertigkeit", "engelsroboter").all().annotate(notiz=Value(" "))),
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

    def get_klasse_ability(self, char):
        class KlasseAbilityTable(tables.Table):
            class Meta:
                model = RelKlasseAbility
                fields = ("ability__name", "ability__beschreibung", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

        return {
            "klasse_ability__table": KlasseAbilityTable(char.relklasseability_set.all())
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
                fields = ("item__name", "tier", "item__beschreibung", "item__manaverbrauch", "item__astralschaden", "item__verteidigung", "item__schadensart")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__beschreibung(self, value):
                regex = "Tier [0IVX]+:"
                return format_html(re.sub(regex, lambda match: f"<br><b>{match.group(0)}</b>", value))

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
                fields = ("anz", "item__name", "item__bs", "item__zs", "item__dk", "item__schadensart", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__zs(self, value, record):
                return f"{value} (ab {record.item.erfolge})"

        return {
            "nahkampf__table": WaffenTable(char.relwaffen_werkzeuge_set.all())
        }

    def get_fernkampf(self, char):
        class SchusswaffenTable(tables.Table):
            class Meta:
                model = RelSchusswaffen
                fields = ("anz", "item__name", "item__bs", "item__zs", "item__dk", "item__präzision", "item__schadensart", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_item__zs(self, value, record):
                return f"{value} (ab {record.item.erfolge})"

        return {
            "fernkampf__table": SchusswaffenTable(char.relschusswaffen_set.all())
        }

    def get_effekte(self, char):
        class EffectTable(tables.Table):
            class Meta:
                model = RelEffect
                fields = ("wertaenderung", "fieldname", "source")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_fieldname(self, value, record):
                display = record.get_target_fieldname_display()
                if "RelAttribut" in record.target_fieldname: return f"{display} {record.target_attribut.attribut.titel}"
                if "RelFertigkeit" in record.target_fieldname: return f"{display} {record.target_fertigkeit.fertigkeit.titel}"
                return display

            def render_source(self, value, record):
                fieldnames = [field for field, val in record.__dict__.items() if "source_" in field and val]
                sources = [getattr(record, field.replace("_id", "")) for field in fieldnames if getattr(record, field) is not None]
                reprs = [f"{field.__class__._meta.verbose_name} {field}".__str__() for field in sources]
                return ", ".join(reprs)

        return {
            "effect__table": EffectTable(
                char.releffect_set.filter(is_active=True)\
                    .prefetch_related(
                        "target_attribut__attribut", "target_fertigkeit__fertigkeit",

                        "source_vorteil__char", "source_vorteil__teil",
                        "source_nachteil__char", "source_nachteil__teil",
                        "source_talent__char", "source_talent__talent",
                        "source_gfsAbility__char", "source_gfsAbility__ability",
                        "source_klasse__char", "source_klasse__klasse",
                        "source_klasseAbility__char", "source_klasseAbility__ability",
                        "source_shopBegleiter__char", "source_shopBegleiter__item",
                        "source_shopMagischeAusrüstung__char", "source_shopMagischeAusrüstung__item",
                        "source_shopRüstung__char", "source_shopRüstung__item",
                        "source_shopAusrüstungTechnik__char", "source_shopAusrüstungTechnik__item",
                        "source_shopEinbauten__char", "source_shopEinbauten__item",
                    )\
                    .annotate(
                        fieldname=Value(" "),
                        source=Value(" "),
                    ).all()
                )
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
        return Log.objects.filter(char=char, art__in=("s", "u", "i", "j", "l"))
    

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = get_object_or_404(Charakter, pk=self.kwargs["pk"])

        return super().get_context_data(
            **kwargs,
            topic = "History",
            app_index=char.name,
            app_index_url=reverse("character:show", args=[char.id]),
            priotable=char.processing_notes["priotable"] if "priotable" in char.processing_notes else None,
        )


@require_GET
@verified_account
def delete_char(request, pk):
    # assert user requesting delete a character
    qs = Charakter.objects.filter(pk=pk)
    if not request.spieler.is_spielleitung: qs = qs.filter(char__eigentümer=request.spieler.instance)
    char = qs.first()
    
    # cannot find char
    if not char:
        messages.error(request, "Es ist nicht dein Charakter, den du löschen willst oder er existiert gar nicht.")
    # delete char
    else:
        messages.success(request, f"{char.name} ist gelöscht.")
        char.delete()

    return redirect("character:index")

@require_POST
@verified_account
def edit_tag(request, pk):

    # assert user requesting to edit the chars of a tag
    tag = Tag.objects.filter(pk=pk, spieler=request.spieler.instance).first()
    if not tag:
        messages.error(request, "Das ist nicht dein Tag.")
        return redirect("character:index")
    
    # get all selected chars for the tag
    char_ids = [int(k.replace(f"tag-{tag.id}-char-", "")) for k, v in request.POST.items() if v == "on" and re.match(f"^tag\-{tag.id}\-char\-\d+$", k)]
    chars = Charakter.objects.filter(id__in=char_ids)
    if not request.spieler.is_spielleitung: chars = chars.filter(eigentümer=request.spieler.instance)
    
    # set chars to db
    tag.charakter_set.set(chars)

    messages.success(request, f'Du hast Charaktere von Tag "{tag.name}" verändert.')
    return redirect("character:index")


@verified_account
def delete_tag(request, pk):

    # assert user requesting to edit the chars of a tag
    tag = Tag.objects.filter(pk=pk, spieler=request.spieler.instance).first()
    num_tags_and_chars_deleted = Tag.objects.filter(pk=pk, spieler=request.spieler.instance).delete()[0]
    if num_tags_and_chars_deleted == 0:
        messages.error(request, "Der Tag existiert nicht.")
        return redirect("character:index")

    messages.success(request, f'Du hast Tag "{tag.name}" gelöscht.')
    return redirect("character:index")


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
    if not request.spieler.is_spielleitung and not Model.objects.filter(pk=pk, char__eigentümer=request.spieler.instance).exists():
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


class CreateCharacterView(UserPassesTestMixin, CreateView):
    # permission
    def test_func(self):
        """ is_spielleitung or adds chars """
        return self.request.spieler.is_spielleitung or "trägt seine chars ein" in self.request.spieler.groups

    def handle_no_permission(self):
        return redirect("character:index")
    # /permission

    model = Charakter
    template_name = "character/create_character.html"
    form_class = CharacterForm
    success_url = None

    def get_formsets_for_context(self):
        formsets = {
            "attribute": AttributFormSet,
            "fertigkeiten": FertigkeitFormSet,
            "gruppen": GruppenFormSet,
            "affektivitäten": AffektivitätenFormSet,
            "klassen": KlassenFormSet,
            "klassen_fähigkeiten": KlassenAbilityFormSet,
            "spezialfertigkeiten": SpezialfertigkeitenFormSet,
            "wissensfertigkeiten": WissensfertigkeitenFormSet,
            "gfs_fähigkeiten": GfsAbilityFormSet,
            "vorteile": VorteilFormSet,
            "nachteile": NachteilFormSet,
            "talente": TalentFormSet,
            "wesenkräfte": WesenkraftFormSet,

            # shop
            "items": ShopItemFormSet,
            "waffenWerkzeuge": ShopWaffenWerkzeugeFormSet,
            "magazine": ShopMagazineFormSet,
            "pfeile_bolzen": ShopPfeilBolzenFormSet,
            "schusswaffen": ShopSchusswaffenFormSet,
            "magischeAusrüstung": ShopMagAusrüstungFormSet,
            "rituale_runen": ShopRitualeRunenFormSet,
            "rüstungen": ShopRüstungFormSet,
            "ausrüstungTechnik": ShopAusrüstungTechnikFormSet,
            "fahrzeuge": ShopFahrzeugFormSet,
            "einbauten": ShopEinbautenFormSet,
            "zauber": ShopZauberFormSet,
            "vergessene_zauber": ShopVergesseneZauberFormSet,
            "begleiter": ShopBegleiterFormSet,
            "engelsroboter": ShopEngelsroboterFormSet,

        }
        return {k: v(self.request.POST) if self.request.POST else v() for k, v in formsets.items()}

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Charakter nachtragen",
            app_index = "Charaktere",
            app_index_url=reverse("character:index"),
            **self.get_formsets_for_context(),
        )
    
    def get(self, request, *args, **kwargs):
        messages.info(request, "Felder, die auf '_fix' enden sind erstmal leer (nicht 0, sondern leer!). Sie sind für Fixwerte gedacht, z.B. 0 auf 'konzentration_fix' bei Nachteil Insomnie.")
        return super().get(request, *args, **kwargs)
    

    def form_valid(self, form):
        context = self.get_formsets_for_context()

        with transaction.atomic():
            # Has errors?
            invalid_formsets = ["form"] if not form.is_valid() else []
            non_form_errors = ""
            for formset in context.values():
                if not formset.is_valid():
                    invalid_formsets.append(formset.prefix)

                    nonform = formset.non_form_errors() or ""
                    if nonform:
                        non_form_errors += f"<p>{formset.prefix}: {nonform}</p>"

            # render form with errors
            if invalid_formsets:
                messages.error(self.request, f"Fehler sind aufgetreten in: {', '.join(invalid_formsets)}")
                if non_form_errors: messages.error(self.request, format_html(non_form_errors))

                return render(self.request, self.template_name, {**self.get_context_data(), **context})
  

            messages.success(self.request, "Charakter ist nun übernommen")
            # create char in db
            self.object = form.save(commit=False)
            self.object.eigentümer = self.request.spieler.instance
            self.object.in_erstellung = False
            self.object.ep_stufe_in_progress = self.object.ep_stufe
            self.object.processing_notes = {
                "creation": "manuell online nachgetragen",
                "effect_signals": "ignore" # do not create RelEffect instances in effect.signals.apply_effect_on_rel_relation()
            }
            self.object.save()
            # create related objects in db
            for formset in context.values():
                formset.instance = self.object
                formset.save()

            del self.object.processing_notes["effect_signals"]
            # add missing Attribute, Fertigkeiten, Gruppen. Would be called automatically,
            # but we had to create explicitly named attrs, ferts, gruppen first. Fill up missing ones with character.signals.init_character()
            self.object.save()


        # redirect to the supplied URL.
        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        return reverse('character:show', kwargs={'pk': self.object.pk})
