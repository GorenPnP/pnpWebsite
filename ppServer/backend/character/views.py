import locale, re, math
from typing import Any, Dict

from django.apps import apps
from django.contrib import messages
from django.contrib.admin.models import ContentType, LogEntry, CHANGE
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Q, ManyToManyField, ManyToManyRel, ManyToOneRel, Value, F, CharField, OuterRef, Case, When, Count
from django.db.models.functions import Concat, Coalesce
from django.db.utils import IntegrityError
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.template import TemplateDoesNotExist, loader as TemplateLoader
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

import django_tables2 as tables

from base.abstract_views import GenericTable
from campaign.forms import AuswertungForm, LarpAuswertungForm
from cards.models import Card, Transaction
from effect.models import RelEffect
from log.create_log import render_number
from log.models import Log
from core.decorators import verified_account
from core.mixins import VerifiedAccountMixin, SpielleitungOnlyMixin, CopiesCharsMixin
from core.utils import ConcatSubquery, CountSubquery, SumSubquery
from shop.views.list import shopmodel_list, shopmodel_upgrade_list

from .enums import gruppen_enum
from .forms import *
from .models.char import Charakter, Tag as CharTag, CurrentStory
from .models.rel import *
from .models.relshop import RelRamsch, RelShop
from .permissions import *

locale.setlocale(locale.LC_NUMERIC, "de_DE.utf8")

