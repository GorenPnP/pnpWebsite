import json
from math import floor

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from ppServer.decorators import verified_account

from character.enums import würfelart_enum
from character.models import *
from shop.models import Zauber

from .models import *

WP_FACTOR = 4


def get_own_NewCharakter(request):

    try:
        spieler = get_object_or_404(Spieler, name=request.user.username)
    except:
        return None, ValueError("Spieler konnte nicht gefunden werden")

    chars = NewCharakter.objects.filter(eigentümer=spieler)
    if chars.count() > 1:
        return None, ValueError("Es existieren mehrere Charaktere zu diesem Spieler")

    elif chars.count() == 0:
        return None, None
    else:
        return chars.first(), None


def cp_erstellung_done(request):
    spieler = get_object_or_404(Spieler, name=request.user.username)
    return NewCharakter.objects.filter(eigentümer=spieler).exists() or not Charakter.objects.filter(eigentümer=spieler, in_erstellung=True).exists()


def new_gfs_done(new_char):
    return new_char is not None and new_char.gfs


def new_prio_done(new_char):
    return not ( new_char.ap is None or new_char.sp is None or new_char.ip is None or new_char.fp is None or new_char.fg is None\
            or new_char.zauber is None or new_char.geld is None)


def new_ap_done(new_char):
    return new_char.ap == 0


def new_fert_done(new_char):
    return new_char.fp == 0 and new_char.fg == 0


def new_zauber_done(new_char):
    return new_char.zauber == 0

def new_vor_nacht_done(new_char):
    return new_char.ip >= 0

def new_spF_and_wF_done(new_char):
    return new_char.spF_wF == 0

@login_required
@verified_account
@csrf_protect
def landing_page(request):

    if request.method == "GET":
        if not cp_erstellung_done(request):
            return redirect("create:cp")

        new_char, _ = get_own_NewCharakter(request)
        if not new_gfs_done(new_char):
            return redirect("create:gfs")

        if not new_prio_done(new_char):
            return redirect("create:prio")

        list = []
        list.append({"done": new_ap_done(new_char), "link": reverse("create:ap"), "text": "Verteile hier AP in Attribute", "werte": "<span id='ap'>{}</span> AP".format(new_char.ap), "id": "attr"})
        list.append({"done": new_fert_done(new_char), "link": reverse("create:fert"), "text": "Verteile hier FP und FG in Fertigkeiten",
                     "werte": "<span id='fp'>{}</span> FP, <span id='fg'>{}</span> FG".format(new_char.fp, new_char.fg), "id": "fert"})

        if not new_char.larp:
            list.append({"done": new_zauber_done(new_char), "link": reverse("create:zauber"), "text": "Suche dir hier Zauber aus", "werte": "noch {} zu vergeben".format(new_char.zauber)})
            list.append({"done": new_spF_and_wF_done(new_char), "link": reverse("create:spF_wF"), "text": "Wähle hier Spezial- und Wissensfertigkeiten aus", "werte": "noch {} zu vergeben".format(new_char.spF_wF)})
        list.append({"done": new_vor_nacht_done(new_char), "link": reverse("create:vor_nachteil"), "text": "Verwalte hier Vor- und Nachteile", "werte": "{} IP".format(new_char.ip)})

        infos = []
        infos.append("<strong>Deine Gfs/Klasse</strong> kannst du dir <a href='{}' target='_blank'>hier</a> nochmal angucken.".format(reverse("wiki:stufenplan", args=[new_char.gfs.id])))
        infos.append("Aussehen und v.A. rollenspielwichtige Aspekte wie Religion, Beruf werden später festgelegt.")
        infos.append("Im <strong>Shop</strong> kann später eingekauft werden, für Neugierige geht's zum Stöbern <a href='{}' target='_blank'>hier</a> entlang.".format(reverse("shop:index")))

        done_completely = new_ap_done(new_char) and\
                        new_fert_done(new_char) and\
                        new_zauber_done(new_char) and\
                        new_vor_nacht_done(new_char) and\
                        new_spF_and_wF_done(new_char) and\
                        (NewCharakterPersönlichkeit.objects.filter(char=new_char).count() or new_char.larp)

        pers = [rel.persönlichkeit.id for rel in NewCharakterPersönlichkeit.objects.filter(char=new_char)]
        context = {
            "larp": new_char.larp,
            "list": list,
            "infos": infos,
            "done": done_completely,
            "persönlichkeiten": Persönlichkeit.objects.all(),
            "persönlichkeit_row": {"link": reverse("wiki:persönlichkeiten"), "wert": pers}
            }
        return render(request, "create/landing_page.html", context=context)

    if request.method == "POST":

        new_char, error = get_own_NewCharakter(request)
        if new_char.larp: return JsonResponse({})

        if error:
            return JsonResponse({"message": "Konnte Charakter nicht finden"}, status=418)

        try:
            p_ids = [int(p_id) for p_id in json.loads(request.body.decode("utf-8"))['p_ids']]
        except:
            return JsonResponse({"message": "Keine Persönlichkeit angekommen"}, status=418)

        print(p_ids)
        persönlichkeiten = [get_object_or_404(Persönlichkeit, id=p_id) for p_id in p_ids]
        toggle_check = NewCharakterPersönlichkeit.objects.filter(char=new_char).count() == 0     # if persönlichkeit chosen, tick that box!


        # persönlichkeit hinzufügen
        NewCharakterPersönlichkeit.objects.filter(char=new_char).delete()
        for persönlichkeit in persönlichkeiten:
            NewCharakterPersönlichkeit.objects.create(char=new_char, persönlichkeit=persönlichkeit)

        # done
        return JsonResponse({"toggle_check": toggle_check})


