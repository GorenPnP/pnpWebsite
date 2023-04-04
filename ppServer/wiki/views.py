import sys
from datetime import date
from functools import cmp_to_key

from django.db.models import F, Subquery, OuterRef, Value
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html

import django_tables2 as tables

from base.abstract_views import DynamicTableView, GenericTable
from character.models import *
from ppServer.mixins import VerifiedAccountMixin
from ppServer.decorators import verified_account


@login_required
@verified_account
def index(request):
    context = {"topic": "Home" }
    return render(request, 'wiki/index.html', context)


class VorteilView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Vorteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["lte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"]
    }


class NachteilView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Nachteil
    table_fields = ["titel", "ip", "beschreibung", "wann_wählbar"]
    filterset_fields = {
        "titel": ["icontains"],
        "ip": ["gte"],
        "beschreibung": ["icontains"],
        "wann_wählbar": ["exact"]
    }


class TalentView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Talent
    table_fields = ["titel", "tp", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "tp": ["lte"],
        "beschreibung": ["icontains"]
    }


class GfsView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):

        class AttrColumn(tables.Column):
            def __init__(self, field, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.field = field

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
            fields = ["titel", "difficulty", "ap", "SCH", "IN", "ST", "VER", "GES", "UM", "WK", "MA", "F", "N", "ap_netto"]
            attrs = GenericTable.Meta.attrs

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
        
        def render_titel(self, value, record):
            url = reverse("wiki:stufenplan", args=[record.id])
            return format_html("<a href='{url}'>{name}</a>", url=url, name=value)

    model = Gfs
    table_class = Table
    filterset_fields = {"titel": ["icontains"], "difficulty": ["exact"]}
    template_name = "wiki/gfs.html"

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


# TODO
# class StufenplanDetailView(LoginRequiredMixin, VerifiedAccountMixin, DetailView):
#     model = Gfs


@login_required
@verified_account
def stufenplan(request, gfs_id):
    gfs = get_object_or_404(Gfs, id=gfs_id)
    entries = []

    # stufenplan
    for e in GfsStufenplan.objects.filter(gfs=gfs):
        entry = {"stufe": e.basis.stufe,
                 "ep": e.basis.ep,
                 "ap": None if e.basis.ap == 0 else "+{}".format(e.basis.ap),
                 "fert": [None if e.basis.fp == 0 else "+{}".format(e.basis.fp),
                          None if e.basis.fg == 0 else "+{} Gr.".format(e.basis.fg)],
                 "special_ability": e.special_ability,
                 "special_ability_description": e.special_ability_description,
                 "zauber": "+{}".format(e.zauber) if e.zauber else None,
                 "tp": None if e.basis.tp == 0 else "+{}".format(e.basis.tp),
                 "wesenkräfte": ", ".join([i.titel for i in e.wesenkräfte.all()]),
                 "vorteile": ", ".join([i.titel for i in e.vorteile.all()])
                }

        entries.append(entry)

    # Gfs Skilltree
    skilltree_model = SkilltreeEntryGfs.objects.filter(gfs=gfs)

    # offset is +2, because anyone lacks the bonus (with Stufe 0)
    # otherwise it would be +1
    skilltree = [{} for _ in range(skilltree_model.count() + 2)]
    for s in skilltree_model:
        skilltree[s.context.stufe] = {"sp": s.context.sp, "text": s.text}

    # set bonus (has stufe 0) as last entry
    skilltree.append(skilltree.pop(0))

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
    boni.append({"field": "Wesenkräfte", "val": ", ".join([i.wesenkraft.titel for i in GfsWesenkraft.objects.filter(gfs=gfs)])})

    context = {"skilltree": skilltree, "stufenplan_entries": entries, "gfs": gfs,
               "topic": gfs.titel, "boni": boni}
    return render(request, "wiki/stufenplan.html", context=context)


class PersönlichkeitTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Persönlichkeit
    table_fields = ["titel", "positiv", "negativ"]
    filterset_fields = {
        "titel": ["icontains"],
        "positiv": ["icontains"],
        "negativ": ["icontains"]
    }


class ProfessionView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = Profession
            fields = ["titel", "attr", "fert", "spezial", "wissen"]
            attrs = GenericTable.Meta.attrs

        titel = tables.Column(verbose_name="Profession")
        attr = tables.Column(orderable=False, verbose_name="Attribut Bonus")
        fert = tables.Column(orderable=False, verbose_name="Fertigkeit Bonus")
        spezial = tables.Column(verbose_name="Spezialfert.")
        wissen = tables.Column(verbose_name="Wissensfert.")

        def render_titel(self, value, record):
            return format_html("<a href='{url}'>{name}</a>", url=reverse("wiki:stufenplan_profession", args=[record.pk]), name=value)

        def render_attr(self, value, record):
            vals = [f"{v.attribut.titel} (<strong>+{v.aktuellerWert}</strong>)" for v in ProfessionAttribut.objects.filter(profession=record).exclude(aktuellerWert=0).prefetch_related("attribut")]
            return format_html(", ".join(vals)) if vals else "—"
    
        def render_fert(self, value, record):
            vals = [f"{v.fertigkeit.titel} (<strong>+{v.fp}</strong>)" for v in ProfessionFertigkeit.objects.filter(profession=record).exclude(fp=0).prefetch_related("fertigkeit")]
            return format_html(", ".join(vals)) if vals else "—"

        def render_spezial(self, value, record):
            spezial = record.spezial.all().values("titel")
            return ", ".join([r["titel"] for r in spezial]) if spezial else "—"
        def render_wissen(self, value, record):
            spezial = record.wissen.all().values("titel")
            return ", ".join([r["titel"] for r in spezial]) if spezial else "—"

    model = Profession
    queryset = Profession.objects.all().annotate(attr=Value(1), fert=Value(1)) # let table render attr & fert

    table_class = Table
    filterset_fields = ["titel"]


@login_required
@verified_account
def stufenplan_profession(request, profession_id):
    profession = get_object_or_404(Profession, id=profession_id)

    prof = {}
    attribute = []
    ferts = []
    for pAttr in ProfessionAttribut.objects.filter(profession=profession):
        if pAttr.aktuellerWert:
            attribute.append("{} (+{})".format(pAttr.attribut.titel, pAttr.aktuellerWert))

    for pFert in ProfessionFertigkeit.objects.filter(profession=profession).exclude(fp=0):
        ferts.append("{} (+{})".format(pFert.fertigkeit.titel, pFert.fp))

    prof = {
        "aktuell_bonus": ", ".join(attribute),
        "fp_bonus": ", ".join(ferts),
        "spezial": ", ".join([t.titel for t in profession.spezial.all()]),
        "wissen": ", ".join([t.titel for t in profession.wissen.all()]),

        "beschreibung": profession.beschreibung
    }



    entries = []

    # stufenplan
    for e in ProfessionStufenplan.objects.filter(profession=profession):
        entry = {"stufe": e.basis.stufe,
                 "ep": e.basis.ep,
                 "tp": None if e.tp == 0 else "+{}".format(e.tp),
                 "weiteres": e.weiteres
                 }

        entries.append(entry)

    context = {"stufenplan_entries": entries,
               "topic": profession.titel, "profession": prof}
    return render(request, "wiki/stufenplan_profession.html", context=context)


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
            if record.wesen == "w": return "nur " + ", ".join([gfs.titel for gfs in record.zusatz_gfsspezifisch.all()])
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


class ReligionTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Religion
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }


class BerufTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Beruf
    table_fields = ["titel", "beschreibung"]
    filterset_fields = {
        "titel": ["icontains"],
        "beschreibung": ["icontains"]
    }


class RangRankingTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = RangRankingEntry
            fields = ["ranking", "min_rang", "survival", "power", "skills", "specials"]
            attrs = GenericTable.Meta.attrs

        min_rang = tables.Column(verbose_name="Rang")

        def render_min_rang(self, value, record):
            return f"{value} - {record.max_rang}"

    model = RangRankingEntry
    topic = "Erfahrungsranking"
    table_class = Table
    # queryset = RangRankingEntry.objects.all().annotate(rang=F("min_rang"))
    filterset_fields = {
        "ranking": ["icontains"],
        "min_rang": ["lte"],
        "survival": ["icontains"],
        "power": ["icontains"],
        "skills": ["icontains"],
        "specials": ["icontains"]
    }



def compare_dates(a, b):
    b = b["date"]
    a = date(b.year, a["date"].month, a["date"].day)
    return -1 if a <= b else 1


def day_diff_without_year(some_date, today):
    return (some_date - today).days + 1


def age(birthdate: date):

    today = date.today()
    years = today.year - birthdate.year

    # hadn't had birthday this year (jet)
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day): years -= 1
    return years


@login_required
@verified_account
def geburtstage(request):

    if not Spieler.objects.get(name=request.user.username).geburtstag:
        context = {
            "no_birthdate": "Uns fehlt dein Geburtstag noch.",
            "topic": "Geburtstage"
        }
        return render(request, "wiki/geburtstage.html", context)

    # collect all birthdays in here
    spieler_birthdays = []

    today = date.today()

    # intermediately save next birthday in here
    days_until_next_birthday = sys.maxsize
    spieler_with_next_birthday = []
    for s in Spieler.objects.exclude(geburtstag=None):

        real_name = s.get_real_name()
        spieler_delta = day_diff_without_year(s.geburtstag, today)

        # append spieler & birthday
        spieler_birthdays.append({
            "name": real_name,
            "date": s.geburtstag,
            "age": age(s.geburtstag),
            "next_party": False
        })

        # birthday has already been this year
        if spieler_delta < 0: continue

        # check if spieler has on the same date as the next having one(s)
        if spieler_delta == days_until_next_birthday:
            days_until_next_birthday = spieler_delta
            spieler_with_next_birthday.append(real_name)

        # new closest birthday found, set it
        elif spieler_delta < days_until_next_birthday:
            days_until_next_birthday = spieler_delta
            spieler_with_next_birthday = [real_name]

    # mark spieler in list with next birthday
    for s in spieler_birthdays:
        if s["name"] in spieler_with_next_birthday: s["next_party"] = True

    spieler_birthdays = sorted(spieler_birthdays, key=cmp_to_key(compare_dates))

    # everyone had already had their birthday, set the first one(s) of the year
    if days_until_next_birthday is sys.maxsize and len(spieler_birthdays):
        first_birthday = spieler_birthdays[0]["date"]
        for spieler_birthday in spieler_birthdays:
            if spieler_birthday["date"] != first_birthday: break

            spieler_birthday["next_party"] = True

    context = {"list": spieler_birthdays, "topic": "Geburtstage"}
    return render(request, "wiki/geburtstage.html", context)


class GfsSpecialAbilities(LoginRequiredMixin, DynamicTableView):
    model = GfsStufenplan
    queryset = GfsStufenplan.objects.select_related('gfs').filter(special_ability__isnull=False).exclude(special_ability="").order_by("special_ability")

    topic = "Gfs-spezifische Fähigkeiten"

    table_fields = ("special_ability", "special_ability_description", "gfs", "basis__stufe")
    filterset_fields = {
        "special_ability": ["icontains"],
        "special_ability_description": ["icontains"],
        "gfs": ["exact"],
        "basis__stufe": ["exact"]
    }

    export_formats = ["csv", "json", "latex", "ods", "tsv", "xls", "xlsx", "yaml"]