class CharacterListView(VerifiedAccountMixin, TemplateView):
    template_name = "character/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        char_qs = Charakter.objects.prefetch_related("eigentümer", "tags").filter(in_erstellung=False).order_by('name')
        if not self.request.user.has_perm(CustomPermission.SPIELLEITUNG.value):
            char_qs = char_qs.filter(eigentümer=self.request.spieler)

        return {
            'charaktere': char_qs,
            "num_all_chars": char_qs.count(),
            "tags": CharTag.objects.filter(spieler=self.request.spieler).annotate(num=Count("charakter")).order_by("name"),
            'topic': "Charaktere",
            "plus": "+ Charakter",
            "plus_url": reverse('create:gfs'),
        }

    def get(self, request, *args, **kwargs):
        tagname = self.request.GET["tag"] if "tag" in self.request.GET else None
        context = self.get_context_data(**kwargs)

        if tagname and CharTag.objects.filter(name=tagname, spieler=self.request.spieler).exists():
            context["charaktere"] = context["charaktere"].filter(tags__name=tagname)

        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        create_tag_form = CreateTagForm({"name": self.request.POST.get("name"), "spieler": self.request.spieler})
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
        "relzauber_set__item", "relritual_rune_set__item", "relfernkampfwaffe_set__item", "relnahkampfwaffe_set__item",
        "relmunition_set__item", "relmagische_ausrüstung_set__item", "relrüstung_set__item",
        "reltechnik_set__item", "relfahrzeug_set__item", "releinbaute_set__item", "relalchemie_set__item",
        "reltinker_set__item", "relbegleiter_set__item", "relramsch_set", "card"
    )

    def get_item_qs(self, model: type[RelShop] or RelRamsch, char: Charakter) -> QuerySet[type[RelShop] or RelRamsch]:
        """ uses model to return the url to a template as string to use for rendering an item in a list """

        # get template
        model_name = model._meta.model_name[3:]
        template = 'character/relitem_list_item/default.html'
        try:
            TemplateLoader.get_template(f'character/relitem_list_item/{model_name}.html')
            template = f'character/relitem_list_item/{model_name}.html'
        except TemplateDoesNotExist:
            pass


        # get detail_url
        detail_url = reverse("character:relitem_upgrade_detail", args=[model, 0]).replace('0', '')

        # form queryset
        qs = model.objects.select_related("char").filter(char=char)\
            .annotate(
                template = Value(template),     # needed to render this item nicely
                model_name = Value(model_name),
                model_verbose_name = Value(apps.get_model("shop", model_name)._meta.verbose_name if model != RelRamsch else "Ramsch"),
                detail_url = Concat(Value(detail_url), F("pk"), output_field=CharField()),
            )
        if model_name in [m._meta.model_name for m in shopmodel_upgrade_list]:
            qs = qs.annotate(
                num_slots = Coalesce(SumSubquery(apps.get_model("shop", f"slot{model_name}").objects.filter(Q(item=OuterRef("item__pk"))), "num"), 0),
                num_used_slots = Coalesce(CountSubquery(apps.get_model("character", f"upgradeslot{model_name}").objects.filter(relitem=OuterRef("pk"))), 0),
            )
        if model != RelRamsch: qs = qs.select_related("item")
        if model == RelFernkampfwaffe: qs = qs.prefetch_related("item__munition")
        return qs.order_by("item", "-stufe", "-notizen")

    def get(self, request, *args, **kwargs):
        if not self.request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and not Charakter.objects.filter(pk=kwargs["pk"], eigentümer=self.request.spieler).exists():
            return redirect("character:index")

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        char = context["object"]
        self._rel_attribute = {rel.attribut.titel: rel for rel in char.relattribut_set.all()}
        self._gruppen_fg = {rel.gruppe: rel.fg for rel in char.relgruppe_set.all()}
        curr_story, _ = CurrentStory.objects.get_or_create(char=char)

        return {
            **context,
            "topic":  char.name,
            "app_index": "Charaktere",
            "app_index_url": reverse("character:index"),
            "plus": "Historie",
            "plus_url": reverse("character:history", args=[char.id]),
            "story_notes_form": StoryNotesForm(instance=curr_story),
            "spend_money_form": SpendMoneyForm(sender_card=char.card),
            "regex_escaped_name": re.escape(char.name),
            "auswertung_form": LarpAuswertungForm() if char.larp else AuswertungForm(),

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
            **self.get_effekte(char),
        }


    def get_personal(self, char):
        gfs = f"<a class='text-white' href='{reverse('wiki:stufenplan', args=[char.gfs.id])}'>{char.gfs.titel}</a>" if char.gfs is not None else '-'

        further_notes = ""
        if char.no_MA_MG: further_notes = Charakter.no_MA_MG.field.verbose_name + "\n\n"
        elif char.no_MA: further_notes = Charakter.no_MA.field.verbose_name + "\n\n"

        fields = [
                ["Name", char.name],
                ["Gfs (Stufe)", format_html(f"{gfs} ({char.skilltree_stufe})")],
                ["Persönlichkeit", char.persönlichkeit.titel if char.persönlichkeit else "-"],
                ["Geschlecht", char.geschlecht],
                ["Alter", f"{char.alter} Jahr{'e' if char.alter != 1 else ''}"],
                ["Größe", f"{char.größe} cm"],
                ["Gewicht", f"{char.gewicht} kg"],
                ["Religion", char.religion.titel if char.religion else ""],
                ["Augenfarbe", char.augenfarbe],
                ["Hautfarbe", char.hautfarbe],
                ["Haarfarbe", char.haarfarbe],
                ["Sexualität", char.sexualität],
                ["präferierter Arm", char.präf_arm],
                ["Beruf", char.beruf.titel if char.beruf else ""],
                ["Notizen", format_html(re.sub("\n", "<br>", further_notes + char.notizen, 0, re.MULTILINE))],
                ["persönliche Ziele", format_html(re.sub("\n", "<br>", char.persönlicheZiele, 0, re.MULTILINE))],
        ]
        if not char.larp:
            fields.insert(2, ["Klassen (Stufe)", ", ".join([f"{rel.klasse.titel} ({rel.stufe})" for rel in char.relklasse_set.all()]) or "-"])

        return {
            "personal__fields": [[k, v if v else "-"] for k, v in fields]
        }

    def get_resources(self, char):
        fields = [
            ["Geld", format_html(f"{render_number(char.geld)} Drachmen (<a class='text-white' href='{reverse('cards:show', args=[char.card.pk])}'>alle Transaktionen -></a>)")],
            ["SP", char.sp],
            ["IP", char.ip],
            ["TP", char.tp],
            ### add here ###
            ["Prestige", render_number(char.prestige)],
            ["Verzehr", render_number(char.verzehr)],
            ["Manifest", char.manifest - char.sonstiger_manifestverlust if char.manifest_fix is None else char.manifest_fix],
            ["Konzentration", char.konzentration if char.konzentration_fix is None else char.konzentration_fix],
            ["Krit-Angriff", char.crit_attack],
            ["Krit-Verteidigung", char.crit_defense],
        ]
        if char.larp:
            fields.insert(4, ["LARP-Ränge", render_number(char.larp_rang)])
        else:
            fields.insert(4, ["EP (Stufe)", f"{render_number(char.ep)} ({char.ep_stufe})"])

        # collect unused Upgrade points (format {item_type, item_name, points}[] of all RelUpgrades with points > 0)
        upgrade_points = sorted([
            entry for m in apps.get_models("character") if issubclass(m, RelUpgrade) for entry in m.objects.filter(char=char, points__gt=0).annotate(
                # verbose_name of item's model
                item_type=Value(m.item.field.related_fields[0][0].related_model._meta.verbose_name)
            ).values("item_type", "item__name", "points")
        ], key=lambda entry: f"{entry['item_type']}|||{entry['item__name']}")
        if len(upgrade_points):
            fields.append(["Upgrade-Punkte", format_html('<ul>' + ''.join([f'<li>{i["item_type"]} <b>{i["item__name"]}</b>: {i["points"]} Punkt{'e' if i["points"] > 1 else ''}</li>' for i in upgrade_points]) + "</ul>")])

        # collect unused Upgrades (format {item_type, item_name, num, upgrade}[] of all OwnUpgrades)
        upgrades = sorted([
            entry for m in apps.get_models("character") if issubclass(m, OwnUpgrade) for entry in m.objects.annotate(
                # verbose_name of relUpgrade.item's model
                item_type=Value(m.relUpgrade.field.related_model.item.field.related_fields[0][0].related_model._meta.verbose_name)
            ).values("item_type", "relUpgrade__item__name", "num", "upgrade__name")
        ], key=lambda entry: f"{entry['item_type']}|||{entry['relUpgrade__item__name']}")
        if len(upgrades):
            fields.append(["unverteilte Upgrades", format_html('<ul>' + ''.join([f'<li>{i["item_type"]} <b>{i["relUpgrade__item__name"]}</b>: {i["num"]}x {i["upgrade__name"]}</li>' for i in upgrades]) + "</ul>")])

        return {
            "resources__fields": [[k, v if v else 0] for k, v in fields]
        }

    def get_calculated(self, char):
        MA_relattr = self._rel_attribute["MA"]
        MA_raw = MA_relattr.aktuellerWert if MA_relattr.aktuellerWert_fix is None else MA_relattr.aktuellerWert_fix
        attrs = { attr_name: rel.aktuell() for attr_name, rel in self._rel_attribute.items() }

        num = lambda n: "{0:.1f}".format(n) if type(n) is float else n

        astrale_reaktion = f'{attrs["MA"] + attrs["WK"]}'
        if char.no_MA_MG: astrale_reaktion = f'{attrs["WK"] + 4}'
        elif char.no_MA: astrale_reaktion = f'{attrs["WK"]} + Pool Angriffsfertigkeit'
        if  char.astrale_reaktion_bonus: astrale_reaktion += f" + {char.astrale_reaktion_bonus}"

        physischer_widerstand = f'{attrs["VER"]}'
        if char.physischer_widerstand_bonus: physischer_widerstand += f" + {char.physischer_widerstand_bonus}"
        if char.physischer_widerstand_bonus_str: physischer_widerstand += f' + {char.physischer_widerstand_bonus_str}'

        return {
            "calculated__fields": [
                ["Initiative", num(attrs["SCH"]*2 + attrs["WK"] + attrs["GES"] + char.initiative_bonus)],
                ["Manaoverflow", num((attrs["WK"] + MA_raw)*3 + char.manaoverflow_bonus)],

                ["physische Reaktion", num(attrs["SCH"] + attrs["GES"] + char.physische_reaktion_bonus)],
                ["physischer Widerstand", f"{physischer_widerstand} HP"],
                ["astrale Reaktion", astrale_reaktion],
                ["astraler Widerstand", f"{attrs["WK"]} + {char.astraler_widerstand_bonus_str} HP" if char.astraler_widerstand_bonus_str else f"{attrs["WK"]} HP"],
                ["Bewegung Laufen", f'{num(char.gfs.base_movement_speed + attrs["SCH"] + char.speed_laufen_bonus)}m'],
                ["Bewegung Schwimmen", f'{num((char.gfs.base_movement_speed + attrs["SCH"])/2 + char.speed_schwimmen_bonus)}m'],
                ["Bewegung Fliegen", f'{num((char.gfs.base_movement_speed + attrs["SCH"])*2 + char.speed_fliegen_bonus)}m'],
                ["Bewegung Astral", f'{num((char.gfs.base_movement_speed + attrs["SCH"])*4 + char.speed_astral_bonus)}m'],
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
                if value == "MA" and not record.char.no_MA_MG and record.char.no_MA:
                    return "Managetik (MG)"
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
                fields = ("fertigkeit__titel", "fertigkeit__attribut__titel", "fp", "fg", "fp_bonus", "pool","fertigkeit__gruppe")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}
                row_attrs = {
                    "class": lambda record:
                        ("impro_possible" if record["impro_possible"] else " ") +
                        ("fert_impossible" if not record["impro_possible"] and record["fp"] == 0 else " ")
                }

            def render_fertigkeit__attribut__titel(self, value):
                if value == "MA" and char.no_MA and not char.no_MA_MG:
                    return "MG"
                return value

            def render_fg(self, value):
                return format_html(f"<i>{value}</i>")

            def render_fp_bonus(self, value):
                return f"+{value}" if value else "-"

            def render_pool(self, value, record):
                return format_html(f"<b>{value}</b>") if record["impro_possible"] or record["fp"] else "-"

            def render_fertigkeit__gruppe(self, value):
                return [name for token, name in gruppen_enum if token == value][0]

        qs_fert = char.relfertigkeit_set.all().prefetch_related("fertigkeit__attribut").annotate(
            fg=Value(1),
            pool=Value(1),
            impro_possible=F("fertigkeit__impro_possible"),
        ).values("fertigkeit__titel", "fertigkeit__attribut__titel", "fp", "fg", "fp_bonus", "pool", "fertigkeit__gruppe", "impro_possible")

        for fert in qs_fert:
            fert["fg"] = self._gruppen_fg[fert["fertigkeit__gruppe"]]

            relattr = self._rel_attribute[fert["fertigkeit__attribut__titel"]]
            fert["pool"] = sum([relattr.aktuell(), fert["fp"], fert["fp_bonus"], fert["fg"]])

        return {
            "fert__table": FertTable(qs_fert),
        }

    def get_hp(self, char):
        khp = [
            self._rel_attribute["ST"].aktuell() * 3,
            math.floor(char.larp_rang / 25) if char.larp else char.ep_stufe * 3,
            char.HPplus_fix if char.HPplus_fix is not None else char.HPplus,
        ]
        ghp = [
            self._rel_attribute["WK"].aktuell() * 3,
            math.floor(char.larp_rang / 25) if char.larp else char.ep_stufe * 3,
            char.HPplus_geistig + (10 if char.no_MA_MG else 0),
        ]

        fields_khp = [
            ["HP durch Stärke", khp[0]],
            ["HP durch LARP-Ränge" if char.larp else "HP durch Stufe", khp[1]],
            ["HP-Bonus", khp[2]],
            [format_html("<b>Körperliche HP</b>"), format_html(f"<b>{sum(khp)}</b>")],
        ]
        fields_ghp = [
            ["HP durch Willenskraft", ghp[0]],
            ["HP durch LARP-Ränge" if char.larp else "HP durch Stufe", khp[1]],
            ["HP-Bonus", ghp[2]],
            [format_html("<b>geistige HP</b>"), format_html(f"<b>{sum(ghp)}</b>")],
        ]

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

            def render_ability__name(self, value, record):
                stufenplan_entry = record.ability.gfsstufenplan

                return format_html(f"{value}<br><small><i>({stufenplan_entry.gfs.titel} {stufenplan_entry.basis.stufe})</i></small>")

        qs = char.relgfsability_set.prefetch_related("ability__gfsstufenplan__basis", "ability__gfsstufenplan__gfs").annotate(
            has_effect = Exists(RelEffect.objects.filter(source_gfsAbility=OuterRef("pk"), target_char=char, is_active=True))
        )
        return {
            "gfs_ability__table": GfsAbilityTable(qs.filter(has_effect=False)),
            "gfs_ability_effect__table": GfsAbilityTable(qs.filter(has_effect=True)),
        }

    def get_klasse_ability(self, char):
        class KlasseAbilityTable(tables.Table):
            class Meta:
                model = RelKlasseAbility
                fields = ("ability__name", "ability__beschreibung", "notizen")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_ability__name(self, value, record):
                stufenplan_entry = record.ability.klassestufenplan_set.first()
                base_entry = record.ability.klasse_set.first() if not stufenplan_entry else None

                klasse = stufenplan_entry.klasse.titel if stufenplan_entry else base_entry.titel
                stufe = stufenplan_entry.stufe if stufenplan_entry else "Basis"

                return format_html(f"{value}<br><small><i>({klasse} {stufe})</i></small>")

        qs = char.relklasseability_set.prefetch_related("ability__klasse_set", "ability__klassestufenplan_set__klasse").annotate(
            has_effect = Exists(RelEffect.objects.filter(source_klasseAbility=OuterRef("pk"), target_char=char, is_active=True))
        )
        return {
            "klasse_ability__table": KlasseAbilityTable(qs.filter(has_effect=False)),
            "klasse_ability_effect__table": KlasseAbilityTable(qs.filter(has_effect=True)),
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
        RelModels = [*[apps.get_model("character", f"Rel{Model._meta.model_name}") for Model in [m for m in shopmodel_list if m not in [Nahkampfwaffe, Fernkampfwaffe, Zauber, Ritual_Rune]]], RelRamsch]
        objects = [item for m in RelModels for item in self.get_item_qs(m, char)]

        return {
            "inventory": sorted(objects, key=lambda o: o.item.name.lower() if hasattr(o.item, "name") else o.item.lower()),
            "ramsch_form": CreateRamschForm(initial={"char": char.pk}),
            "inventory__random_items": format_html(re.sub("\n", "<br>", char.sonstige_items, 0, re.MULTILINE)),

            "zauber": self.get_item_qs(RelZauber, char),
            "ritual": self.get_item_qs(RelRitual_Rune, char),
            "nahkampf": self.get_item_qs(RelNahkampfwaffe, char),
            "fernkampf": self.get_item_qs(RelFernkampfwaffe, char),
            "munition": self.get_item_qs(RelMunition, char),
        }

    def get_effekte(self, char):
        class EffectTable(tables.Table):
            class Meta:
                model = RelEffect
                fields = ("wert", "fieldname", "source")
                orderable = False
                attrs = {"class": "table table-dark table-striped table-hover"}

            def render_wert(self, value, record):
                return record.wertaenderung_str or record.wertaenderung

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
                        "source_shopEinbaute__char", "source_shopEinbaute__item",
                    )\
                    .annotate(
                        wert=Value(" "),
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
        return Log.objects.prefetch_related("spieler").filter(char=char, art__in=("s", "u", "i", "j", "l", "q", "w"))


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = get_object_or_404(Charakter.objects.prefetch_related("card"), pk=self.kwargs["pk"])

        return super().get_context_data(
            **kwargs,
            topic = "Historie",
            app_index=char.name,
            app_index_url=reverse("character:show", args=[char.id]),

            priotable=char.processing_notes["priotable"] if "priotable" in char.processing_notes else None,

            card=char.card,
            transactions = char.card.get_transactions().annotate(
                card_uuid=Case(When(sender=char.card, then=F("receiver")), default=F("sender")),

                card_name=Subquery(Card.objects.filter(pk=OuterRef("card_uuid")).values("name")[:1]),
                card=Case(When(card_name=None, then=Subquery(Card.objects.filter(pk=OuterRef("card_uuid")).values("char__name")[:1])), default=F("card_name")),

                diff=Case(When(sender=char.card, then=Value(-1) * F("amount")), default=F("amount"), output_field=models.IntegerField()),
            )
        )


@require_GET
@verified_account
def delete_char(request, pk):
    # assert user requesting delete a character
    qs = Charakter.objects.filter(pk=pk)
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value): qs = qs.filter(eigentümer=request.spieler)
    char = qs.first()

    # cannot find char
    if not char:
        messages.error(request, "Es ist nicht dein Charakter, den du löschen willst oder er existiert gar nicht.")
    # delete char
    else:
        try:
            char.delete()
            messages.success(request, f"{char.name} wurde gelöscht.")
        except IntegrityError as err:
            caught_constraint = err.__str__().split('\n')[0].split('violates check constraint')[-1]
            messages.error(request, f"{char.name} wurde nicht gelöscht. Es gab Probleme mit {caught_constraint}. Das passiert häufig, wenn zurzeit aktive Effekte nicht deaktiviert werden können (z.B. Attribut plötzlich negativ o.Ä.).")

    return redirect("character:index")

@require_POST
@verified_account
def edit_tag(request, pk):

    # assert user requesting to edit the chars of a tag
    tag = CharTag.objects.filter(pk=pk, spieler=request.spieler).first()
    if not tag:
        messages.error(request, "Das ist nicht dein Tag.")
        return redirect("character:index")

    # get all selected chars for the tag
    char_ids = [int(k.replace(f"tag-{tag.id}-char-", "")) for k, v in request.POST.items() if v == "on" and re.match(fr"^tag\-{tag.id}\-char\-\d+$", k)]
    chars = Charakter.objects.filter(id__in=char_ids)
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value): chars = chars.filter(eigentümer=request.spieler)

    # set chars to db
    tag.charakter_set.set(chars)

    messages.success(request, f'Du hast Charaktere von Tag "{tag.name}" verändert.')
    return redirect("character:index")


