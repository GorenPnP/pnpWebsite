import sys
from datetime import date
from functools import cmp_to_key

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

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


@login_required
@verified_account
def gfs(request):
    all_gfs: list = []
    for gfs in Gfs.objects.all():
        attrs = gfs.attr_calc()
        powerLevel = sum([val["aktuellerWert"] + 2*val["maxWert"] for val in attrs]) - gfs.ap

        all_gfs.append({
            "id": gfs.id,
            "titel": gfs.titel,
            "ap": gfs.ap,
            "attrs": attrs,
            "powerLevel": powerLevel
        })

    return render(request, 'wiki/gfs.html', {'topic': 'Gfs/Klassen', "heading": Attribut.objects.all(),
                                               "gfs": all_gfs})


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
               "topic": gfs.titel, "beschreibung": gfs.beschreibung, "boni": boni}
    return render(request, "wiki/stufenplan.html", context=context)


class PersönlichkeitTableView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
    model = Persönlichkeit
    table_fields = ["titel", "positiv", "negativ"]
    filterset_fields = {
        "titel": ["icontains"],
        "positiv": ["icontains"],
        "negativ": ["icontains"]
    }


@login_required
@verified_account
def profession(request):
    profs = Profession.objects.all()
    entries = []

    for p in profs:

        attribute = []
        maxima = []
        ferts = []

        for pAttr in ProfessionAttribut.objects.filter(profession=p):
            if pAttr.aktuellerWert:
                attribute.append("{} (<span class='emphasis'>+{}</span>)".format(pAttr.attribut.titel, pAttr.aktuellerWert))

            if pAttr.maxWert:
                maxima.append("{} (<span class='emphasis'>+{}</span>)".format(pAttr.attribut.titel, pAttr.maxWert))

        for pFert in ProfessionFertigkeit.objects.filter(profession=p).exclude(fp=0):
            ferts.append("{} (<span class='emphasis'>+{}</span>)".format(pFert.fertigkeit.titel, pFert.fp))

        entry = {
            "aktuell_bonus": ", ".join(attribute),
            "max_bonus": ", ".join(maxima), "fp_bonus": ", ".join(ferts),
            "titel": p.titel, "id": p.id, "talente": ", ".join([t.titel for t in p.talente.all()]),
            "spezial": ", ".join([t.titel for t in p.spezial.all()]),
            "wissen": ", ".join([t.titel for t in p.wissen.all()])
        }
        entries.append(entry)

    return render(request, 'wiki/profession.html', {'topic': 'Professionen', "professionen": entries})


@login_required
@verified_account
def stufenplan_profession(request, profession_id):
    profession = get_object_or_404(Profession, id=profession_id)

    prof = {}
    attribute = []
    maxima = []
    ferts = []
    for pAttr in ProfessionAttribut.objects.filter(profession=profession):
        if pAttr.aktuellerWert:
            attribute.append("{} (+{})".format(pAttr.attribut.titel, pAttr.aktuellerWert))

        if pAttr.maxWert:
            maxima.append("{} (+{})".format(pAttr.attribut.titel, pAttr.maxWert))

    for pFert in ProfessionFertigkeit.objects.filter(profession=profession).exclude(fp=0):
        ferts.append("{} (+{})".format(pFert.fertigkeit.titel, pFert.fp))

    prof = {
        "aktuell_bonus": ", ".join(attribute),
        "max_bonus": ", ".join(maxima),
        "fp_bonus": ", ".join(ferts),
        "talente": ", ".join([t.titel for t in profession.talente.all()]),
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
            attrs = {"class": "table table-dark table-striped table-hover"}


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
            attrs = {"class": "table table-dark table-striped table-hover"}

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
