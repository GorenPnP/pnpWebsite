from datetime import date
from typing import Any, Dict

from django.db.models import F, Subquery, OuterRef, Min, ExpressionWrapper, Q, Value
from django.db.models.fields import BooleanField, CharField
from django.db.models.functions import Concat
from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

import django_tables2 as tables
from django_filters import FilterSet, ModelChoiceFilter

from base.abstract_views import DynamicTableView, GenericTable
from character.models import *
from ppServer.mixins import VerifiedAccountMixin
from ppServer.decorators import verified_account
from ppServer.utils import ConcatSubquery

from .models import *


@verified_account
def index(request):
    return render(request, 'wiki/index.html', { "topic": "Home" })


class VorteilView(VerifiedAccountMixin, DynamicTableView):
    model = Vorteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar", "is_sellable", "has_implementation"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["lte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"],
        "is_sellable": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class NachteilView(VerifiedAccountMixin, DynamicTableView):
    model = Nachteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar", "is_sellable", "has_implementation"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["gte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"],
        "is_sellable": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"

class TalentView(VerifiedAccountMixin, DynamicTableView):
    model = Talent
    table_fields = ["titel", "tp", "beschreibung", "has_implementation"]
    filterset_fields = {
        "titel": ["icontains"],
        "tp": ["lte"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"

class KlasseListView(VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):

        class Meta:
            model = Klasse
            fields = ["icon", "titel", "beschreibung"]
            attrs = GenericTable.Meta.attrs

        def render_icon(self, value, record):
            return format_html(f'<img src="{value.url}" style="max-width: 64px; max-height 64px;" />')
        
        def render_titel(self, value, record):
            url = reverse("wiki:klasse", args=[record.id])
            return format_html("<a href='{url}'>{name}</a>", url=url, name=value)

    model = Klasse
    table_class = Table
    filterset_fields = {"titel": ["icontains"], "beschreibung": ["icontains"]}
    template_name = "base/dynamic-table.html"

    app_index = "Wiki"
    app_index_url = "wiki:index"

class KlasseDetailView(VerifiedAccountMixin, DetailView):

    queryset = Klasse.objects.prefetch_related("klassestufenplan_set__ability")
    template_name = "wiki/klasse_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs,
            app_index = "Klassen",
            app_index_url = reverse("wiki:klassen"),
        )
        return {**context, "topic": context["object"].titel}


class WesenView(VerifiedAccountMixin, ListView):
    model = Wesen
    template_name = "wiki/wesen.html"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("gfs_set__gfsimage_set")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs,
            topic = "Wesen",
            app_index = "Wiki",
            app_index_url = reverse("wiki:index"),
            gfs=Gfs.objects.all(),
        )
    
    def post(self, request, *args, **kwargs):
        gfs = Gfs.objects.filter(titel=request.POST.get("gfs"))
        if not gfs.count():
            messages.error(request, f"Gfs/Klasse '{request.POST.get('gfs')}' gibt es leider nicht")
            return redirect(request.build_absolute_uri())
                                 
        return redirect(reverse("wiki:stufenplan", args=[gfs.first().id]))