def get_entries_of_prio():
    # Note: FP & FG together in one field!
    return [
        [row.get_priority_display(), row.ip, row.ap, row.sp, row.konzentration, row.fp, row.fg, row.zauber, row.drachmen, row.spF_wF]
        for row in Priotable.objects.all()
    ]


@login_required
@verified_account
def new_gfs_characterization(request):
    gfs_characterizations = []
    for gfs_characterization in GfsCharacterization.objects.all():
        serialized_dict = {}
        for field in GfsCharacterization._meta.fields:
            serialized_dict[field.attname] = getattr(gfs_characterization, field.attname)
        gfs_characterizations.append(serialized_dict)

    filters = []
    for field in GfsCharacterization._meta.fields:
        if field.attname in ["id", "gfs_id"]: continue

        filters.append({
            "text": field.help_text,
            "name": field.attname,
            "choices": [{"id": choice[0], "titel": choice[1]} for choice in field.choices]
        })

    context = {
        "filters": filters,
        "gfs": [{"id": gfs.id, "titel": gfs.titel, "beschreibung": gfs.beschreibung} for gfs in Gfs.objects.all()],
        "gfs_characterizations": gfs_characterizations
    }
    return render(request, "create/gfs_characterization.html", context)


@login_required
@verified_account
@csrf_protect
def new_gfs(request):
    if request.method == "GET":

        gfs = []
        for c in NewCharakter.objects.filter(eigentümer__name=request.user.username):
            gfs.append(c.gfs.titel)

        for c in Charakter.objects.filter(eigentümer__name=request.user.username, in_erstellung=True):
            gfs.append(c.gfs.titel)

        context = {"gfs": Gfs.objects.all(),
                   "old_scetches": gfs}

        return render(request, "create/gfs.html", context)

    if request.method == "POST":
        try:
            gfs_id = json.loads(request.body.decode("utf-8"))["gfs_id"]
            larp = json.loads(request.body.decode("utf-8"))["larp"]
        except:
            return JsonResponse({"message": "Keine Gfs angekommen"}, status=418)

        # alle Charaktere in_erstellung löschen
        for c in Charakter.objects.filter(eigentümer__name=request.user.username, in_erstellung=True):
            c.delete()

        # jeder nur ein NewCharakter zurzeit
        for c in NewCharakter.objects.filter(eigentümer__name=request.user.username):
            c.delete()

        spieler = get_object_or_404(Spieler, name=request.user.username)
        gfs = get_object_or_404(Gfs, id=gfs_id)
        new_char = NewCharakter.objects.create(eigentümer=spieler, gfs=gfs, larp=larp)

        # set default vals
        if larp:
            new_char.ap = 100
            new_char.fp = 20
            new_char.fg = 2
            new_char.geld = 5000
            new_char.sp = 0
            new_char.ip = 0
            new_char.zauber = 0
            new_char.save()


        return JsonResponse({"url": reverse("create:prio")})


