import json, re
from math import floor

from django.db.models import F, Subquery, OuterRef, Q, Count, Sum, Value, Window, Func, Exists
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html

import django_tables2 as tables
from django_tables2.columns import TemplateColumn

from ppServer.mixins import VerifiedAccountMixin

from base.abstract_views import DynamicTableView, DynamicTablesView, GenericTable
from levelUp.decorators import *
from levelUp.views import *
from character.enums import würfelart_enum
from character.models import *
from shop.models import Zauber

from .mixins import CreateMixin
from .models import *

hub_decorators = [provide_char, gfs_done, prio_done]



class GfsWahlfilterView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):

    model = GfsCharacterization
    topic = "Gfs Wahlfilter"
    template_name = "create/gfs_characterization.html"

    filterset_fields = ["gfs__difficulty", "state", "social", "magical", "can_punch", "can_shoot", "gets_pricy_skills", "can_fly", "attitude"]
    table_fields = ["gfs__titel", "gfs__beschreibung"]

    app_index = "Erstellung"
    app_index_url = "create:gfs"



@method_decorator(hub_decorators, name="dispatch")
class LandingPageView(LoginRequiredMixin, CreateMixin, OwnCharakterMixin, TemplateView):

    def get(self, request: HttpRequest, char: Charakter) -> HttpResponse:

        # rows
        rows = []
        rows.append({"done": is_personal_done(request, char=char), "link": reverse("create:personal"), "text": "<b>Persönliches</b> festlegen", "werte": "-", "id": "personal"})
        rows.append({"done": is_ap_done(request, char=char), "link": reverse("create:ap"), "text": "<b>Attribute</b> verteilen", "werte": "{} AP".format(char.ap), "id": "attr"})
        rows.append({"done": is_ferts_done(request, char=char), "link": reverse("create:fert"), "text": "<b>Fertigkeiten</b> verteilen",
                     "werte": "{} FP<br>{} FG".format(char.fp, char.fg), "id": "fert"})

        if not char.larp:
            rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')
            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp
            zauber_werte = "<br>".join([
                *[f"{amount} Stufe {stufe} Zauber" for stufe, amount in char.zauberplätze.items()],
                f"{char.sp} SP",
                f"{char.ap} AP / {MA_aktuell} MA"
            ])

            rows.append({"done": is_zauber_done(request, char=char), "link": reverse("create:zauber"), "text": "<b>Zauber</b> aussuchen", "werte": zauber_werte})
            rows.append({"done": is_spF_wF_done(request, char=char), "link": reverse("create:spF_wF"), "text": "<b>Spezial- und Wissensfertigkeiten</b> wählen", "werte": "{} offen<br>{} WP<br>{} SP".format(char.spF_wF, char.wp, char.sp)})


        # submit-btn disabled state
        done_completely =\
            is_personal_done(request, char=char) and\
            is_ap_done(request, char=char) and\
            is_ferts_done(request, char=char) and\
            is_zauber_done(request, char=char) and\
            is_spF_wF_done(request, char=char) and\
            is_teil_done(request, char=char)


        # infos
        infos = [
            "<strong>Deine Gfs/Klasse</strong> kannst du dir <a href='{}' target='_blank'>hier</a> nochmal angucken.".format(reverse("wiki:stufenplan", args=[char.gfs.id])),
            "Im <strong><a href='{}' target='_blank'>Shop</a></strong> kannst du Ausrüstung kaufen.".format(reverse("shop:index")),
        ]

        # assemble context & render
        context = {
            "topic": "Erstellungshub",
            "rows": rows,
            "done": done_completely,
            "infos": infos,
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),

            "is_teil_done": is_teil_done(request, char=char),
            "ip": char.ip,
        }
        return render(request, "create/landing_page.html", context=context)


    def post(self, request: HttpRequest, char: Charakter) -> HttpResponse:

        rels = []
        for rel in RelAttribut.objects.filter(char=char):
            rel.aktuellerWert += rel.aktuellerWert_temp
            rel.aktuellerWert_temp = 0

            rel.maxWert += rel.maxWert_temp
            rel.maxWert_temp = 0

            rels.append(rel)
        RelAttribut.objects.bulk_update(rels, fields=["aktuellerWert", "aktuellerWert_temp", "maxWert", "maxWert_temp"])

        char.in_erstellung = False
        char.save(update_fields=["in_erstellung"])

        return redirect(reverse("character:show", args=[char.id]))


