from ppServer.decorators import verified_account
import json
from math import floor

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import *


from django.http import HttpResponse

@login_required
@verified_account
def index(request):

    is_spielleiter = User.objects.filter(username=request.user.username, groups__name='spielleiter').exists()
    char_qs = Charakter.objects.prefetch_related("eigentümer").filter(in_erstellung=False).order_by('name')

    if not is_spielleiter:
        char_qs = char_qs.filter(eigentümer__name=request.user.username)

    context = {
        'charaktere': char_qs,
        'is_spielleiter': is_spielleiter,
        'topic': "Charaktere",
        "plus": "+ Charakter",
        "plus_url": reverse('create:gfs')
    }
    return render(request, "character/index.html", context)


@login_required
@verified_account
def show(request, pk):

    # sections of navbar and for reference in POST
    sections = [
        {"name": "Persönliches", "template": "character/show_persönlich.html"},
        {"name": "Attribute", "template": "character/show_attr.html"},
        {"name": "Fertigkeiten", "template": "character/show_fert.html"},
        {"name": "Proben", "template": "character/show_proben.html"},
        {"name": "Spezialf.", "template": "character/show_spezial.html"},
        {"name": "Wissensf.", "template": "character/show_wissen.html"},
        {"name": "Vorteile", "template": "character/show_teil.html"},
        {"name": "Nachteile", "template": "character/show_teil.html"},
        {"name": "Talente", "template": "character/show_talent.html"},
        {"name": "Wesenkr.", "template": "character/show_wesenkr.html"},
        {"name": "Affektivität", "template": "character/show_affekt.html"},
        {"name": "Inventar", "template": "character/show_items.html"},
    ]

    # the char, needed by anyone
    char = get_object_or_404(Charakter, id=pk)
    username = request.user.username

    if not User.objects.filter(username=username, groups__name='spielleiter').exists() and (char.eigentümer is None or username != char.eigentümer.name):
        return redirect('character:index')


    if request.method == "GET":

        wesen = ""
        if not char.gfs:
            wesen = ", ".join([i.spezies.titel for i in RelSpezies.objects.filter(char=char)])

        # get sums for hp
        base_hp = get_object_or_404(RelAttribut, char=char, attribut__titel="ST").aktuell()

        # sum up
        context = {
            "topic": char.name,
            "sections": sections,
            'char': char,
            'wesen': wesen,
            "totAb": base_hp * -1,
            "maxHp": base_hp * 5 + floor(char.rang /10 + .5) + char.HPplus,
            "wkHp": get_object_or_404(RelAttribut, char=char, attribut__titel="WK").aktuell() * 5,
            "konzentration": char.get_konzentration(),
            "persönlichkeiten": ", ".join([rel.persönlichkeit.titel for rel in RelPersönlichkeit.objects.filter(char=char)]),
            "app_index": "Charaktere",
            "app_index_url": reverse("character:index"),
        }

        return render(request, "character/show.html", context)

    if request.method == "POST":
        section = json.loads(request.body.decode("utf-8"))["section"]

        context = {"char": char}

        # get corresponding template
        template = ""
        for s in sections:
            if s["name"] == section:
                template = s["template"]
                break

        # attribute ids, körperlich / geistig / rest
        # for attrs, ferts (with 1 attr)
        context["k"] = [1, 3, 4, 5]
        context["g"] = [2, 6, 7]
        context["m"] = [7, 8]


        # persönliches
        if section == sections[0]["name"]:
            wesen = ""
            if not char.gfs:
                wesen = ", ".join([i.spezies.titel for i in RelSpezies.objects.filter(char=char)])

            context["wesen"] =  wesen

            # get sums for hp
            base_hp = get_object_or_404(RelAttribut, char=char, attribut__titel="ST").aktuell()
            context["totAb"] = base_hp * -1
            context["maxHp"] = base_hp * 5 + floor(char.rang /10 + .5) + char.HPplus
            context["wkHp"] = get_object_or_404(RelAttribut, char=char, attribut__titel="WK").aktuell() * 5
            context["konzentration"] = char.get_konzentration()


        # attribute
        elif section == sections[1]["name"]:
            context["relAttrs"] = RelAttribut.objects.filter(char=char)


        # fertigkeiten
        elif section == sections[2]["name"]:

            # get ferts with two attrs
            fert_else = RelFertigkeit.objects.filter(char=char).exclude(fertigkeit__attr2=None)

            # get ferts with one attr
            attrs = []
            attr_aktWert = {}
            for relAttr in RelAttribut.objects.filter(char=char):
                attrs.append({
                    "attr_id": relAttr.attribut.id,
                    "fg": relAttr.fg,
                    "fg_bonus": relAttr.fg_bonus,
                    "ferts": RelFertigkeit.objects.filter(char=char, fertigkeit__attr2=None, fertigkeit__attr1=relAttr.attribut)
                })

                # to calc limits
                attr_aktWert[relAttr.attribut.id] = relAttr.aktuell()

            context["fert2"] = fert_else
            context["attr"] = attrs
            context["limits"] = {
                "k": round(sum([attr_aktWert[attr_id] for attr_id in context["k"]]) / 2, 1),
                "g": round(sum([attr_aktWert[attr_id] for attr_id in context["g"]]) / 2, 1),
                "m": round(sum([attr_aktWert[attr_id] for attr_id in context["m"]]) / 2, 1)
            }


        # proben
        elif section == sections[3]["name"]:
            # need some ferts
            ferts = {}
            needed_ferts = ["Laufen", "Heben", "Entschlossenheit", "Schwimmen", "Resistenz", "Konstitution"]
            for rel in RelFertigkeit.objects.filter(char=char, fertigkeit__titel__in=needed_ferts):
                ferts[rel.fertigkeit.titel] = rel.pool()

            # need attrs
            attrs = {}
            for rel in RelAttribut.objects.filter(char=char): attrs[rel.attribut.titel] = rel


            # collect proben
            context["proben"] = [
                    {"titel": "Schadenswiderstand", "val": attrs["ST"].aktuell() + attrs["VER"].aktuell()},
                    {"titel": "Astralwiderstand", "val": attrs["MA"].aktuell() + attrs["WK"].aktuell()},
                    {"titel": "Initiative", "val": "{} + {} W4".format(
                        attrs["WK"].aktuell() + attrs["ST"].aktuell(), attrs["SCH"].aktuell())
                     },
                    {"titel": "Initiative Astral", "val": "{} + {} W4".format(
                        attrs["SCH"].aktuell() + attrs["WK"].aktuell(), floor(attrs["MA"].aktuell() / 2 + .5))
                    },
                    {"titel": "Gehrate", "val": attrs["SCH"].aktuell() * 2},
                    {"titel": "Laufrate", "val": attrs["SCH"].aktuell() * 4},
                    {"titel": "Sprinten", "val": attrs["SCH"].aktuell() * 4 + ferts["Laufen"]},

                    {"titel": "Reaktion", "val": (attrs["SCH"].aktuell() + attrs["GES"].aktuell() + attrs["WK"].aktuell()) / 2},
                    {"titel": "Intuition", "val": (attrs["IN"].aktuell() + 2 * attrs["SCH"].aktuell()) / 2},
                    {"titel": "Bewegung Astral", "val": 2 * attrs["MA"].aktuell() * (attrs["WK"].aktuell() + attrs["SCH"].aktuell())},
                    {"titel": "Tragfähigkeit", "val": 3 * attrs["ST"].aktuell() + attrs["GES"].aktuell()},
                    {"titel": "Heben", "val": 4 * attrs["ST"].aktuell() + attrs["N"].aktuell()},

                    {"titel": "Schwimmen", "val": round(attrs["SCH"].aktuell() * 2 / 3 + ferts["Schwimmen"] / 5, 1)},
                    {"titel": "Tauchen", "val": round(attrs["SCH"].aktuell() * 2 / 5 + ferts["Schwimmen"] / 5, 1)},
                    {"titel": "Ersticken", "val": 3 * attrs["WK"].aktuell() + ferts["Heben"] + ferts["Entschlossenheit"] + 3 * ferts["Schwimmen"]},
                    {"titel": "Immunsystem", "val": 5 * attrs["ST"].aktuell() + attrs["VER"].aktuell() + ferts["Konstitution"] + ferts["Resistenz"]},
                    {"titel": "Regeneration", "val": 10 * (attrs["ST"].aktuell() + attrs["WK"].aktuell())},
                    {"titel": "Manaoverflow", "val": 100 * (attrs["MA"].aktuell() + attrs["WK"].aktuell())},
                ]


        # spezial
        elif section == sections[4]["name"]:

             # need attrs
            attrs = {}
            for rel in RelAttribut.objects.filter(char=char): attrs[rel.attribut.id] = rel

            # assemble spezial
            spezial = []
            for rel in RelSpezialfertigkeit.objects.filter(char=char):

                ausgleich = 0
                ferts = []
                for relFert in RelFertigkeit.objects.filter(char=char, fertigkeit__in=rel.spezialfertigkeit.ausgleich.all()):
                    ferts.append(relFert.fertigkeit.titel)
                    ausgleich += relFert.pool()

                spezial.append({
                    "titel": rel.spezialfertigkeit.titel,
                    "attrs": "{}, {}".format(rel.spezialfertigkeit.attr1.titel, rel.spezialfertigkeit.attr2.titel),
                    "ferts": ", ".join(ferts),
                    "ausgleich": floor(ausgleich / 2 + .5),
                    "stufe": rel.stufe - 5,
                    "pool": attrs[rel.spezialfertigkeit.attr1.id].aktuell() + attrs[rel.spezialfertigkeit.attr2.id].aktuell() + rel.stufe - 5
                })
            context["spezial"] = spezial


         # wissen
        elif section == sections[5]["name"]:

             # need attrs
            attrs = {}
            for rel in RelAttribut.objects.filter(char=char): attrs[rel.attribut.id] = rel

            # assemble wissen
            wissen = []
            for rel in RelWissensfertigkeit.objects.filter(char=char):

                ferts_sum = 0
                ferts = []
                for relFert in RelFertigkeit.objects.filter(char=char, fertigkeit__in=rel.wissensfertigkeit.fertigkeit.all()):
                    ferts.append(relFert.fertigkeit.titel)
                    ferts_sum += relFert.pool()

                wissen.append({
                    "titel": rel.wissensfertigkeit.titel,
                    "attrs": "{}, {}, {}".format(
                        rel.wissensfertigkeit.attr1.titel,
                        rel.wissensfertigkeit.attr2.titel,
                        rel.wissensfertigkeit.attr3.titel),
                    "ferts": ", ".join(ferts),
                    "ferts_sum": ferts_sum,
                    "w2": rel.würfel2,
                    "schwellwert": 100 - attrs[rel.wissensfertigkeit.attr1.id].aktuell() -
                                   attrs[rel.wissensfertigkeit.attr2.id].aktuell() -
                                   attrs[rel.wissensfertigkeit.attr3.id].aktuell() -
                                   ferts_sum
                })
            context["wissen"] = wissen


        # vorteil
        elif section == sections[6]["name"]:
            context["teil_kind"] = "Vorteil"
            context["teil"] = RelVorteil.objects.filter(char=char, will_create=False)


        # nachteil
        elif section == sections[7]["name"]:
            context["teil_kind"] = "Nachteil"
            context["teil"] = RelNachteil.objects.filter(char=char)


        # talent
        elif section == sections[8]["name"]:
            pass


        # wesenkraft
        elif section == sections[9]["name"]:
            context["wesenkr"] = RelWesenkraft.objects.filter(char=char)


        # affektivität
        elif section == sections[10]["name"]:
            affekt = []
            for a in Affektivität.objects.filter(char=char):

                um = 0
                meaning = ""

                # get meaning and um via binary search tree (sorry!)
                if a.wert < 10:
                    if a.wert < -30:
                        if a.wert < -70:
                            if a.wert < -100:
                                meaning = "Erzfeind"
                                um = -10
                            else:
                                meaning = "Schwerer Feind"
                                um = -7
                        elif a.wert < -50:
                            meaning = "Feind"
                            um = -5
                        else:
                            meaning = "Hass"
                            um = -3
                    elif a.wert < 1:
                        if a.wert < -10:
                            meaning = "Nicht mögen"
                            um = -2
                        else:
                            meaning = "Abneigung"
                            um = -1
                    else:
                        meaning = "Schon mal gesehen"
                        um = 0
                elif a.wert < 50:
                    if a.wert < 20:
                        meaning = "Bekanntschaft"
                        um = 1
                    elif a.wert < 30:
                        meaning = "Gute Bekannte"
                        um = 2
                    else:
                        meaning = "Kollegen"
                        um = 3
                elif a.wert < 85:
                    if a.wert < 70:
                        meaning = "Freunde"
                        um = 4
                    else:
                        meaning = "Gute Freunde"
                        um = 5
                elif a.wert < 101:
                    meaning = "Beste Freunde oder läuft da sogar was...?"
                    um = 7
                else:
                    meaning = "Entweder Blutsgeschwister oder es ist Liebe im Spiel..."
                    um = 10

                affekt.append({
                    "name": a.name,
                    "wert": a.wert,
                    "grad": meaning,
                    "um": um,
                    "notizen": a.notizen
                })

            context["affekt"] = affekt

        # items/shop
        elif section == sections[11]["name"]:
            shop_models = [
                RelItem, RelWaffen_Werkzeuge, RelMagazin, RelPfeil_Bolzen,
                RelSchusswaffen, RelMagische_Ausrüstung, RelRituale_Runen,
                RelRüstung, RelAusrüstung_Technik, RelFahrzeug, RelEinbauten,
                RelWesenkraft, RelVergessenerZauber, RelAlchemie, RelTinker, RelBegleiter
            ]

            items = []
            for model in shop_models:
                for rel in model.objects.filter(char=char):
                    items.append(rel)

            context["items"] = items


        # not implemented / invalid
        else:
            return HttpResponse("<h1 style='text-align:center'>Not jet implemented</h1>")

        return JsonResponse({"html": render(request, template, context).content.decode("utf-8")})