@verified_account
def delete_tag(request, pk):

    # assert user requesting to edit the chars of a tag
    tag = CharTag.objects.filter(pk=pk, spieler=request.spieler).first()
    num_tags_and_chars_deleted = CharTag.objects.filter(pk=pk, spieler=request.spieler).delete()[0]
    if num_tags_and_chars_deleted == 0:
        messages.error(request, "Der Tag existiert nicht.")
        return redirect("character:index")

    messages.success(request, f'Du hast Tag "{tag.name}" gelöscht.')
    return redirect("character:index")


@verified_account
@require_POST
def add_ramsch(request, pk):
    # assert user requesting to add an item
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and not Charakter.objects.filter(pk=pk, eigentümer=request.spieler).exists():
        messages.error(request, "Es ist nicht dein Charakter, dem du Items geben willst.")
        return redirect(reverse("character:show", args=[pk]))

    # validate incoming data
    try:
        form = CreateRamschForm(request.POST)
        form.full_clean()
        if not form.is_valid(): raise ValueError("form is not valid")
        if form.cleaned_data["char"].pk != pk: raise ValueError("pk on form is different")
    except:
        messages.error(request, "Anfrage fehlerhaft")
        return redirect(reverse("character:show", args=[pk]))

    # create entry
    relramsch_item = form.save()

    # log creation
    Log.objects.create(
        spieler=request.spieler,
        char=relramsch_item.char,
        art="q", # Inventar-Item angelegt
        kosten="",
        notizen=f"{relramsch_item.item}",
    )

    messages.success(request, f"{relramsch_item.item} angelegt")
    return redirect(reverse("character:show", args=[pk]))