@login_required
@verified_account
@csrf_protect
def new_priotable(request):
    entries = get_entries_of_prio()

    if request.method == 'POST':

        # collect data
        num_entries = len(entries)
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if new_char is None:
            return JsonResponse({"url": reverse("create:gfs")}, status=300)

        fields = {}
        try:
            for k, v in json.loads(request.body.decode("utf-8")).items(): fields[k] = int(v)
        except error:
            return JsonResponse({'message': 'Falsche Auswahl (Format)'}, status=418)

        if len(fields.values()) != num_entries:
            return JsonResponse({"message": "Falsche Auswahl (Anzahl Felder)"}, status=418)

        for val in fields.values():
            if val < 0 or val >= num_entries:
                return JsonResponse({"message": "Falsche Auswahl (Inhalt Felder)"}, status=418)

        print(fields)

        # start logic
        ap = new_char.gfs.ap * -1
        for category in fields.keys():
            row = fields[category]
            col = int(category) + 1

            # row: [priority, IP, AP, (SP, konzentration), (FP, FG), Zauber, Drachmen]
            if col == 1:
                new_char.ip = entries[row][col]
            elif col == 2:
                ap = entries[row][col]

            elif col == 3:
                new_char.sp = entries[row][col]
                new_char.konzentration = entries[row][col + 1]
            elif col == 4:
                new_char.fp = entries[row][col + 1]
                new_char.fg = entries[row][col + 2]
            elif col == 5:
                new_char.zauber = entries[row][col + 2]
            else:
                new_char.geld = entries[row][col + 2]
                new_char.spF_wF = entries[row][col + 3]

        ap -= new_char.gfs.ap
        if ap < 0:
            return JsonResponse({"message": "Zu wenig AP für Gfs"}, status=418)

        new_char.ap = ap
        new_char.save()

        return JsonResponse({"url": reverse("create:landing_page")})


    if request.method == "GET":
        if not cp_erstellung_done(request):
            return redirect("create:cp")

        new_char, error = get_own_NewCharakter(request)
        if not new_gfs_done(new_char):
            return redirect("create:gfs")

        if new_prio_done(new_char):
            return redirect("create:landing_page")

        # get ap cost for gfs
        ap_cost = new_char.gfs.ap

        # get MA maximum
        max_MA = max_MA = GfsAttribut.objects.get(gfs=new_char.gfs, attribut__titel="MA").maxWert

        if (max_MA == 0):      # mundan => keine Zauber wählbar (nur 0 Zauber in prio F)
            for k in range(len(entries)):
                entries[k][6] = 0 if k + 1 == len(entries) else None

        notes = [
            "IP = für Vor- und Nachteile",
            "AP = Aufwerten eines Attributs",
            "SP = für alles Mögliche, vor Allem um nicht zu sterben",
            "Konz. = Konzentration, um Proben besser zu würfeln als sonst",
            "FP = Fertigkeitspunkte",
            "FG = Fertigkeitsgruppen",
            ]

        context = {"topic": "Prioritätentabelle", 'table': entries, 'notizen': notes, "id": new_char.id, "ap_cost": ap_cost, "gfs": new_char.gfs}
        return render(request, "create/prio.html", context)


# reachable only via links all over
@login_required
@verified_account
@csrf_protect
def new_vor_nachteil(request, char_id=None):

    meta_dict = {"vorteil_multiple": ["Magisches Band", "Meister", "Schutzgeist", "Spezialisiert", "Talentiert"],
                 "nachteil_multiple": ["Allergie", "Angst", "Besessen", "Codex", "Defizit", "Drogenabhängig", "Fanatisch", "Feind",
                                     "Galaktisches Ziel", "Gespaltene Persönlichkeit", "Rassistisch", "Schwere Allergie", "Unkontrolliert",
                                     "Verbittert", "Verliebt", "Voreingenommen"],
                 }

    if request.method == "GET":

        # get rel_vort & rel_nacht
        rel_vort = NewCharakterVorteil
        rel_nacht = NewCharakterNachteil

        new_char, error = get_own_NewCharakter(request)
        if not new_char:
            return redirect("character:index")

        vorteil_list = []
        for v in Vorteil.objects.all():
            rel = rel_vort.objects.filter(char=new_char, teil=v)
            teil = {"item": v, "notizen": rel[0].notizen if rel else "",
                    "anzahl": rel[0].anzahl if rel else 0}
            vorteil_list.append(teil)

        nachteil_list = []
        for v in Nachteil.objects.all():

            rel = rel_nacht.objects.filter(char=new_char, teil=v)
            dict = {"item": v, "notizen": rel[0].notizen if rel else "",
                    "anzahl": rel[0].anzahl if rel else 0}
            nachteil_list.append(dict)

        context = {"vorteil_list": vorteil_list, "nachteil_list": nachteil_list,
                   "meta": meta_dict, "ip": new_char.ip
                   }

        return render(request, "create/vor_nachteil.html", context)

    if request.method == "POST":

        # get new_char
        new_char, error = get_own_NewCharakter(request)
        if not new_char:
            return redirect("character:index")

        try:
            vorteile = json.loads(request.body.decode("utf-8"))["vorteile"]
            nachteile = json.loads(request.body.decode("utf-8"))["nachteile"]
        except:
            return JsonResponse({"message": "Vor- und/oder Nachteile nicht angekommen"}, status=418)

        # get ip of already purchased teils
        sum = new_char.ip
        for relVort in NewCharakterVorteil.objects.filter(char=new_char):
            sum += (relVort.anzahl * relVort.teil.ip)
        for relNacht in NewCharakterNachteil.objects.filter(char=new_char):
            sum -= (relNacht.anzahl * relNacht.teil.ip)

        # delete existing
        NewCharakterVorteil.objects.filter(char=new_char).delete()
        NewCharakterNachteil.objects.filter(char=new_char).delete()

        # collect and create new vorteile
        ip_diff = 0
        id_vort = [int(i) for i in vorteile.keys()]
        for teil in Vorteil.objects.filter(id__in=id_vort):
            entry = vorteile[str(teil.id)]
            ip_diff -= (teil.ip * entry["anz"])

            NewCharakterVorteil.objects.get_or_create(char=new_char, teil=teil,
                anzahl=entry["anz"], notizen=entry["notizen"])

        # ... new nachteile
        id_nacht = [int(i) for i in nachteile.keys()]
        for teil in Nachteil.objects.filter(id__in=id_nacht):
            entry = nachteile[str(teil.id)]
            ip_diff += (teil.ip * entry["anz"])

            NewCharakterNachteil.objects.get_or_create(char=new_char, teil=teil,
                anzahl=entry["anz"], notizen=entry["notizen"])

        # set ip-pool
        new_char.ip = sum + ip_diff
        new_char.save()

        # response
        return JsonResponse({"url": reverse("create:landing_page")})


