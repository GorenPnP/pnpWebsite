import sys
from datetime import date

from django.db.models import F, Subquery, OuterRef, Value, Min, ExpressionWrapper, Q
from django.db.models.fields import BooleanField
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic.base import TemplateView

import django_tables2 as tables

from base.abstract_views import DynamicTableView, GenericTable
from character.models import *
from ppServer.mixins import VerifiedAccountMixin
from ppServer.decorators import verified_account


@login_required
@verified_account
def index(request):
    return render(request, 'wiki/index.html', { "topic": "Home" })


class VorteilView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Vorteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar", "is_sellable"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["lte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"],
        "is_sellable": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class NachteilView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Nachteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar", "is_sellable"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["gte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"],
        "is_sellable": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"

class TalentView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Talent
    table_fields = ["titel", "tp", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "tp": ["lte"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class GfsView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
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


@login_required
@verified_account
def stufenplan(request, gfs_id):
    gfs = get_object_or_404(Gfs, id=gfs_id)
    entries = []

    # stufenplan
    for e in GfsStufenplan.objects.filter(gfs=gfs):
        entry = {
            "stufe": e.basis.stufe,
            "ep": e.basis.ep,
            "ap": None if e.basis.ap == 0 else "+{}".format(e.basis.ap),
            "fert": [None if e.basis.fp == 0 else "+{}".format(e.basis.fp),
                    None if e.basis.fg == 0 else "+{} Gr.".format(e.basis.fg)],
            "zauber": "+{}".format(e.zauber) if e.zauber else None,
            "tp": None if e.basis.tp == 0 else "+{}".format(e.basis.tp),
            "wesenkräfte": ", ".join([i.titel for i in e.wesenkräfte.all()]),
            "vorteile": ", ".join([i.titel for i in e.vorteile.all()])
        }
        if hasattr(e, "ability") and e.ability:
            entry["ability"] = {
                "name": e.ability,
                "beschreibung": e.ability.beschreibung,
            }

        entries.append(entry)


    skilltree = [{"sp": entry.sp, "text": []} for entry in SkilltreeBase.objects.filter(stufe__gt=0).order_by("stufe")]

    # Gfs Skilltree
    for s in GfsSkilltreeEntry.objects.prefetch_related("base").filter(gfs=gfs, base__stufe__gt=0):

        # offset is -2, because anyone lacks the bonus (with Stufe 0) and starts at Stufe 2
        skilltree[s.base.stufe-2]["text"].append(s.__repr__())

    # list to string
    for s in skilltree: s["text"] = ", ".join(s["text"])

    # set bonus (has stufe 0) as last entry
    bonus = GfsSkilltreeEntry.objects.prefetch_related("base").filter(gfs=gfs, base__stufe=0)
    skilltree.append({"sp": 0, "text": ", ".join([b.__repr__() for b in bonus])})


    # startboni
    boni = []

    start = []
    gAttrs = GfsAttribut.objects.filter(gfs=gfs)
    for gAttr in gAttrs:
        start.append("{} ({} | {})".format(gAttr.attribut.titel, gAttr.aktuellerWert, gAttr.maxWert))

    boni.append({"field": "Attribute", "val": ", ".join(start)})

    start = []
    gFerts = GfsFertigkeit.objects.filter(gfs=gfs)
    for gFert in gFerts:
        if gFert.fp:
            start.append("{} ({} Bonus-FP)".format(gFert.fertigkeit.titel, gFert.fp))
    boni.append({"field": "Fertigkeiten", "val": ", ".join(start)})

    boni.append({"field": "Vorteile", "val": ", ".join(["{} {}".format(i.teil.titel, i.notizen).strip() for i in GfsVorteil.objects.filter(gfs=gfs)])})
    boni.append({"field": "Nachteile", "val": ", ".join(["{} {}".format(i.teil.titel, i.notizen).strip() for i in GfsNachteil.objects.filter(gfs=gfs)])})
    boni.append({"field": "Zauber", "val": ", ".join(["{} (Tier {})".format(i.item.name, i.tier).strip() for i in GfsZauber.objects.prefetch_related("item").filter(gfs=gfs)])})
    boni.append({"field": "Wesenkräfte", "val": ", ".join([i.wesenkraft.titel for i in GfsWesenkraft.objects.filter(gfs=gfs)])})

    context = {
        "skilltree": skilltree,
        "stufenplan_entries": entries,
        "gfs": gfs,
        "topic": gfs.titel,
        "boni": boni,
        "app_index": "Wiki",
        "app_index_url": reverse("wiki:index")
    }
    return render(request, "wiki/stufenplan.html", context=context)


class PersönlichkeitTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Persönlichkeit
    table_fields = ["titel", "positiv", "negativ"]
    filterset_fields = {
        "titel": ["icontains"],
        "positiv": ["icontains"],
        "negativ": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class SpezialfertigkeitTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Spezialfertigkeit
    table_fields = ["titel", "attr1", "attr2", "ausgleich", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "attr1": ["exact"],
        "attr2": ["exact"],
        "ausgleich": ["exact"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class WissensfertigkeitTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Wissensfertigkeit
    table_fields = ["titel", "attr1", "attr2", "attr3", "fertigkeit", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "attr1": ["exact"],
        "attr2": ["exact"],
        "attr3": ["exact"],
        "fertigkeit": ["exact"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class WesenkraftTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = Wesenkraft
            fields = ["titel", "probe", "manaverbrauch", "wirkung", "wesen"]
            attrs = GenericTable.Meta.attrs


        def render_wesen(self, value, record):
            """ see: enum_wesenkr = [('a', 'alle'),
                    ('m', 'magisch'),
                    ('w', "wesenspezifisch"),
                    ('f', 'manifest < ..')
                ]
            """
            if record.wesen == "w": return ("startet bei Tier 1: ") + ", ".join([gfs.titel for gfs in record.zusatz_gfsspezifisch.all()])
            if record.wesen == "f": return f"Manifest < {record.zusatz_manifest}"
            return value


    model = Wesenkraft
    table_class = Table
    filterset_fields = {
        "titel": ["icontains"],
        "probe": ["icontains"],
        "manaverbrauch": ["icontains"],
        "wirkung": ["icontains"],
        "wesen": ["exact"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class ReligionTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Religion
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class BerufTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Beruf
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }

    app_index = "Wiki"
    app_index_url = "wiki:index"


class GeburtstageView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):
    template_name = "wiki/geburtstage.html"

    def get(self, request):
        context = {
            "topic": "Geburtstage",
            "app_index": "Wiki",
            "app_index_url": reverse("wiki:index"),
        }

        if not Spieler.objects.get(name=request.user.username).geburtstag:
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


class GfsSpecialAbilities(LoginRequiredMixin, DynamicTableView):
    model = GfsAbility
    queryset = GfsAbility.objects.select_related('gfsstufenplan__gfs', 'gfsstufenplan__basis').order_by("name")

    topic = "Gfs-spezifische Fähigkeiten"

    table_fields = ("name", "beschreibung", "gfsstufenplan__gfs", "gfsstufenplan__basis__stufe")
    filterset_fields = {
        "name": ["icontains"],
        "beschreibung": ["icontains"],
        "gfsstufenplan__gfs": ["exact"],
        "gfsstufenplan__basis__stufe": ["exact"],
    }

    export_formats = ["csv", "json", "latex", "ods", "tsv", "xls", "xlsx", "yaml"]
