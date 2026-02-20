import locale, re
from collections import OrderedDict
from typing import Any, Dict

from django.apps import apps
from django.contrib import messages
from django.db import transaction
from django.db.models import Value, F, CharField, OuterRef, Case, When
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

import django_tables2 as tables

from base.abstract_views import GenericTable
from cards.models import Card, Transaction
from effect.models import RelEffect
from log.create_log import render_number
from log.models import Log
from ppServer.decorators import verified_account
from ppServer.mixins import VerifiedAccountMixin, CopiesCharsMixin
from ppServer.utils import ConcatSubquery
from shop.views.list import shopmodel_list, RenderableTable, annotate_other

from .forms import *
from .models import *

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
            "tags": Tag.objects.filter(spieler=self.request.spieler).annotate(num=Count("charakter")).order_by("name"),
            'topic': "Charaktere",
            "plus": "+ Charakter",
            "plus_url": reverse('create:gfs'),
        }
    
    def get(self, request, *args, **kwargs):
        tagname = self.request.GET["tag"] if "tag" in self.request.GET else None
        context = self.get_context_data(**kwargs)

        if tagname and Tag.objects.filter(name=tagname, spieler=self.request.spieler).exists():
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
    
    class ItemTable(RenderableTable):
        class Meta(RenderableTable.Meta):
            orderable = False

        def __init__(self, *args, csrf_token: str, **kwargs):
            super().__init__(*args, **kwargs)

            self.csrf_token = csrf_token


        def render_item__icon(self, value, record):
            Model = apps.get_model('shop', record["model_name"])
            instance = Model.objects.get(pk=self._get(record, "item__pk"))

            # use python model .objects.get().getIconUrl()
            return format_html("<img src='{url}' loading='lazy'>", url=instance.getIconUrl())
        
        def render_item__beschreibung(self, value):
            return self.render_beschreibung(value)
        
        def render_art(self, value):
            return value

        def render_other(self, value):
            value = value.replace("item__", "")
            return super().render_other(value)

        def render_use(self, value, record):
            relmodel_name = f"Rel{record['model_name']}"
            pk = record["pk"]
            
            RelModel = apps.get_model("character", relmodel_name)
            if RelModel == RelRamsch: price = 0
            else:
                FirmaShopModel = RelModel.item.field.related_model.firmen.through
                relitem = get_object_or_404(RelModel.objects.prefetch_related(f"item__{FirmaShopModel._meta.model_name}_set__firma"), pk=pk)
                price = relitem.cheapest() or 0

            href = reverse("character:remove_item", args=[relmodel_name, pk])
            sell_btn = f'<button type="submit" class="btn btn-sm btn-warning" name="sell">verkaufen (je {int(price * 0.4+.5):n} Dr.)</button>'
            return format_html(
                f"""<form method="post" action="{href}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{self.csrf_token}"/>
                    <input type="number" class="form-control" style="width: 10ch" placeholder="Anzahl" aria-label="Anzahl" name="amount" value="1" min="1" max="{record['anz']}" step="1" required>
                    <button type="submit" class="btn btn-sm btn-danger" name="use">verbrauchen</button>
                    {sell_btn if price else ''}
                </form>"""
            )
        
        @staticmethod
        def get_queryset(char: Charakter, RelShopQS: QuerySet[models.Model], field_names: list[str]) -> list:
            try:
                Shop = apps.get_model("shop", RelShopQS.model._meta.model_name[3:])
            except:

                # RelRamsch
                return RelShopQS\
                    .filter(char=char)\
                    .annotate(
                        model_name=Value("Ramsch"),
                        art=Value(RelShopQS.model._meta.verbose_name),
                        
                        item__pk=F("pk"),
                        item__icon=Value(""),
                        item__name=F("item"),
                        stufe=Value(None, output_field=models.IntegerField()),
                        item__beschreibung=Value("(selbst angelegt)"),
                        other=Value(""),
                        notizen=Value("-"),
                        use=Value("-"),
                    )\
                    .values(*field_names, "pk", "model_name", "art", "item__pk")

            # normal RelShop-case

            other_fields = [f for f in Shop.getShopDisplayFields() if f not in ["preis", "ab_stufe"] and f"item__{f}" not in field_names]

            return RelShopQS\
                .filter(char=char, item__frei_editierbar=False)\
                .annotate(
                    model_name=Value(Shop._meta.model_name),
                    art=Value(Shop._meta.verbose_name),
                    use=Value("-"),
                    other=Subquery(Shop.objects.filter(pk=OuterRef("item__pk")).annotate(**annotate_other(Shop, other_fields)).values_list("other", flat=True)),
                )\
                .values(*field_names, "pk", "model_name", "art", "item__pk")


    template_name = "character/show.html"
    model = Charakter
    queryset = Charakter.objects.prefetch_related(
        "gfs", "persönlichkeit", "religion", "beruf", "relfertigkeit_set__fertigkeit__attribut", "relgruppe_set",
        "relklasse_set__klasse", "relklasseability_set__ability", "relattribut_set__attribut", "relwesenkraft_set__wesenkraft", "reltalent_set__talent",
        "relgfsability_set__ability", "affektivität_set",
        "relzauber_set__item", "relrituale_runen_set__item", "relschusswaffen_set__item", "relwaffen_werkzeuge_set__item",
        "relmagazin_set__item", "relpfeil_bolzen_set__item", "relmagische_ausrüstung_set__item", "relrüstung_set__item",
        "relausrüstung_technik_set__item", "relfahrzeug_set__item", "releinbauten_set__item", "relalchemie_set__item",
        "reltinker_set__item", "relbegleiter_set__item", "relramsch_set", "card"
    )

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
            **self.get_nah_fernkampf(char),
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
                return [name for token, name in enums.gruppen_enum if token == value][0]

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
            self._rel_attribute["ST"].aktuell() * 5,
            math.floor(char.larp_rang / 20) if char.larp else char.ep_stufe * 2,
            char.HPplus_fix if char.HPplus_fix is not None else char.HPplus,
        ]
        ghp = [
            self._rel_attribute["WK"].aktuell() * 5,
            math.floor(char.larp_rang / 20) if char.larp else char.ep_stufe * 2,
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

        table_fields = OrderedDict(
            anz = tables.Column(),
            item__icon = tables.Column(verbose_name=""),
            item__name = tables.Column(verbose_name="Name"),
            stufe = tables.Column(),
            item__beschreibung = tables.Column(verbose_name="Beschreibung"),
            art = tables.Column(),
            other = tables.Column(verbose_name=""),
            notizen = tables.Column(),
            use = tables.Column(verbose_name=""),
        )

        objects = []

        # Misc Shop items
        for Model in [m for m in shopmodel_list if m not in [Waffen_Werkzeuge, Schusswaffen, Zauber, Rituale_Runen]]:
            RelModel = apps.get_model("character", f"Rel{Model._meta.model_name}")
            objects += ShowView.ItemTable.get_queryset(char, RelModel.objects.prefetch_related("item__firmen"), table_fields.keys())

        # RelRamsch
        objects += ShowView.ItemTable.get_queryset(char, char.relramsch_set, table_fields.keys())
            
        return {
            "inventory__table": ShowView.ItemTable(
                sorted(objects, key=lambda o: o["item__name"].lower()),
                extra_columns = [(k, v) for k, v in table_fields.items()],
                csrf_token=get_token(self.request)
            ),
            "ramsch_form": CreateRamschForm(initial={"char": char.pk}),
            "inventory__random_items": format_html(re.sub("\n", "<br>", char.sonstige_items, 0, re.MULTILINE))
        }

    def get_zauber(self, char):
        class ZauberTable(ShowView.ItemTable):
            class Meta(ShowView.ItemTable.Meta): pass

            def render_item__beschreibung(self, value):
                regex = "Tier [0IVX]+:"
                return format_html(re.sub(regex, lambda match: f"<br><b>{match.group(0)}</b>", value))
            
            def render_learned(self, value):
                return "✔" if value else "✖"


        table_fields = OrderedDict(
            learned = tables.Column(verbose_name="gelernt"),
            item__icon = tables.Column(verbose_name=""),
            item__name = tables.Column(),
            tier = tables.Column(),
            item__beschreibung = tables.Column(),
            item__manaverbrauch = tables.Column(),
            item__astralschaden = tables.Column(),
            other = tables.Column(verbose_name=""),
            notizen = tables.Column(),
        )

        return {
            "zauber__table": ZauberTable(
                ZauberTable.get_queryset(char, char.relzauber_set.prefetch_related("item__firmen"), table_fields.keys()),
                extra_columns = [(k, v) for k, v in table_fields.items()],
                csrf_token=get_token(self.request),
            )
        }

    def get_ritual(self, char):
        table_fields = OrderedDict(
            anz = tables.Column(),
            item__icon = tables.Column(verbose_name=""),
            item__name = tables.Column(verbose_name="Name"),
            stufe = tables.Column(),
            item__beschreibung = tables.Column(verbose_name="Beschreibung"),
            other = tables.Column(verbose_name=""),
            notizen = tables.Column(),
            use = tables.Column(verbose_name=""),
        )

        return {
            "ritual__table": ShowView.ItemTable(
                ShowView.ItemTable.get_queryset(char, char.relrituale_runen_set.prefetch_related("item__firmen"), table_fields.keys()),
                extra_columns = [(k, v) for k, v in table_fields.items()],
                csrf_token=get_token(self.request),
            )
        }

    def get_nah_fernkampf(self, char):
        class WaffenTable(ShowView.ItemTable):
            class Meta(ShowView.ItemTable.Meta): pass

            def render_item__zs(self, value, record):
                return f"{value} (ab {record.item.erfolge})"

        table_fields = OrderedDict(
            anz = tables.Column(),
            item__icon = tables.Column(verbose_name=""),
            item__name = tables.Column(verbose_name="Name"),
            stufe = tables.Column(),
            item__beschreibung = tables.Column(verbose_name="Beschreibung"),
            other = tables.Column(verbose_name=""),
            notizen = tables.Column(),
            use = tables.Column(verbose_name=""),
        )

        return {
            "nahkampf__table": WaffenTable(
                ShowView.ItemTable.get_queryset(char, char.relwaffen_werkzeuge_set.prefetch_related("item__firmen"), table_fields.keys()),
                extra_columns = [(k, v) for k, v in table_fields.items()],
                csrf_token=get_token(self.request)
            ),
            "fernkampf__table": WaffenTable(
                ShowView.ItemTable.get_queryset(char, char.relschusswaffen_set.prefetch_related("item__firmen"), table_fields.keys()),
                extra_columns = [(k, v) for k, v in table_fields.items()],
                csrf_token=get_token(self.request)
            )
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
                        "source_shopAusrüstungTechnik__char", "source_shopAusrüstungTechnik__item",
                        "source_shopEinbauten__char", "source_shopEinbauten__item",
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
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value): qs = qs.filter(char__eigentümer=request.spieler)
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
    tag = Tag.objects.filter(pk=pk, spieler=request.spieler).first()
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
    tag = Tag.objects.filter(pk=pk, spieler=request.spieler).first()
    num_tags_and_chars_deleted = Tag.objects.filter(pk=pk, spieler=request.spieler).delete()[0]
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
        notizen=f"{relramsch_item.anz}x {relramsch_item.item}",
    )

    messages.success(request, f"{relramsch_item.anz}x {relramsch_item.item} angelegt")
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
        RelRamsch.objects.create(char=char, anz=1, item=form.cleaned_data["reason"])

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