@login_required
@verified_account
@csrf_protect
def new_ap(request):
    if request.method == "POST":
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        try:
            attr_dict = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({"message": "Attribute sind nicht angekommen"}, status=418)

        # get difference between existing vals and selected ones
        ap_diff = 0
        relAttrs = NewCharakterAttribut.objects.filter(char=new_char)
        for relAttr in relAttrs:
            curr = attr_dict[str(relAttr.pk)]
            ap_diff += curr["aktuell_ap"] - relAttr.aktuellerWert_ap
            ap_diff += 2 * (curr["max_ap"] - relAttr.maxWert_ap)

            if relAttr.ges_aktuell() > relAttr.ges_max_bonus():
                return JsonResponse({"message": "Wert von {} ist über dem Maximum".format(relAttr.attribut.titel)})

        # check if their difference === AP
        if ap_diff != new_char.ap:
            return JsonResponse({"message": "Nicht die passende Anz AP ausgegeben: soll {}, ist {}".format(new_char.ap, ap_diff)}, status=418)

        # all save since here
        # set aktuell_ap and max_ap to attributes
        for relAttr in relAttrs:
            curr = attr_dict[str(relAttr.pk)]
            relAttr.aktuellerWert_ap = curr["aktuell_ap"]
            relAttr.maxWert_ap = curr["max_ap"]
            relAttr.save()

        new_char.ap = 0
        new_char.save()

        # redirect
        return JsonResponse({"url": reverse("create:landing_page")})

    if request.method == "GET":
        if not cp_erstellung_done(request):
            return redirect("create:cp")

        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if not new_gfs_done(new_char):
            return redirect("create:gfs")

        if not new_prio_done(new_char):
            return redirect("create:prio")


        if new_char.larp:
            headings = [
                TableHeading("Attribut", "attr", TableFieldType.TEXT).serialize(),
                TableHeading("Aktuell", "aktuell_ap", TableFieldType.NUMBER_INPUT).serialize(),
                TableHeading("Maximum", "maximum_ap", TableFieldType.NUMBER_INPUT).serialize(),
                TableHeading("Stand", "result", TableFieldType.TEXT).serialize(),
            ]
        else:
            headings = [
                TableHeading("Attribut", "attr", TableFieldType.TEXT).serialize(),
                TableHeading("Aktuell", "aktuell", TableFieldType.TEXT).serialize(),
                TableHeading("+", "aktuell_ap", TableFieldType.NUMBER_INPUT).serialize(),
                TableHeading("Maximum", "maximum", TableFieldType.TEXT).serialize(),
                TableHeading("+", "maximum_ap", TableFieldType.NUMBER_INPUT).serialize(),
                TableHeading("Stand", "result", TableFieldType.TEXT).serialize(),
            ]
        rows = []
        attributes = []
        for new_a in NewCharakterAttribut.objects.filter(char=new_char):
            aktuell_bonus = "+{}".format(new_a.aktuellerWert_bonus) if new_a.aktuellerWert_bonus else ""
            max_bonus = "+{}".format(new_a.maxWert_bonus) if new_a.maxWert_bonus else ""
            row = {
                "pk": new_a.pk,
                "attr": "{} ({})".format(new_a.attribut.titel, new_a.attribut.beschreibung),
                "aktuell": "{}{}".format(new_a.aktuellerWert, aktuell_bonus),
                "aktuell_ap": new_a.aktuellerWert_ap,
                "maximum": "{}{}".format(new_a.maxWert, max_bonus),
                "maximum_ap": new_a.maxWert_ap,
                "result": ""

            }
            rows.append(row)

            attribute = {
                "pk": new_a.pk,
                "aktuell": new_a.aktuellerWert + new_a.aktuellerWert_bonus,
                "aktuell_ap": new_a.aktuellerWert_ap,
                "max": new_a.maxWert + new_a.maxWert_bonus,
                "max_ap": new_a.maxWert_ap
            }
            attributes.append(attribute)

        context = {"headings": headings, "rows": rows, "attributes": attributes, "ap_pool": new_char.ap, "id": new_char.id}
        return render(request, "create/ap.html", context)


