from ppServer.decorators import verified_account
from functools import cmp_to_key

import math, re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from character.models import *
from django.utils.datetime_safe import datetime
from log.views import logAlleMAverloren
from create.models import NewCharakter


@login_required
@verified_account
def index(request):
    context = {"topic": "Home" }
    return render(request, 'wiki/index.html', context)


@login_required
@verified_account
def vorteile(request):
    context = {'topic': 'Vorteile', 'list': Vorteil.objects.all().order_by("titel")}
    return render(request, 'wiki/vor_nachteile.html', context)


@login_required
@verified_account
def nachteile(request):
    context = {'topic': 'Nachteile', 'list': Nachteil.objects.all().order_by("titel")}
    return render(request, 'wiki/vor_nachteile.html', context)


@login_required
@verified_account
def talente(request):
    context = {"topic": "Talente", "list": Talent.objects.all()}
    return render(request, "wiki/talent.html", context)


@login_required
@verified_account
def gfs(request):
    return render(request, 'wiki/gfs.html', {'topic': 'Gfs/Klassen', "heading": Attribut.objects.all(),
                                               "gfs": Gfs.objects.all()})


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
                 "weiteres": e.weiteres,
                 "zauber": "+{}".format(e.zauber) if e.zauber else None,
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
        if gfs.wesen:
            sAttr = SpeziesAttribut.objects.get(attribut=gAttr.attribut, spezies=gfs.wesen)
        aktuellerWert = gAttr.aktuellerWert + (sAttr.aktuellerWert if gfs.wesen else 0)
        maxWert = gAttr.maxWert + (sAttr.maxWert if gfs.wesen else 0)

        start.append("{} ({} | {})".format(gAttr.attribut.titel, aktuellerWert, maxWert))

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


@login_required
@verified_account
def spezial(request):
    return render(request, 'wiki/spezial.html', {'topic': 'Spezialfertigkeiten', "spezial": Spezialfertigkeit.objects.all().order_by("titel")})


@login_required
@verified_account
def wissen(request):
    return render(request, 'wiki/wissen.html', {'topic': 'Wissensfertigkeiten', 'wissen': Wissensfertigkeit.objects.all().order_by("titel")})


@login_required
@verified_account
def wesenkräfte(request):
    wesenkraft = []
    for w in Wesenkraft.objects.all().order_by("titel"):
        wesen = w.get_wesen_display()
        zusatz = []
        if w.wesen == "w":
            for z in w.zusatz_wesenspezifisch.all():
                zusatz.append(z.titel)
        elif w.wesen == "f":
            zusatz.append(w.zusatz_manifest)
            wesen = "Manifest kleiner gleich "

        wesenkraft.append({"kraft": w, "für": wesen, "zusatz": zusatz})
    return render(request, "wiki/wesenkraft.html", {"wesenkräfte": wesenkraft, "topic": "Wesenkräfte"})


@login_required
@verified_account
def religion(request):
    return render(request, "wiki/religion.html", {'topic': "Religionen", "religionen": Religion.objects.all().order_by("titel")})


@login_required
@verified_account
def beruf(request):
    return render(request, "wiki/beruf.html", {'topic': "Berufe", "berufe": Beruf.objects.all().order_by("titel")})


@login_required
@verified_account
def rang_ranking(request):
    return render(request, "wiki/rang_ranking.html", {"list": RangRankingEntry.objects.all().order_by("order"), "topic": "Erfahrungsranking"})


def compare_dates(a, b):
    if a["date"].month < b["date"].month: return -1
    if a["date"].month > b["date"].month: return 1

    if a["date"].day < b["date"].day: return -1
    if a["date"].day > b["date"].day: return 1

    if a["date"].year < b["date"].year: return -1
    if a["date"].year > b["date"].year: return 1
    return 0


def delta_without_year(date, today):
    return (datetime(today.year, date.month, date.day) - today).days + 1


@login_required
@verified_account
def geburtstage(request):
    today = datetime.today()
    name_dict = {}    # [username] = full name
    for u in User.objects.all():
       name_dict[u.username] = "{} {}".format(u.first_name, u.last_name)


    spieler_list = []
    next_birthday = {"delta": None, "date": None, "spieler": []}
    for s in Spieler.objects.all():
        if s.geburtstag:
            spieler_delta = delta_without_year(s.geburtstag, today)
            next_age = math.floor((today - datetime(s.geburtstag.year, s.geburtstag.month, s.geburtstag.day)).days / 365.2425)
            if spieler_delta != 0:
                next_age += 1

            spieler_list.append({"name": name_dict[s.name], "date": s.geburtstag, "next_age": next_age, "next_party": False})

            # birthday has already been this year
            if spieler_delta < 0:
                continue

            if next_birthday["delta"] is None:
                next_birthday["date"] = s.geburtstag
                next_birthday["delta"] = delta_without_year(s.geburtstag, today)
                next_birthday["spieler"].append(name_dict[s.name])
                continue

            if spieler_delta < next_birthday["delta"]:
                next_birthday["spieler"] = [name_dict[s.name]]
                next_birthday["date"] = s.geburtstag
                next_birthday["delta"] = spieler_delta
                continue

            # same date, append to list
            if spieler_delta == next_birthday["delta"]:
                next_birthday["spieler"].append(name_dict[s.name])

    for s in spieler_list:
        if s["name"] in next_birthday["spieler"]:
            s["next_party"] = True

    spieler_list = sorted(spieler_list, key=cmp_to_key(compare_dates))

    # everyone had already their birthday, set the first one(s) of the year
    if next_birthday["delta"] is None:
        first_years_birthday = None
        for s in spieler_list:
            if first_years_birthday is None:
                first_years_birthday = s["date"]
            if s["date"] == first_years_birthday:
                s["next_party"] = True
                s["next_age"] -= 1
            else: break

    context = {"list": spieler_list, "topic": "Geburtstage"}
    return render(request, "wiki/geburtstage.html", context)