def _decrease_anz_relshop(request, relshop_model: str, rel_item_pk: int):
    try:
        Model = apps.get_model('character', relshop_model)
        # assert model
        if not issubclass(Model, RelShop) and Model != RelRamsch: raise LookupError()

        amount = int(request.POST.get("amount"))
    except LookupError:
        messages.error(request, "Anfrage fehlerhaft")
        return {"success": False, "redirect": redirect("character:index")}

    # assert user requesting to use an item
    if not request.user.has_perm(CustomPermission.SPIELLEITUNG.value) and not Model.objects.filter(pk=rel_item_pk, char__eigentümer=request.spieler).exists():
        messages.error(request, "Es ist nicht dein Charakter, von dem du Items benutzen willst.")
        return redirect("character:index")

    # assert item existance
    rel_shop = Model.objects.prefetch_related("char__eigentümer")
    if issubclass(Model, RelShop): rel_shop = rel_shop.prefetch_related("item")
    rel_shop = rel_shop.filter(pk=rel_item_pk).first()

    if not rel_shop:
        messages.error(request, "Item konnte nicht im Inventar gefunden werden.")
        return {"success": False, "redirect": redirect("character:index")}

    if rel_shop.anz < amount:
        messages.error(request, "Zu wenige Items im Inventar gefunden.")
        return {"success": False, "redirect": redirect("character:index")}

    char = rel_shop.char
    item = rel_shop.item
    item_name = rel_shop.item.name if issubclass(Model, RelShop) else rel_shop.item
    stufe = rel_shop.stufe or 1 if issubclass(Model, RelShop) else 1

    # remove item
    if rel_shop.anz == amount:
        rel_shop.delete()
    else:
        rel_shop.anz -= amount
        rel_shop.save(update_fields=["anz"])

    return {"success": True, "stufe": stufe, "amount": amount, "char": char, "item_name": item_name, "item": item}