@login_required
@verified_account
@csrf_protect
def new_fert(request):
    if request.method == "POST":

        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        try:
            fp_dict = json.loads(request.body.decode("utf-8"))["fp_dict"]
            fg_dict = json.loads(request.body.decode("utf-8"))["fg_dict"]
        except:
            return JsonResponse({"message": "Fertigkeiten sind nicht angekommen"}, status=418)

        # get difference between existing vals and selected ones
        # fg
        fg_diff = 0
        relAttrs = NewCharakterAttribut.objects.filter(char=new_char)
        for relAttr in relAttrs:
            fg = fg_dict[str(relAttr.attribut.id)]
            fg_diff += fg - relAttr.fg

            if fg > relAttr.limit_fg():
                return JsonResponse({"message": "FG sind höher als Attribut oder Limit in {}.".format(relAttr.attribut.titel)}, status=418)

        if fg_diff != new_char.fg:
            return JsonResponse({"message": "FG falsch verteilt. Sind {}, sollen {} sein.".format(fg_diff, char.fg)}, status=418)

        # fp
        fp_diff = 0
        relFerts = NewCharakterFertigkeit.objects.filter(char=new_char)
        for relFert in relFerts:
            fp_diff += fp_dict[str(relFert.fertigkeit.id)] - relFert.fp

            attr1 = relAttrs.get(attribut=relFert.fertigkeit.attr1).ges_aktuell_bonus()
            attr2 =  relAttrs.get(attribut=relFert.fertigkeit.attr2).ges_aktuell_bonus() if relFert.fertigkeit.attr2 else attr1
            limit = min(floor((attr1 + attr2) / 2 + .5), 12)

            if fp_dict[str(relFert.fertigkeit.id)] > limit:
                return JsonResponse({"message": "FP sind höher als Limit in {}.".format(relFert.fertigkeit.titel)}, status=418)

        if fp_diff != new_char.fp:
            return JsonResponse({"message": "FP falsch verteilt. Sind {}, sollen {} sein.".format(fp_diff, char.fp)}, status=418)

        # check done
        # all save since here

        # set values in models
        for relAttr in relAttrs:
            relAttr.fg = fg_dict[str(relAttr.attribut.id)]
            relAttr.save()

        for relFert in relFerts:
            relFert.fp = fp_dict[str(relFert.fertigkeit.id)]
            relFert.save()

        new_char.fp = 0
        new_char.fg = 0
        new_char.save()

        # redirect
        return JsonResponse({"url": reverse("create:landing_page")})

    if request.method == "GET":
        if not cp_erstellung_done(request):
            return redirect("create:cp")

        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if not new_gfs_done(new_char):
            return redirect("create:gfs")

        if not new_prio_done(new_char):
            return redirect("create:prio")

        dict_1 = {}
        list_1 = []
        list_else = []
        for new_f in NewCharakterFertigkeit.objects.filter(char=new_char):

            # ignore those without an attr
            if new_f.fertigkeit.attr1 is None and new_f.fertigkeit.attr2 is None: continue

            # shuffle attr to correct positions, meaning: (none, MA) => (MA, none)
            if new_f.fertigkeit.attr1 is None and new_f.fertigkeit.attr2:
                new_f.fertigkeit.attr1 = new_f.fertigkeit.attr2
                new_f.fertigkeit.attr2 = None
                new_f.fertigkeit.save()

            # fertigkeiten with 2 attrs
            rel_attr1 = get_object_or_404(NewCharakterAttribut, attribut=new_f.fertigkeit.attr1, char=new_char)
            if new_f.fertigkeit.attr2:
                rel_attr2 = get_object_or_404(NewCharakterAttribut, attribut=new_f.fertigkeit.attr2, char=new_char)
                attr1 = rel_attr1.ges_aktuell_bonus()
                attr2 = rel_attr2.ges_aktuell_bonus()
                limit = min( int(floor((attr1 + attr2) / 2 + 0.5)), 12 )

                list_else.append({"rel": new_f, "attr1_aktuell": attr1, "attr2_aktuell": attr2, "limit_fp": limit})

            # fertigkeiten with 1 attr
            else:
                fg = new_f.ges_fg()

                attr_id = new_f.fertigkeit.attr1.id
                fert_1 = {"rel": new_f, "show_fg": 0, "fg": fg, "fg_bonus": rel_attr1.fg_bonus, "last_in_group": 0, "first_in_group": 0,
                            "attr1_aktuell": rel_attr1.ges_aktuell_bonus(), "limit_fp": min(rel_attr1.ges_aktuell_bonus(), 12),
                            "limit_fg": rel_attr1.ges_aktuell_bonus()}

                if attr_id in dict_1.keys():
                    dict_1[attr_id].append(fert_1)
                else:
                    dict_1[attr_id] = [fert_1]

        # collect fert_1
        keys = [i for i in dict_1.keys()]
        keys.sort()
        for attr in keys:
            dict_1[attr][0]["first_in_group"] = 1
            dict_1[attr][len(dict_1[attr]) - 1]["last_in_group"] = 1
            dict_1[attr][1 if len(dict_1[attr]) > 1 else 0]["show_fg"] = 1

            list_1 += dict_1[attr]

        attr_list = []
        for new_a in NewCharakterAttribut.objects.filter(char=new_char):
            aktuellerWert = new_a.aktuellerWert_ap + new_a.aktuellerWert
            attr_list.append({"titel": new_a.attribut.titel, "val": aktuellerWert})

        context = {"attr_list": attr_list, "list_1": list_1, "list_else": list_else, "fp_pool": new_char.fp,
                   "fg_pool": new_char.fg, "id": new_char.id}
        return render(request, "create/fert.html", context)


