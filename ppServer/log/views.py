from ppServer.decorators import spielleiter_only
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from functools import cmp_to_key

from character.models import Attribut, Fertigkeit, Charakter, Spieler

from .models import Log, kind_enum


def logShop(spieler, char, items):
    """Gekaufte Items"""
    """items = [{"num": , "item_str": , (ggf. "stufe": ,) "preis_ges": , (ggf. "preisCP_ges": ,) "firma_titel": , "in_points": }]"""

    for i in items:

        if i["num"] <= 0:
            raise ValueError("Item {}: die gekaufte Anzahl ist negativ".format(i["item"].__str__()))

        if i["preis_ges"] < 0:
            raise ValueError("Item {}: der bezahlte Preis in Drachmen oder Quiz-Punkten ist negativ".format(i["item"].__str__()))

        notizen = "Von {} wurden {} Stück".format(i["item"].__str__(), i["num"])
        if i["item"].stufenabhängig:
            notizen += " der Stufe {}".format( i["stufe"])
        notizen += " von der Firma {} gekauft.".format(i["firma_titel"])

        kosten = "{} Drachmen".format(i["preis_ges"])

        Log.objects.create(art="s", spieler=spieler, char=char, notizen=notizen, kosten=kosten)


def logQuizPointsSP(spieler, char, quiz_points_alt, quiz_points_neu, neue_sp, notiz=None):
    """Vermehrung des Geldes"""
    if quiz_points_neu > quiz_points_alt:
        raise ValueError("Der Betrag der Punkte ist größer geworden")

    kosten = "{} Quiz-Punkte".format(quiz_points_alt - quiz_points_neu)

    notizen = "Der Charakter besitzt nun {} SP mehr, also {}.".format(neue_sp, neue_sp + char.sp)
    if notiz:
        notizen += "\n" + notiz

    Log.objects.create(art="d", spieler=spieler, char=char, notizen=notizen, kosten=kosten)

def logAlleMAverloren(spieler, char, rel_MA, spruchz_fp, kampfm_fp, antim_fp):
    """Die Magie ist (mal wieder) komplett weg"""

    notizen = "Der Charakter besitzt nun komplett keine Magie Mehr.\n"
    kosten = 0
    # attr (aktuell, max)
    if rel_MA.aktuellerWert > 0 or rel_MA.maxWert > 0:
        notizen += "Magie-Attribut: "

    if rel_MA.aktuellerWert > 0:
        notizen += "aktueller Wert -{}, ".format(rel_MA.aktuellerWert)
        kosten += (rel_MA.aktuellerWert * 3)

    if rel_MA.maxWert > 0:
        notizen += "Maximum -{},".format(rel_MA.maxWert)
        kosten += (rel_MA.maxWert * 5)

    notizen += "\n"

    # fg
    if rel_MA.fg > 0:
        notizen += "FG der Magie: -{},\n".format(rel_MA.fg)
        kosten += (rel_MA.fg * 2)

    # fp
    if spruchz_fp > 0:
        notizen += "Spruchzauberei-FP: -{},\n".format(spruchz_fp)
        kosten += spruchz_fp

    if kampfm_fp > 0:
        notizen += "Kampfmagie-FP: -{},\n".format(kampfm_fp)
        kosten += kampfm_fp

    if antim_fp > 0:
        notizen += "Antimagie-FP: -{}".format(antim_fp)
        kosten += antim_fp

    Log.objects.create(art="v", spieler=spieler, char=char, notizen=notizen, kosten="{} CP".format(kosten))


def sort_by_name(a, b):
    if a.name < b.name: return -1
    if a.name > b.name: return 1
    return 0


@login_required
@spielleiter_only
def userLog(request):

    if request.method == "GET":

        logs = [{"item": l, "kategorie": l.get_art_display()} for l in Log.objects.all().order_by("-timestamp", "spieler", "char", "art")]

        # get used filter categories
        char = []
        spieler = []
        for l in logs:
            char.append(l["item"].char)
            spieler.append(l["item"].spieler)

        # make those entries unique
        spieler = sorted(set(spieler), key=cmp_to_key(sort_by_name))
        char = sorted(set(char), key=cmp_to_key(sort_by_name))

        # collect and render
        context = {
            "filter": {"char": char, "spieler": spieler, "kategorie": kind_enum},
            "logs": logs
        }
        return render(request, "log/userLog.html", context)


    if request.method == "POST":
        json_dict = json.loads(request.body.decode("utf-8"))

        try:
            char_filter = json_dict["char"]
            spieler_filter = json_dict["spieler"]
            kategorie_filter = json_dict["kategorie"]

            page_number = json_dict['page_number']
        except:
            return JsonResponse({"message": "Not all filters were provided or pagenumber is missing"}, status=418)

        logs = Log.objects

        if len(char_filter): logs = logs.filter(char_id__in=char_filter)
        if len(spieler_filter): logs = logs.filter(spieler_id__in=spieler_filter)
        if len(kategorie_filter): logs = logs.filter(art__in=kategorie_filter)

        if not len(char_filter) + len(spieler_filter) + len(kategorie_filter): logs = logs.all()

        log_paginator = Paginator(logs, 20)
        page = log_paginator.get_page(page_number)
        paging = {
            #'count': page.count(),
            'end_index': page.end_index(),
            'has_next': page.has_next(),
            'has_other_pages': page.has_other_pages(),
            'has_previous': page.has_previous(),
            #'index': page.index(),
            'next_page_number': page.next_page_number() if page.has_next() else None,
            'number': page.number,
            #'paginator': page.paginator,
            'previous_page_number': page.previous_page_number() if page.has_previous() else None,
            'start_index': page.start_index(),
            'num_pages': page.paginator.num_pages
        }
        logs = [{"charname": l.char.name,
                 "spielername": l.spieler.name,
                 "kategorie": l.get_art_display(),
                 "notizen": l.notizen,
                 "kosten": l.kosten,
                 "timestamp": l.timestamp} for l in page.object_list]


        return JsonResponse({"logs": logs, "paging": paging})