class GfsFormView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    def get(self, request: HttpRequest) -> HttpResponse:

        username = request.user.username
        old_scetches = Gfs.objects\
            .prefetch_related("charakter_set__eigentümer")\
            .filter(charakter__eigentümer__name=username, charakter__in_erstellung=True)

        context = {
            "gfs": Gfs.objects.all(),
            "old_scetches": old_scetches,
            "topic": "Charakter erstellen",
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        }

        return render(request, "create/gfs.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            gfs_id = int(request.POST["gfs_id"])
            larp = "larp" in request.POST
        except:
            return JsonResponse({"message": "Keine Gfs angekommen"}, status=418)

        spieler = get_object_or_404(Spieler, name=request.user.username)
        gfs = get_object_or_404(Gfs, id=gfs_id)

        # alle Charaktere in_erstellung löschen
        Charakter.objects.filter(eigentümer=spieler, in_erstellung=True).delete()

        # create new character
        char = Charakter.objects.create(eigentümer=spieler, gfs=gfs, larp=larp, in_erstellung=True)

        # set default vals
        if larp:
            char.ap = 100
            char.fp = 20
            char.fg = 2
            char.geld = 5000
            char.sp = 0
            char.ip = 0
            char.zauberplätze = {}
            char.beruf = get_object_or_404(Beruf, titel="Schüler")
            char.save(update_fields=["ap", "fp", "fg", "geld", "sp", "ip", "zauberplätze", "beruf"])

        else:
            # some fields
            char.manifest = char.gfs.startmanifest
            char.wesenschaden_waff_kampf = char.gfs.wesenschaden_waff_kampf
            char.wesenschaden_andere_gestalt = char.gfs.wesenschaden_andere_gestalt
            char.save(update_fields=["manifest", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt"])

            # Attributes
            objects = []
            for e in RelAttribut.objects.filter(char=char):
                gfs_attr = GfsAttribut.objects.get(gfs=char.gfs, attribut=e.attribut)

                e.aktuellerWert = gfs_attr.aktuellerWert
                e.maxWert = gfs_attr.maxWert
                objects.append(e)
            RelAttribut.objects.bulk_update(objects, fields=["aktuellerWert", "maxWert"])
            
            # Fertigkeiten
            objects = []
            for gfs_fert in GfsFertigkeit.objects.filter(gfs=char.gfs, fp__gt=0):
                e = RelFertigkeit.objects.get(char=char, fertigkeit=gfs_fert.fertigkeit)
                e.fp_bonus = gfs_fert.fp
                objects.append(e)
            RelFertigkeit.objects.bulk_update(objects, fields=["fp_bonus"])

            # Wesenkräfte
            for gfs_wesenkr in GfsWesenkraft.objects.filter(gfs=char.gfs):
                RelWesenkraft.objects.create(char=char, wesenkraft=gfs_wesenkr.wesenkraft)

            # Vorteile
            for gfs_teil in GfsVorteil.objects.filter(gfs=char.gfs):
                RelVorteil.objects.create(
                    char=char, teil=gfs_teil.teil,
                    notizen=gfs_teil.notizen,

                    # special fields
                    attribut=gfs_teil.attribut,
                    fertigkeit=gfs_teil.fertigkeit,
                    engelsroboter=gfs_teil.engelsroboter,
                    ip=gfs_teil.ip
                )

            # Nachteile
            for gfs_teil in GfsNachteil.objects.filter(gfs=char.gfs):
                RelNachteil.objects.create(
                    char=char, teil=gfs_teil.teil,
                    notizen=gfs_teil.notizen,

                    # special fields
                    attribut=gfs_teil.attribut,
                    fertigkeit=gfs_teil.fertigkeit,
                    engelsroboter=gfs_teil.engelsroboter,
                    ip=gfs_teil.ip
                )

        return redirect("create:prio")


@method_decorator([provide_char, gfs_done, prio_not_done], name="dispatch")
class PriotableFormView(LoginRequiredMixin, CreateMixin, OwnCharakterMixin, TemplateView):

    # number of WP per spF & wF chosen
    WP_FACTOR = 4

    def get_entries(self):
        return Priotable.objects.all().values_list("priority", "ip", "ap", "sp", "konzentration", "fp", "fg", "zauber", "drachmen", "spF_wF")


    def get(self, request: HttpRequest, char: Charakter) -> HttpResponse:
        entries = self.get_entries()

        # # get MA maximum
        # max_MA = max_MA = GfsAttribut.objects.get(gfs=char.gfs, attribut__titel="MA").maxWert

        # # mundan => keine Zauber wählbar (nur 0 Zauber in prio F)
        # if max_MA == 0:
        #     for k in range(entries.count()):
        #         entries[k][7] = entries[k][7] and None  # produces 0 | None

        notes = [
            "IP = für Vor- und Nachteile",
            "AP = Aufwerten eines Attributs",
            "SP = für alles Mögliche, vor Allem um nicht zu sterben",
            "Konz. = Konzentration, um Proben besser zu würfeln als sonst",
            "FP = Fertigkeitspunkte",
            "FG = Fertigkeitsgruppen",
        ]

        context = {
            "topic": "Prioritätentabelle",
            'table': entries,
            'notizen': notes,
            "ap_cost": char.gfs.ap,
            "gfs": char.gfs,
            "app_index": "Erstellung",
            "app_index_url": reverse("create:prio"),
        }
        return render(request, "create/prio.html", context)


    def post(self, request: HttpRequest, char: Charakter) -> HttpResponse:
        entries = self.get_entries()

        # collect data
        num_entries = entries.count()
        if char is None:
            return JsonResponse({"url": reverse("create:gfs")}, status=300)

        fields = {}
        try:
            for k, v in json.loads(request.body.decode("utf-8")).items(): fields[k] = int(v)
        except:
            return JsonResponse({'message': 'Falsche Auswahl (Format)'}, status=418)

        if len(fields.values()) != num_entries:
            return JsonResponse({"message": "Falsche Auswahl (Anzahl Felder)"}, status=418)

        for val in fields.values():
            if val < 0 or val >= num_entries:
                return JsonResponse({"message": "Falsche Auswahl (Inhalt Felder)"}, status=418)

        # start logic
        for category in fields.keys():
            row = fields[category]
            col = int(category) + 1

            # row: [priority, IP, AP, (SP, konzentration), (FP, FG), Zauber, Drachmen]
            if col == 1:
                char.ip = entries[row][col]
            elif col == 2:
                ap = entries[row][col]

            elif col == 3:
                char.sp = entries[row][col]
                char.konzentration = entries[row][col + 1]
            elif col == 4:
                char.fp = entries[row][col + 1]
                char.fg = entries[row][col + 2]
            elif col == 5:
                amount = entries[row][col + 2]
                char.zauberplätze = {"0": amount} if amount else {}
            else:
                char.geld = entries[row][col + 2]
                char.spF_wF = entries[row][col + 3]
                char.wp = entries[row][col + 3] * self.WP_FACTOR

        ap -= char.gfs.ap
        if ap < 0:
            return JsonResponse({"message": "Zu wenig AP für Gfs"}, status=418)

        char.ap = ap
        char.save(update_fields=["ip", "sp", "konzentration", "fp", "fg", "zauberplätze", "geld", "spF_wF", "wp", "ap"])

        return JsonResponse({"url": reverse("create:landing_page")})



@method_decorator(hub_decorators, name="dispatch")
class PersonalFormView(CreateMixin, GenericPersonalView):
    pass


@method_decorator(hub_decorators, name="dispatch")
class ApFormView(CreateMixin, GenericAttributView):
    pass


@method_decorator(hub_decorators, name="dispatch")
class FertigkeitFormView(CreateMixin, GenericFertigkeitView):
    pass


@method_decorator(hub_decorators, name="dispatch")
class ZauberFormView(CreateMixin, GenericZauberView):
    pass


@method_decorator(hub_decorators, name="dispatch")
class SpF_wFFormView(CreateMixin, GenericSpF_wFView):
    pass


@method_decorator(hub_decorators, name="dispatch")
class VorteilFormView(CreateMixin, GenericVorteilView):
    pass

@method_decorator(hub_decorators, name="dispatch")
class NachteilFormView(CreateMixin, GenericNachteilView):
    pass