@require_POST
@verified_account
def remove_relshop(request, relshop_model, pk):
    res = _decrease_anz_relshop(request, relshop_model, pk)
    if not res["success"]: return res["redirect"]

    if "sell" in request.POST:
        # get sell price
        price = 0
        Model = apps.get_model('character', relshop_model)
        if issubclass(Model, RelShop):  # is not RelRamsch
            price = res["item"].cheapest(res["stufe"]) or 0
            
            # 40% of cheapest price
            price = int((price * .4) + .5) * res["amount"]
        
        # receive money
        card = res["char"].card
        card.money += price
        card.save(update_fields=["money"])

        Transaction.objects.create(receiver=card, amount=price, reason=f"verkaufe {res['amount']}x {res['item_name']}")

        # log transaction
        Log.objects.create(
            spieler=request.spieler,
            char=res["char"],
            art="w", # Inventar-Item verbraucht
            kosten=f"Erlös: {price:n} Drachmen",
            notizen=f"{res['amount']}x {res['item_name']}",
        )
        messages.success(request, f'Du hast {res["amount"]} von "{res["item_name"]}" für {price:n} Dr. verkauft')

    if "use" in request.POST:
        # log usage
        Log.objects.create(
            spieler=request.spieler,
            char=res["char"],
            art="j", # Inventar-Item verbraucht
            kosten="",
            notizen=f"{res['amount']}x {res['item_name']}",
        )
        messages.success(request, f'Du hast {res["amount"]} von "{res["item_name"]}" verbraucht')

    return redirect(reverse("character:show", args=[res["char"].id]))


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