@verified_account
@require_POST
def spend_money(request, pk):
    char = get_object_or_404(Charakter.objects.prefetch_related("eigentümer", "card__char__eigentümer", "card__spieler"), pk=pk)

    # assert user requesting to add an item
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and char.eigentümer != request.spieler:
        messages.error(request, "Es ist nicht dein Charakter, dessen Geld du ausgeben willst.")
        return redirect(reverse("character:show", args=[pk]))

    # validate incoming data
    try:
        form = SpendMoneyForm(request.POST, sender_card=char.card)
        form.full_clean()

        if not form.is_valid(): raise ValueError("form is not valid")
        if form.cleaned_data["sender"].char.pk != pk: raise ValueError("pk on form is different")
    except:
        messages.error(request, format_html(f"Geld ausgeben hat nicht geklappt {form.errors if form else ''}"))
        return redirect(reverse("character:show", args=[pk]))

    # spend money
    card = form.cleaned_data["sender"]
    card.money -= form.cleaned_data["amount"]
    card.save(update_fields=["money"])

    # receiver gets money
    if form.cleaned_data["receiver"] is not None:
        form.cleaned_data["receiver"].money += form.cleaned_data["amount"]
        form.cleaned_data["receiver"].save(update_fields=["money"])

    # create Transaction
    form.save()

    # add ramsch
    if form.cleaned_data["add_to_inventory"]:
        RelRamsch.objects.create(char=char, item=form.cleaned_data["reason"])

    # log
    Log.objects.create(
        spieler=request.spieler,
        char=char,
        art="e", # Geld ausgegeben
        kosten=f"{form.cleaned_data['amount']} Dr.",
        notizen=form.cleaned_data["reason"] + (f' an {form.cleaned_data["receiver"]}' if form.cleaned_data["receiver"] else ''),
    )
    if form.cleaned_data["receiver"] and form.cleaned_data["receiver"].char:
        Log.objects.create(
            spieler=request.spieler,
            char=form.cleaned_data["receiver"].char,
            art="g", # Geld bekommen
            kosten=f"{form.cleaned_data['amount']} Dr.",
            notizen=f'{form.cleaned_data["reason"]} von {card}',
        )

    messages.success(request, f"{form.cleaned_data['amount']:n} Dr. für {form.cleaned_data['reason']} ausgegeben")
    return redirect(reverse("character:show", args=[pk]))