@login_required
@verified_account
@csrf_protect
def new_zauber(request):
    if request.method == "GET":
        if not cp_erstellung_done(request):
            return redirect("create:cp")

        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if not new_gfs_done(new_char):
            return redirect("create:gfs")

        if not new_prio_done(new_char):
            return redirect("create:prio")

        zauber_list = [{"item": z, "select": NewCharakterZauber.objects.filter(char=new_char, item=z).count()} for z in Zauber.objects.filter(frei_editierbar=False).order_by("ab_stufe")]

        context = {"zauber_list": zauber_list, "zauber": new_char.zauber}
        return render(request, "create/zauber.html", context)

    if request.method == "POST":
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        try:
            id_list = json.loads(request.body.decode("utf-8"))["id_list"]
        except:
            return JsonResponse({"message": "Zauber nicht angekommen"}, status=418)

        must_val = new_char.zauber + \
            NewCharakterZauber.objects.filter(char=new_char).count()
        if len(id_list) != must_val:
            return JsonResponse({'message': 'Falsche Anzahl Zauber. Soll {}, ist {}'.format(must_val, is_val)}, status=418)

        # valid since here
        NewCharakterZauber.objects.filter(char=new_char).delete()

        chosen_n = [z for z in Zauber.objects.filter(id__in=id_list)]

        for z in chosen_n:
            NewCharakterZauber.objects.get_or_create(char=new_char, item=z)

        new_char.zauber = 0
        new_char.save()
        return JsonResponse({"url": reverse("create:landing_page")})


