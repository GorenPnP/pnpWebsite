from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
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
def userLog(request):

    logs = []
    if User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
        context = {"spielleiter": True}
        for l in Log.objects.all().order_by("-timestamp", "spieler", "char", "art"):
            logs.append({"item": l, "kategorie": l.get_art_display()})
    else:
        context = {"spielleiter": False}
        chars = Charakter.objects.filter(eigentümer__name=request.user.username)
        for l in Log.objects.filter(char__in=chars).order_by("-timestamp", "char", "art"):
            logs.append({"item": l, "kategorie": l.get_art_display()})

    char = []
    spieler = []
    kategorie = []
    for l in logs:
        char.append(l["item"].char)
        spieler.append(l["item"].spieler)
    spieler = sorted(set(spieler), key=cmp_to_key(sort_by_name))
    char = sorted(set(char), key=cmp_to_key(sort_by_name))

    context["filter"] = {"char": char, "spieler": spieler, "kategorie": kind_enum}
    context["logs"] = logs
    context["user"] = request.user.username
    return render(request, "log/userLog.html", context)