@verified_account
@require_POST
def remove_sp(request, pk):
    # assert user requesting to add an item
    char = get_object_or_404(Charakter, pk=pk)
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and char.eigentümer != request.spieler:
        messages.error(request, "Es ist nicht dein Charakter, dessen SP du ausgeben willst.")
        return redirect(reverse("character:show", args=[pk]))

    # has SP?
    if char.sp_fix is not None or char.sp < 1:
        messages.error(request, "Keine SP vorhanden")
        return redirect(reverse("character:show", args=[pk]))

    # spend SP
    char.sp -= 1
    char.save(update_fields=["sp"])

    # log
    Log.objects.create(
        spieler=request.spieler,
        char=char,
        art="k", # SP ausgegeben
        kosten=f"1 SP",
        notizen="in einer Story",
    )

    messages.success(request, f"1 SP ausgegeben")
    return redirect(reverse("character:show", args=[pk]))


def _decrease_anz_relshop(request, Model: type[RelShop], rel_item_pk: int):
    
    # get rel
    qs = Model.objects.select_related("char__eigentümer", "char__card").filter(pk=rel_item_pk)
    if Model != RelRamsch: qs = qs.prefetch_related("item")
    rel_shop = qs.first()

    # assert item existance
    if not rel_shop:
        messages.error(request, "Item konnte nicht im Inventar gefunden werden.")
        return {"success": False, "redirect": redirect("character:index")}

    # assert user requesting to use an item
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and rel_shop.char.eigentümer != request.spieler:
        messages.error(request, "Es ist nicht dein Charakter, von dem du Items benutzen willst.")
        return {"success": False, "redirect": redirect("character:index")}

    char = rel_shop.char
    item_name = rel_shop.item.name if Model != RelRamsch else rel_shop.item
    item = rel_shop.item._meta.model.objects.annotate_price().get(pk=rel_shop.item.pk) if Model != RelRamsch else rel_shop.item
    stufe = rel_shop.stufe or 1 if Model != RelRamsch else 1

    # remove item
    rel_shop.delete()

    return {"success": True, "stufe": stufe, "char": char, "item_name": item_name, "item": item}