@login_required
@verified_account
def new_spF_wF(request):
    new_char, error = get_own_NewCharakter(request)
    if error:
        return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

    if not new_gfs_done(new_char):
        return redirect("create:gfs")

    if not new_prio_done(new_char):
        return redirect("create:prio")


    if request.method == "GET":

        ferts = []
        for spF in Spezialfertigkeit.objects.all():
            relFert = NewCharakterSpezialfertigkeit.objects.filter(char=new_char, spezialfertigkeit=spF).first()
            sp = {
                "kind": "Spezial",
                "pk": "spF{}".format(spF.pk),
                "titel": spF.titel,
                "beschreibung": spF.beschreibung,
                "attrs": "{}, {}".format(spF.attr1.titel, spF.attr2.titel),
                "ferts": ", ".join([fert.titel for fert in spF.ausgleich.all()]),
                "punkte": relFert.stufe if relFert else None
            }
            ferts.append(sp)

        for wF in Wissensfertigkeit.objects.all():
            relFert = NewCharakterWissensfertigkeit.objects.filter(char=new_char, wissensfertigkeit=wF).first()
            w = {
                "kind": "Wissen",
                "pk": "wF{}".format(wF.pk),
                "titel": wF.titel,
                "beschreibung": wF.beschreibung,
                "attrs": "{}, {}, {}".format(wF.attr1.titel, wF.attr2.titel, wF.attr3.titel),
                "ferts": ", ".join([fert.titel for fert in wF.fertigkeit.all()]),
                "punkte": relFert.stufe if relFert else None
            }
            ferts.append(w)

        context = { 
            "topic": "Spezial- & Wissensf.",
            "fertigkeiten": ferts,
            "wp": new_char.spF_wF * WP_FACTOR,
            "spF_wF": new_char.spF_wF,
            "headings": [
                TableHeading("Fertigkeit", "titel", TableFieldType.TEXT).serialize(),
                TableHeading("Art", "kind", TableFieldType.TEXT).serialize(),
                TableHeading("Attribute", "attrs", TableFieldType.TEXT).serialize(),
                TableHeading("Fertigkeit/en", "ferts", TableFieldType.TEXT).serialize(),
                TableHeading("WP", "punkte", TableFieldType.NUMBER_INPUT).serialize(),
            ]
        }
        return render(request, "create/spF_wF.html", context)

    if request.method == "POST":
        try:
            selected = json.loads(request.body.decode("utf-8"))["selected"]
        except:
            return JsonResponse({"message": "Ausgewählte Fertigkeiten sind nicht angekommen"}, status=418)

        # test


        # get pool
        current_spF = NewCharakterSpezialfertigkeit.objects.filter(char=new_char)
        current_wF = NewCharakterWissensfertigkeit.objects.filter(char=new_char)

        spF_wF = new_char.spF_wF + current_spF.count() + current_wF.count()
        wp = new_char.spF_wF * WP_FACTOR + sum([spF.stufe for spF in current_spF]) + sum([wF.stufe for wF in current_wF])
        if len(selected) != spF_wF:
            return JsonResponse({"message": "Anzahl der ausgewählten Fertigkeiten passt nicht"}, status=418)

        if sum([fert["wp"] for fert in selected]) != wp:
            return JsonResponse({"message": "WP in den Fertigkeiten passen nicht"}, status=418)


        # apply
        new_char.spF_wF = 0
        new_char.save()

        NewCharakterSpezialfertigkeit.objects.filter(char=new_char).delete()
        NewCharakterWissensfertigkeit.objects.filter(char=new_char).delete()

        for fert in selected:
            if fert["kind_of_fert"] == "spF":
                base = get_object_or_404(Spezialfertigkeit, pk=fert["pk"])
                NewCharakterSpezialfertigkeit.objects.create(char=new_char, spezialfertigkeit=base, stufe=fert["wp"])
            else:
                base = get_object_or_404(Wissensfertigkeit, pk=fert["pk"])
                NewCharakterWissensfertigkeit.objects.create(char=new_char, wissensfertigkeit=base, stufe=fert["wp"])

        # redirect
        return JsonResponse({"url": reverse("create:landing_page")})