class GfsView(VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):

        class AttrColumn(tables.Column):
            def __init__(self, field, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.field = field

            def order(self, queryset, is_descending):
                queryset = queryset.order_by(("-" if is_descending else "") + self.field, "titel")
                return (queryset, True)

            def render(self, value, record):
                curr = getattr(record, f"{self.field}_curr")
                max = getattr(record, f"{self.field}_max")
                text = f"{curr} / {max}"
                css_class = ""
                if value <= 5: css_class = "text-danger"
                if value >= 14: css_class = "text-success"

                return format_html(f'<span class="{css_class} text-nowrap">{text}</span>')

        class Meta:
            model = Gfs
            fields = ["icon", "titel", "difficulty", "ap", "SCH", "IN", "ST", "VER", "GES", "UM", "WK", "MA", "F", "N", "ap_netto"]
            attrs = GenericTable.Meta.attrs

        def order_ap_netto(self, queryset, is_descending):
            queryset = queryset.order_by(("-" if is_descending else "") + "ap_netto", "titel")
            return (queryset, True)

        icon = tables.Column(verbose_name="")
        titel = tables.Column(verbose_name="Gfs / Klasse")

        SCH = AttrColumn(field="SCH")
        IN = AttrColumn(field="IN")
        ST = AttrColumn(field="ST")
        VER = AttrColumn(field="VER")
        GES = AttrColumn(field="GES")
        UM = AttrColumn(field="UM")
        WK = AttrColumn(field="WK")
        MA = AttrColumn(field="MA")
        F = AttrColumn(field="F")
        N = AttrColumn(field="N")

        def render_icon(self, value, record):
            return format_html(f'<img src="{value.url}" style="max-width: 64px; max-height 64px;" />')
        
        def render_titel(self, value, record):
            url = reverse("wiki:stufenplan", args=[record.id])
            return format_html("<a href='{url}'>{name}</a>", url=url, name=value)

    model = Gfs
    table_class = Table
    filterset_fields = {"titel": ["icontains"], "difficulty": ["exact"]}
    template_name = "wiki/gfs.html"

    app_index = "Wiki"
    app_index_url = "wiki:index"

    def get_queryset(self):
        # original qs
        qs = super().get_queryset()

        attr_qs = GfsAttribut.objects.select_related("attribut", "gfs").filter(gfs__id=OuterRef("id"))
        return qs\
            .annotate(
                SCH_curr=Subquery(attr_qs.filter(attribut__titel="SCH").values("aktuellerWert")[:1]),
                SCH_max=Subquery(attr_qs.filter(attribut__titel="SCH").values("maxWert")[:1]),
                SCH=F("SCH_curr") + 2* F("SCH_max"),

                IN_curr=Subquery(attr_qs.filter(attribut__titel="IN").values("aktuellerWert")[:1]),
                IN_max=Subquery(attr_qs.filter(attribut__titel="IN").values("maxWert")[:1]),
                IN=F("IN_curr") + 2* F("IN_max"),

                ST_curr=Subquery(attr_qs.filter(attribut__titel="ST").values("aktuellerWert")[:1]),
                ST_max=Subquery(attr_qs.filter(attribut__titel="ST").values("maxWert")[:1]),
                ST=F("ST_curr") + 2* F("ST_max"),

                VER_curr=Subquery(attr_qs.filter(attribut__titel="VER").values("aktuellerWert")[:1]),
                VER_max=Subquery(attr_qs.filter(attribut__titel="VER").values("maxWert")[:1]),
                VER=F("VER_curr") + 2* F("VER_max"),

                GES_curr=Subquery(attr_qs.filter(attribut__titel="GES").values("aktuellerWert")[:1]),
                GES_max=Subquery(attr_qs.filter(attribut__titel="GES").values("maxWert")[:1]),
                GES=F("GES_curr") + 2* F("GES_max"),

                UM_curr=Subquery(attr_qs.filter(attribut__titel="UM").values("aktuellerWert")[:1]),
                UM_max=Subquery(attr_qs.filter(attribut__titel="UM").values("maxWert")[:1]),
                UM=F("UM_curr") + 2* F("UM_max"),

                WK_curr=Subquery(attr_qs.filter(attribut__titel="WK").values("aktuellerWert")[:1]),
                WK_max=Subquery(attr_qs.filter(attribut__titel="WK").values("maxWert")[:1]),
                WK=F("WK_curr") + 2* F("WK_max"),

                MA_curr=Subquery(attr_qs.filter(attribut__titel="MA").values("aktuellerWert")[:1]),
                MA_max=Subquery(attr_qs.filter(attribut__titel="MA").values("maxWert")[:1]),
                MA=F("MA_curr") + 2* F("MA_max"),

                F_curr=Subquery(attr_qs.filter(attribut__titel="F").values("aktuellerWert")[:1]),
                F_max=Subquery(attr_qs.filter(attribut__titel="F").values("maxWert")[:1]),
                F=F("F_curr") + 2* F("F_max"),

                N_curr=Subquery(attr_qs.filter(attribut__titel="N").values("aktuellerWert")[:1]),
                N_max=Subquery(attr_qs.filter(attribut__titel="N").values("maxWert")[:1]),
                N=F("N_curr") + 2* F("N_max"),

                ap_netto=F("SCH") + F("IN") + F("ST") + F("VER") + F("GES") + F("UM") + F("WK") + F("MA") + F("F") + F("N") - F("ap")
            )


@verified_account
def stufenplan(request, gfs_id):

    # get Gfs with startboni
    gfs_qs = Gfs.objects.prefetch_related("gfsimage_set").annotate(
        start_attribut = ConcatSubquery(GfsAttribut.objects.filter(gfs=OuterRef("pk")).annotate(text=Concat("attribut__titel", Value(" "), "aktuellerWert", Value("/"), "maxWert", output_field=CharField())).values("text"), separator=", "),
        start_fertigkeit = ConcatSubquery(GfsFertigkeit.objects.filter(gfs=OuterRef("pk"), fp__gt=0).annotate(text=Concat("fertigkeit__titel", Value(" +"), "fp", output_field=CharField())).values("text"), separator=", "),
        start_vorteil = ConcatSubquery(GfsVorteil.objects.filter(gfs=OuterRef("pk")).annotate(text=Concat("teil__titel", Value(" "), "notizen", output_field=CharField())).values("text"), separator=", "),
        start_nachteil = ConcatSubquery(GfsNachteil.objects.filter(gfs=OuterRef("pk")).annotate(text=Concat("teil__titel", Value(" "), "notizen", output_field=CharField())).values("text"), separator=", "),
        start_zauber = ConcatSubquery(GfsZauber.objects.filter(gfs=OuterRef("pk")).annotate(text=Concat("item__name", Value(" (Tier "), "tier", Value(")"), output_field=CharField())).values("text"), separator=", "),
        start_wesenkraft = ConcatSubquery(GfsWesenkraft.objects.filter(gfs=OuterRef("pk")).values("wesenkraft__titel"), separator=", "),
    )
    gfs = get_object_or_404(gfs_qs, id=gfs_id)

    # startboni
    boni = [
        {"field": "Attribute", "val": gfs.start_attribut},
        {"field": "Fertigkeiten", "val": gfs.start_fertigkeit},
        {"field": "Vorteile", "val": gfs.start_vorteil},
        {"field": "Nachteile", "val": gfs.start_nachteil},
        {"field": "Zauber", "val": gfs.start_zauber},
        {"field": "Wesenkräfte", "val": gfs.start_wesenkraft},
        {"field": "Startmanifest", "val": gfs.startmanifest},
        {"field": "Schaden waffenloser Kampf (andere Form) in HP", "val": f"{gfs.wesenschaden_waff_kampf or 0} ({gfs.wesenschaden_andere_gestalt or 0})"},
        {"field": "Kosten in AP", "val": gfs.ap},
    ]


    # Skilltree
    skilltree_subquery = GfsSkilltreeEntry.objects\
        .prefetch_related("base", "fertigkeit", "vorteil", "nachteil", "wesenkraft", "spezialfertigkeit", "wissensfertigkeit")\
        .filter(gfs=gfs)
    skilltree = list(SkilltreeBase.objects.values("stufe", "sp").order_by("stufe"))
    for skill in skilltree_subquery:
        i = skill.base.stufe - skilltree[0]["stufe"]
        if "text" in skilltree[i]:
            skilltree[i]["text"].append(skill.__repr__())
        else:
            skilltree[i]["text"] = [skill.__repr__()]


    # Stufenplan
    entries = []
    for e in GfsStufenplan.objects.prefetch_related("basis", "ability").filter(gfs=gfs).annotate(
        vorteile_string = ConcatSubquery(Vorteil.objects.filter(gfsstufenplan=OuterRef("pk")).values("titel"), separator=", "),
        wesenkräfte_string = ConcatSubquery(Wesenkraft.objects.filter(gfsstufenplan=OuterRef("pk")).values("titel"), separator=", "),
    ):
        entry = {
            "stufe": e.basis.stufe,
            "ep": e.basis.ep,
            "ap": f"+{e.basis.ap}" if e.basis.ap else None,
            "fert": [f"+{e.basis.fp}" if e.basis.fp else None,
                    f"+{e.basis.fg} Gr.".format() if e.basis.fg else None],
            "zauber": f"+{e.zauber}" if e.zauber else None,
            "tp": f"+{e.basis.tp}" if e.basis.tp else None,
            "wesenkräfte": e.wesenkräfte_string,
            "vorteile": e.vorteile_string
        }
        if hasattr(e, "ability") and e.ability:
            entry["ability"] = {
                "name": e.ability,
                "beschreibung": e.ability.beschreibung,
            }

        entries.append(entry)


    context = {
        "gfs": gfs,
        "boni": boni,
        "skilltree": skilltree,
        "stufenplan_entries": entries,
        "topic": gfs.titel,
        "app_index": Gfs._meta.verbose_name_plural,
        "app_index_url": reverse("wiki:gfs")
    }
    return render(request, "wiki/stufenplan.html", context=context)


class PersönlichkeitTableView(VerifiedAccountMixin, DynamicTableView):
    model = Persönlichkeit
    table_fields = ["titel", "beschreibung", "charakterbeispiele"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"],
        "charakterbeispiele": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class SpezialfertigkeitTableView(VerifiedAccountMixin, DynamicTableView):
    class SpF_Filter(FilterSet):
        class Meta:
            model = Spezialfertigkeit
            fields = {
                "titel": ["icontains"],
                "attr1": ["exact"],
                "attr2": ["exact"],
                "ausgleich": ["exact"],
                "beschreibung": ["icontains"]
            }

        attr1 = ModelChoiceFilter(
            field_name="attr1",
            method="filter_attr",
            queryset=Attribut.objects.all()
        )
        attr2 = ModelChoiceFilter(
            field_name="attr2",
            method="filter_attr",
            queryset=Attribut.objects.all()
        )
        ausgleich = ModelChoiceFilter(
            field_name="ausgleich",
            method="filter_ausgleich",
            queryset=Fertigkeit.objects.prefetch_related("attribut").all()
        )

        def filter_attr(self, queryset, name, value):
            qs = queryset.prefetch_related("attr1", "attr2")
            return qs.filter(**{name: value}) if value else qs

        def filter_ausgleich(self, queryset, name, value):
            qs = queryset.prefetch_related("ausgleich__attribut")
            return qs.filter(ausgleich=value) if value else qs
    
    model = Spezialfertigkeit
    table_fields = ["titel", "attr1", "attr2", "ausgleich", "beschreibung"]
    filterset_class = SpF_Filter

    app_index = "Wiki"
    app_index_url = "wiki:index"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("attr1", "attr2", "ausgleich__attribut")


class WissensfertigkeitTableView(VerifiedAccountMixin, DynamicTableView):
    class WF_Filter(FilterSet):
        class Meta:
            model = Wissensfertigkeit
            fields = {
                "titel": ["icontains"],
                "attr1": ["exact"],
                "attr2": ["exact"],
                "attr3": ["exact"],
                "fertigkeit": ["exact"],
                "beschreibung": ["icontains"]
            }

        attr1 = ModelChoiceFilter(
            field_name="attr1",
            method="filter_attr",
            queryset=Attribut.objects.all()
        )
        attr2 = ModelChoiceFilter(
            field_name="attr2",
            method="filter_attr",
            queryset=Attribut.objects.all()
        )
        attr3 = ModelChoiceFilter(
            field_name="attr3",
            method="filter_attr",
            queryset=Attribut.objects.all()
        )
        fertigkeit = ModelChoiceFilter(
            field_name="fertigkeit",
            method="filter_fertigkeit",
            queryset=Fertigkeit.objects.prefetch_related("attribut").all()
        )

        def filter_attr(self, queryset, name, value):
            qs = queryset.prefetch_related("attr1", "attr2")
            return qs.filter(**{name: value}) if value else qs

        def filter_fertigkeit(self, queryset, name, value):
            qs = queryset.prefetch_related("fertigkeit__attribut")
            return qs.filter(fertigkeit=value) if value else qs

    model = Wissensfertigkeit
    table_fields = ["titel", "attr1", "attr2", "attr3", "fertigkeit", "beschreibung"]
    filterset_class = WF_Filter

    app_index = "Wiki"
    app_index_url = "wiki:index"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("attr1", "attr2", "attr3", "fertigkeit__attribut")


class WesenkraftTableView(VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = Wesenkraft
            fields = ["titel", "probe", "manaverbrauch", "wirkung", "skilled_gfs"]
            attrs = GenericTable.Meta.attrs


        def render_skilled_gfs(self, value, record):
            return ("startet bei Tier 1: ") + ", ".join([gfs.titel for gfs in record.skilled_gfs.all()])


    model = Wesenkraft
    table_class = Table
    filterset_fields = {
        "titel": ["icontains"],
        "probe": ["icontains"],
        "manaverbrauch": ["icontains"],
        "wirkung": ["icontains"],
        "skilled_gfs": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("skilled_gfs__wesen")


class ReligionTableView(VerifiedAccountMixin, DynamicTableView):
    model = Religion
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"
    plus = "+ Religion"
    plus_url = "admin:character_religion_add"


class BerufTableView(VerifiedAccountMixin, DynamicTableView):
    model = Beruf
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"
    plus = "+ Beruf"
    plus_url = "admin:character_beruf_add"


class GeburtstageView(VerifiedAccountMixin, TemplateView):
    template_name = "wiki/geburtstage.html"

    def get(self, request):
        context = {
            "topic": "Geburtstage",
            "app_index": "Wiki",
            "app_index_url": reverse("wiki:index"),
        }

        if not request.spieler.instance.geburtstag:
            messages.error(request, "Dein Geburtstag fehlt noch. Teile ihn uns mit, damit du die Liste aller Geburtstage sehen kannst!")
            return render(request, self.template_name, context)
        
        # score each date by month *31 + day to get the closest positive to today

        # get today's score
        today = date.today().month * 31 + date.today().day
        # get lowest positive of all players
        lowest_score = Spieler.objects\
            .filter(geburtstag__isnull=False)\
            .order_by("geburtstag__month", "geburtstag__day")\
            .annotate(
                score = F("geburtstag__month") *31 + F("geburtstag__day") - today
            )\
            .filter(score__gte=0)\
            .aggregate(
                min_score = Min("score")
            )["min_score"]

        # use it to annotate "next_party"
        context["spieler"] = Spieler.objects\
            .filter(geburtstag__isnull=False)\
            .order_by("geburtstag__month", "geburtstag__day")\
            .annotate(
                score = F("geburtstag__month") *31 + F("geburtstag__day") - today,
                next_party = ExpressionWrapper(Q(score=lowest_score), output_field=BooleanField())
            )
        
        # render view
        return render(request, self.template_name, context)


class GfsSpecialAbilities(VerifiedAccountMixin, DynamicTableView):
    model = GfsAbility
    queryset = GfsAbility.objects.select_related('gfsstufenplan__gfs', 'gfsstufenplan__basis').order_by("name")

    topic = "Gfs-spezifische Fähigkeiten"

    table_fields = ("name", "beschreibung", "gfsstufenplan__gfs", "gfsstufenplan__basis__stufe", "has_implementation")
    filterset_fields = {
        "name": ["icontains"],
        "beschreibung": ["icontains"],
        "gfsstufenplan__gfs": ["exact"],
        "gfsstufenplan__basis__stufe": ["exact"],
    }

    export_formats = ["csv", "json", "latex", "tsv"]


class RuleListView(VerifiedAccountMixin, ListView):

    model = Rule
    template_name = "wiki/rule_index.html"


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs,
            topic = "Regeln",
            app_index = "Wiki",
            app_index_url = reverse("wiki:index"),
        )

class RuleDetailView(VerifiedAccountMixin, DetailView):

    model = Rule
    template_name = "wiki/rule_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs,
            app_index = "Regeln",
            app_index_url = reverse("wiki:rule_index"),
        )
        context["topic"] = f'{context["object"].nr}: {context["object"].titel}'
        return context