@require_POST
@verified_account
def remove_relshop(request, rel_model: type[RelShop], pk: int):
    res = _decrease_anz_relshop(request, rel_model, pk)
    if not res["success"]: return res["redirect"]

    if "sell" in request.POST:
        # get sell price
        price = 0
        if rel_model != RelRamsch:
            curr_price = (res["item"].curr_price or 0) * (res["stufe"] or 1)

            # 40% of cheapest price
            price = int((curr_price * .4) + .5)

        # receive money
        card = res["char"].card
        card.money += price
        card.save(update_fields=["money"])

        Transaction.objects.create(receiver=card, amount=price, reason=f"verkaufe 1x {res['item_name']}")

        # log transaction
        Log.objects.create(
            spieler=request.spieler,
            char=res["char"],
            art="w", # Inventar-Item verbraucht
            kosten=f"Erlös: {price:n} Drachmen",
            notizen=f"1x {res['item_name']}",
        )
        messages.success(request, f'Du hast "{res["item_name"]}" für {price:n} Dr. verkauft')

    if "use" in request.POST:
        # log usage
        Log.objects.create(
            spieler=request.spieler,
            char=res["char"],
            art="j", # Inventar-Item verbraucht
            kosten="",
            notizen=f"1x {res['item_name']}",
        )
        messages.success(request, f'Du hast "{res["item_name"]}" verbraucht')

    return redirect(reverse("character:show", args=[res["char"].pk]))


@require_POST
@verified_account
def save_story_notes(request, pk):
    # assert user requesting to add an item
    char = get_object_or_404(Charakter, pk=pk)
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and char.eigentümer != request.spieler:
        return JsonResponse({"message": "Es ist nicht dein Charakter, dessen Notizen du speichern willst."}, status=418)

    form = StoryNotesForm(request.POST, instance=char.currentstory)
    form.full_clean()
    if not form.is_valid():
        return JsonResponse({"message": "Notizen speichern ist fehlgeschlagen."}, status=418)

    form.save()

    return JsonResponse({}, status=200)


@require_POST
@verified_account
def save_item_notizen(request, relshop_model, pk):
    # assert user requesting to add an item
    Model = apps.get_model('character', relshop_model)
    relshop = get_object_or_404(Model.objects.prefetch_related("char"), pk=pk)
    char = relshop.char
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and char.eigentümer != request.spieler:
        return JsonResponse({"message": "Es ist nicht dein Charakter, dessen Notizen du speichern willst."}, status=418)

    form = ItemNotesForm(request.POST, instance=relshop)
    form.full_clean()
    if not form.is_valid():
        return JsonResponse({"message": "Notizen speichern ist fehlgeschlagen."}, status=418)

    form.save()
    return JsonResponse({}, status=200)


class CreateCharacterView(VerifiedAccountMixin, CopiesCharsMixin, CreateView):
    redirect_to = "character:index"

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
            "nahkampfwaffen": ShopNahkampfwaffeFormSet,
            "munition": ShopMunitionFormSet,
            "fernkampfwaffen": ShopFernkampfwaffeFormSet,
            "magischeAusrüstung": ShopMagAusrüstungFormSet,
            "rituale_runen": ShopRitualRuneFormSet,
            "rüstungen": ShopRüstungFormSet,
            "technik": ShopTechnikFormSet,
            "fahrzeuge": ShopFahrzeugFormSet,
            "einbauten": ShopEinbauteFormSet,
            "zauber": ShopZauberFormSet,
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
            self.object.eigentümer = self.request.spieler
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
            card = Card.objects.create(char=self.object, money=form.cleaned_data["geld"], active=True)
            Transaction.objects.create(receiver=card, amount=card.money, reason="Nachtrag Kapital")

            del self.object.processing_notes["effect_signals"]
            # add missing Attribute, Fertigkeiten, Gruppen. Would be called automatically,
            # but we had to create explicitly named attrs, ferts, gruppen first. Fill up missing ones with character.signals.init_character()
            self.object.save()


        # redirect to the supplied URL.
        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        return reverse('character:show', kwargs={'pk': self.object.pk})