@login_required
@verified_account
@csrf_protect
def new_cp(request):
    if request.method == "GET":
        new_char, error = get_own_NewCharakter(request)
        if error:
            return JsonResponse({"message": "Charakter konnte nicht gefunden werden"}, status=418)

        if new_char:
            if not new_gfs_done(new_char):
                return redirect("create:gfs")

            if not new_prio_done(new_char):
                return redirect("create:prio")

            if not new_ap_done(new_char):
                return redirect("create:ap")

            if not new_fert_done(new_char):
                return redirect("create:fert")

            if not new_zauber_done(new_char):
                return redirect("create:zauber")

            if not new_vor_nacht_done(new_char):
                return redirect("create:vor_nachteil")


            # transition from NewCharakter to Charakter
            c = Charakter.objects.create(sp=new_char.sp, konzentration=new_char.konzentration, geld=new_char.geld,
                                        eigentümer=new_char.eigentümer, manifest=new_char.gfs.startmanifest, gfs=new_char.gfs,
                                        larp=new_char.larp, wesenschaden_andere_gestalt=new_char.gfs.wesenschaden_andere_gestalt,
                                        wesenschaden_waff_kampf=new_char.gfs.wesenschaden_waff_kampf,
                                        ep_system=new_char.ep_system, ip=new_char.ip, profession=new_char.profession,
                                        HPplus=new_char.HPplus, HPplus_fix=new_char.HPplus_fix)

            # there is a signal that adds attr & fert to a character on every save. delete these again
            RelAttribut.objects.filter(char=c).delete()

            for rel in NewCharakterAttribut.objects.filter(char=new_char):
                RelAttribut.objects.create(char=c, attribut=rel.attribut, aktuellerWert=rel.ges_aktuell(),
                                           aktuellerWert_bonus=rel.aktuellerWert_bonus, maxWert_bonus=rel.maxWert_bonus,
                                           maxWert=rel.ges_max(), fg=rel.ges_fg())

            # there is a signal that adds attr & fert to a character on every save. delete these again
            RelFertigkeit.objects.filter(char=c).delete()

            for rel in NewCharakterFertigkeit.objects.filter(char=new_char):
                RelFertigkeit.objects.create(
                    char=c, fertigkeit=rel.fertigkeit, fp=rel.fp, fp_bonus=rel.fp_bonus)

            
            for rel in NewCharakterPersönlichkeit.objects.filter(char=new_char):
                RelPersönlichkeit.objects.create(char=c, persönlichkeit=rel.persönlichkeit)

            for rel in NewCharakterVorteil.objects.filter(char=new_char):
                RelVorteil.objects.create(char=c, teil=rel.teil, notizen=rel.notizen, anzahl=rel.anzahl)

            for rel in NewCharakterNachteil.objects.filter(char=new_char):
                RelNachteil.objects.create(char=c, teil=rel.teil, notizen=rel.notizen, anzahl=rel.anzahl)

            for rel in NewCharakterTalent.objects.filter(char=new_char):
                RelTalent.objects.create(char=c, talent=rel.talent)

            for rel in NewCharakterSpezialfertigkeit.objects.filter(char=new_char):
                RelSpezialfertigkeit.objects.create(char=c, spezialfertigkeit=rel.spezialfertigkeit, stufe=rel.stufe)

            for rel in NewCharakterWissensfertigkeit.objects.filter(char=new_char):
                RelWissensfertigkeit.objects.create(char=c, wissensfertigkeit=rel.wissensfertigkeit, würfel2=würfelart_enum[rel.stufe][0])

            for rel in GfsWesenkraft.objects.filter(gfs=new_char.gfs):
                RelWesenkraft.objects.create(char=c, wesenkraft=rel.wesenkraft)

            for rel in NewCharakterZauber.objects.filter(char=new_char):
                RelZauber.objects.create(char=c, item=rel.item, anz=1)

            new_char.delete()

            if c.larp:
                c.beruf = get_object_or_404(Beruf, titel="Schüler")
                c.save()

        # new_char already deleted
        else:
            spieler = get_object_or_404(Spieler, name=request.user.username)
            c = Charakter.objects.get(eigentümer=spieler, in_erstellung=True)

            if c is None:
                return redirect("create:gfs")

        context = {"c": c}
        context["berufe"] = Beruf.objects.all()
        context["religionen"] = Religion.objects.all()
        context["chosen_beruf_id"] = c.beruf.id if c.beruf else None
        context["chosen_religion_id"] = c.religion.id if c.religion else None
        return render(request, "create/cp.html", context)

    if request.method == "POST":

        character = get_object_or_404(Charakter, id=request.POST.get("char_id"))

        if request.user.username != character.eigentümer.name:
            return JsonResponse({"message": "Keine Erlaubnis die Charaktererstellung eines fremden Charakters zu beenden"}, status=418)

        try:
            name = request.POST.get("name")
        except:
            return JsonResponse({"message": "Name nicht angekommen"}, status=418)

        if not name:
            return JsonResponse({"message": "Da fehlt noch ein Name"}, status=418)

        character.name = name

        try:
            if not character.larp: character.beruf = Beruf.objects.get(id=request.POST.get("beruf"))
            character.religion = Religion.objects.get(id=request.POST.get("religion"))
            character.useEco = request.POST.get("eco_morph") == "eco"
            character.in_erstellung = False
        except:
            return JsonResponse({"message": "Daten nicht angekommen"}, status=418)

        character.save()

        return redirect("character:index")