class EditUpgrades(VerifiedAccountMixin, SpielleitungOnlyMixin, TemplateView):
    model = Charakter
    template_name = "character/edit_upgrades.html"

    def setup(self, request, *args, **kwargs):
        res = super().setup(request, *args, **kwargs)
        self.object = Charakter.objects.get(pk=self.kwargs["pk"])
        return res

    def get_forms(self, item, data=None) -> list[RelUpgradeForm, BaseInlineFormSet, list[BaseInlineFormSet]]:
        model_name = item._meta.model_name  # model_name of BaseShop instance belonging to item

        RelUpgrade = apps.get_model("character", f"relupgrade{model_name}")
        relUpgrade, _ = RelUpgrade.objects.get_or_create(item=item, char=self.object)

        OwnUpgrade = apps.get_model("character", f"ownupgrade{model_name}")
        OwnUpgradeFormSet = inlineformset_factory(RelUpgrade, OwnUpgrade, form=get_OwnUpgradeForm(OwnUpgrade), extra=1)

        upgradeslotformsets = []

        # prep UpgradeSlotFormSet
        RelItem = apps.get_model("character", f"rel{model_name}")
        UpgradeSlot = apps.get_model("character", f"upgradeslot{model_name}")
        UpgradeSlotFormSet = inlineformset_factory(RelItem, UpgradeSlot, form=get_UpgradeSlotForm(UpgradeSlot), extra=1)
        for relitem in getattr(item, f"rel{model_name}_set").prefetch_related("item__slots__tag", "upgradeslot_set__upgrade", "upgradeslot_set__slot__tag").filter(char=self.object):
            upgradeslotformsets.append(UpgradeSlotFormSet(data=data, instance=relitem, queryset=relitem.upgradeslot_set.select_related("slot", "upgrade", "relitem__item"), prefix=f"upgradeslot-{model_name}-{relitem.pk}"))


        # important things to build up and validate
        return [
            RelUpgradeForm(model=RelUpgrade, data=data, instance=relUpgrade, prefix=f"relupgrade-{model_name}-{item.pk}"),
            OwnUpgradeFormSet(data=data, instance=relUpgrade, queryset=relUpgrade.own_upgrades.select_related("upgrade", f"relUpgrade__item"), prefix=f"ownupgrade-{model_name}-{item.pk}"),
            upgradeslotformsets,
        ]


    def get_context_data(self, relUpgradeForm=None, ownUpgradeFormSet=None, upgradeSlotFormSets=None, *args, **kwargs):
        formsets = []
        for m in shopmodel_upgrade_list:

            model_name = m._meta.model_name

            item_qs = m.objects.prefetch_related(f"rel{model_name}_set", f"relupgrade{model_name}_set")\
                .filter(Q(**{f"rel{model_name}__char": self.object}) | Q(**{f"relupgrade{model_name}__char": self.object}))\
                .distinct()

            data = []
            for item in item_qs:
                if not relUpgradeForm or relUpgradeForm.instance.item != item:
                    relUpgradeForm, ownUpgradeFormSet, upgradeSlotFormSets = self.get_forms(item)

                data.append({
                    "item": item,
                    "post_link": reverse("character:upgrades_post", args=[self.object.pk, m, item.pk]),
                    "relUpgradeForm": relUpgradeForm,
                    "ownUpgradeFormSet": ownUpgradeFormSet,
                    "upgradeSlotFormSets": upgradeSlotFormSets,
                })

            formsets.append({
                "modelname": m._meta.verbose_name_plural,
                "data": data,
            })


        return super().get_context_data(
			*args, **kwargs,
			topic = "Upgrades",
			app_index = self.object.name,
			app_index_url = reverse("character:show", args=[self.object.pk]),

            formsets = formsets,
        )

    def post(self, *args, **kwargs):
        item = get_object_or_404(kwargs["shop_model"], pk=kwargs["item_pk"])
        form, ownupgradeformset, upgradeslotformsets = self.get_forms(item, self.request.POST)

        # clean
        form.full_clean()
        for f in upgradeslotformsets:
            f.clean()
        ownupgradeformset.clean()

        # all valid?
        if not form.is_valid() or not ownupgradeformset.is_valid() or False in [f.is_valid() for f in upgradeslotformsets]:
            messages.error(self.request, "Etwas hat nicht geklappt :(")

            return render(self.request, self.template_name, self.get_context_data(
                relUpgradeForm=form, ownUpgradeFormSet=ownupgradeformset, upgradeSlotFormSets=upgradeslotformsets
            ))

        # check if item & char of model instances fits to the url params
        if form.instance.char != self.object or form.instance.item != item or\
            True in [f.instance.relUpgrade.char != self.object or f.instance.relUpgrade.item != item for f in ownupgradeformset.forms] or\
            True in [True in [f.instance.relitem.char != self.object or f.instance.relitem.item != item for f in fs.forms] for fs in upgradeslotformsets]:

            messages.error(self.request, f"Falscher Charakter oder falsches Item entdeckt. Lade neu")
            return redirect(reverse("character:upgrades", args=[self.object.pk]))


        # all valid for now. save everything and try the rest.
        try:
            with transaction.atomic():
                relUpgrade = form.save()
                ownUpgrades = ownupgradeformset.save()  # checks are included in checks for relUpgrade
                upgradeSlots = [(uslot, formset, i) for formset in upgradeslotformsets for i, uslot in enumerate(formset.save())]

                # check relational constraints after save
                try:
                    relUpgrade.check_custom_m2m_constraints()
                except ValidationError as e:
                    form.add_error(None, e)
                    raise AssertionError()

                for slot, formset, i in upgradeSlots:
                    try:
                        slot.check_custom_m2m_constraints()
                    except ValidationError as e:
                        formset.forms[i].add_error(None, e)
                        raise AssertionError()

        except AssertionError:
            messages.error(self.request, "Etwas hat nicht geklappt :(")

            return render(self.request, self.template_name, self.get_context_data(
                relUpgradeForm=form, ownUpgradeFormSet=ownupgradeformset, upgradeSlotFormSets=upgradeslotformsets
            ))


        # log changes
        LogEntry.objects.log_action(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(relUpgrade._meta.model).pk,
            object_id=relUpgrade.id,
            object_repr=relUpgrade.__str__(),
            action_flag=CHANGE
        )

        messages.success(self.request, f"Speichern von {item} hat geklappt")
        return redirect(reverse("character:upgrades", args=[self.object.pk]))


class RelItemUpgradeDetailView(VerifiedAccountMixin, DetailView):
    template_name = "character/relitem_upgrade.html"

    context_object_name = "object"
    object = None
    item = None

    def setup(self, request, *args, **kwargs):
        res = super().setup(request, *args, **kwargs)
        self.queryset = self.kwargs["shop_model"].objects.select_related("char")
        if self.kwargs["shop_model"] != RelRamsch:
            self.queryset = self.queryset.select_related("item__firma")

        self.get_object()
        if self.queryset.model != RelRamsch: self.item = get_object_or_404(self.get_item_queryset(), pk=self.object.item.pk)

        return res

    def get_item_queryset(self):
        Model = self.object.item._meta.model
        qs = Model.objects.select_related("firma").annotate_price()
        if Model == RelFernkampfwaffe:
            qs = qs.annotate_schaden()
        try:
            Model._meta.get_field("fertigkeit")
            qs = qs.prefetch_related("fertigkeit")
        except FieldDoesNotExist:
            pass
        return qs

    def get_object(self, *args, **kwargs):
        if not self.object: self.object = get_object_or_404(self.queryset or self.model, pk=self.kwargs["pk"])
        return self.object

    def get_table_fields(self):
        if self.queryset.model == RelRamsch: return []

        excluded_types = [ManyToManyRel, ManyToOneRel, ManyToManyField]
        excluded_fields = ["pk", "id", "ab_stufe", "icon", "name", "beschreibung", "frei_editierbar", "stufenabhängig", "verfügbarkeit", "firma", "price", "has_implementation"]

        field_list = []
        for field in self.item._meta.get_fields():
            if type(field) in excluded_types or field.name in excluded_fields: continue

            name = field.verbose_name or field.name
            value = getattr(self.item, f"get_{field.name}_display")() if field.choices else getattr(self.item, field.name)
            field_list.append({"name": name, "value": value})
        return field_list

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs,
            table_fields=self.get_table_fields(),
            csrf_token=get_token(self.request),
            shop_url = reverse('shop:detail', args=[self.item._meta.model, self.item.pk]) if self.queryset.model != RelRamsch else '',
            sell_price = f"{int(self.item.curr_price * (self.object.stufe or 1) * 0.4+.5):n}" if self.queryset.model != RelRamsch else None,
            rm_item_url = reverse('character:remove_item', args=[self.object._meta.model, self.object.pk]),

            topic = self.object.item.name if self.queryset.model != RelRamsch else self.object.item,
            app_index = self.object.char.name,
            app_index_url = reverse("character:show", args=[self.object.char.pk]),
        )
        context["object"] = self.item if self.queryset.model != RelRamsch else {"name": self.object.item}
        context["rel"] = self.object

        if ("name_form" not in context or not context["name_form"]) and self.queryset.model == RelRamsch:
            context["name_form"] = RelRamschNameForm(instance=self.object, prefix="name")

        if "notizen_form" not in context:
            context["notizen_form"] = get_RelShopNotizenForm(self.queryset.model)(instance=self.object, prefix="notizen")

        # slots & upgrades (not in every model)
        if self.item and self.item._meta.model in shopmodel_upgrade_list:
            Shop_modelname = self.item._meta.model_name
            Slot = apps.get_model("shop", f"slot{Shop_modelname}")
            UpgradeSlot = apps.get_model("character", f"upgradeslot{Shop_modelname}")
            relUpgrade, _ = apps.get_model("character", f"relupgrade{Shop_modelname}").objects.get_or_create(char=self.object.char, item=self.item)

            # gather upgrades
            context["upgrades"] = self.item.possible_upgrades.select_related("tag", "prerequisite").order_by("ab_stufe", "tag__name")
            context["owned_upgrades"] = Upgrade.objects\
                .filter(Q(**{f"ownupgrade{Shop_modelname}__in": relUpgrade.own_upgrades.values_list("pk", flat=True)}))\
                .annotate(
                    num = Subquery(relUpgrade.own_upgrades.filter(upgrade=OuterRef("pk")).values("num")[:1]),
                )\
                .order_by("ab_stufe", "tag__name")

            # gather slots (with associated upgrades)
            slots = Slot.objects.filter(item=self.item).prefetch_related("tag").annotate(
                num_tags = Count("tag"),
                tags = ConcatSubquery(Tag.objects.filter(Q(**{f"slot{Shop_modelname}": OuterRef("pk")})).values("pk")),
                upgrades = ConcatSubquery(UpgradeSlot.objects.filter(relitem=self.object, slot=OuterRef("pk")).values("upgrade")),
            ).values("num", "tags", "tagnames", "num_tags", "upgrades")
            all_tags = Tag.objects.all()

            # fill pks of Tag, Upgrade with the whole object
            for slot in slots:
                upgrade_pks = [int(pk) for pk in (slot["upgrades"] or "").split(",")] if slot["upgrades"] else []
                slot["upgrades"] = [u for u in context["upgrades"] if u.pk in upgrade_pks]
                
                tag_pks = [int(pk) for pk in (slot["tags"] or "").split(",")] if slot["tags"] else []
                slot["tags"] = [t for t in all_tags if t.pk in tag_pks]

            context["slots"] = slots

        return context

    # TODO delete later
    def get(self, request, *args, **kwargs):
        messages.warning(request, "Diese Seite befindet sich zurzeit aktiv in Entwicklung bzgl. Upgrades")
        return super().get(request, *args, **kwargs)

    def post(self, *args, **kwargs):

        # notizen
        notizen_form = get_RelShopNotizenForm(self.queryset.model)(data=self.request.POST, instance=self.object, prefix="notizen")
        notizen_form.full_clean()

        if notizen_form.is_valid():
            notizen_form.save()
        else:
            messages.error(self.request, "Beim Speichern der Notizen ist etwas schief gelaufen")

        # item name for RelRamsch
        name_form = None
        if self.queryset.model == RelRamsch:
            name_form = RelRamschNameForm(data=self.request.POST, instance=self.object, prefix="name")
            name_form.full_clean()

            if name_form.is_valid():
                name_form.save()
            else:
                messages.error(self.request, "Beim Speichern der Notizen ist etwas schief gelaufen")

        if notizen_form.is_valid() and (not name_form or name_form.is_valid()):
            return redirect(self.request.build_absolute_uri())
        return render(self.request, self.template_name, self.get_context_data(notizen_form=notizen_form, name_form=name_form))