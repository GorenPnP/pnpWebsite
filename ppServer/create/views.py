import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.utils.decorators import method_decorator


from ppServer.mixins import VerifiedAccountMixin

from base.abstract_views import DynamicTableView
from character.models import Spieler, Beruf, RelAttribut, RelFertigkeit, RelVorteil,\
    RelNachteil, RelWesenkraft, GfsAttribut, GfsFertigkeit, GfsWesenkraft, GfsVorteil,\
    GfsNachteil, GfsZauber, GfsStufenplanBase
from levelUp.mixins import LevelUpMixin

from .decorators import *
from .models import *


class GfsWahlfilterView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):

    model = GfsCharacterization
    topic = "Gfs Wahlfilter"
    template_name = "create/gfs_characterization.html"

    filterset_fields = ["gfs__difficulty", "state", "social", "magical", "can_punch", "can_shoot", "gets_pricy_skills", "can_fly", "attitude"]
    table_fields = ["gfs__titel", "gfs__beschreibung"]

    app_index = "Erstellung"
    app_index_url = "create:gfs"


class GfsFormView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "gfs": Gfs.objects.all(),
            "old_scetches": Charakter.objects.filter(eigentümer__name=request.user.username, in_erstellung=True),
            "topic": "Charakter erstellen",
            "app_index": "Erstellung",
            "app_index_url": reverse("create:gfs"),
        }

        return render(request, "create/gfs.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            gfs_id = int(request.POST["gfs_id"])
            larp = "larp" in request.POST
            stufe = int(request.POST.get("stufe")) if "stufe" in request.POST else 0
        except:
            return JsonResponse({"message": "Keine Gfs angekommen"}, status=418)

        spieler = get_object_or_404(Spieler, name=request.user.username)
        gfs = get_object_or_404(Gfs, id=gfs_id)

        # alle Charaktere in_erstellung löschen
        Charakter.objects.filter(eigentümer=spieler, in_erstellung=True).delete()

        # create new character
        char = Charakter.objects.create(eigentümer=spieler, gfs=gfs, larp=larp, in_erstellung=True, processing_notes={"creation_larp": larp, "creation_stufe": stufe})

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
            if stufe:
                char.ep = GfsStufenplanBase.objects.get(stufe=stufe).ep
            char.save(update_fields=["manifest", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "ep"])

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
                tier = 1 if gfs_wesenkr.wesenkraft.skilled_gfs.filter(id=gfs.id).exists() else 0
                RelWesenkraft.objects.create(char=char, wesenkraft=gfs_wesenkr.wesenkraft, tier=tier)

            # Vorteile
            for gfs_teil in GfsVorteil.objects.filter(gfs=char.gfs):
                rel = RelVorteil.objects.create(
                    char=char, teil=gfs_teil.teil,
                    notizen=gfs_teil.notizen,

                    # special fields
                    attribut=gfs_teil.attribut,
                    fertigkeit=gfs_teil.fertigkeit,
                    engelsroboter=gfs_teil.engelsroboter,
                    ip=gfs_teil.ip,

                    # sellable? needs info?
                    is_sellable=gfs_teil.is_sellable,
                )
                rel.update_will_create()

            # Nachteile
            for gfs_teil in GfsNachteil.objects.filter(gfs=char.gfs):
                rel = RelNachteil.objects.create(
                    char=char, teil=gfs_teil.teil,
                    notizen=gfs_teil.notizen,

                    # special fields
                    attribut=gfs_teil.attribut,
                    fertigkeit=gfs_teil.fertigkeit,
                    engelsroboter=gfs_teil.engelsroboter,
                    ip=gfs_teil.ip,

                    # sellable?
                    is_sellable=gfs_teil.is_sellable,
                )
                rel.update_will_create()

            # Zauber
            for gfs_zauber in GfsZauber.objects.filter(gfs=char.gfs):
                RelWesenkraft.objects.create(char=char, item=gfs_zauber.item, tier=gfs_zauber.tier)


        return redirect(reverse("create:prio", args=[char.id]))


@method_decorator([is_gfs_done, is_prio_missing], name="dispatch")
class PriotableFormView(LevelUpMixin, DetailView):
    template_name = "create/prio.html"
    model = Charakter

    # number of WP per spF & wF chosen
    WP_FACTOR = 4

    def get_entries(self):
        return Priotable.objects.all().values_list("priority", "ip", "ap", "sp", "konzentration", "fp", "fg", "zauber", "drachmen", "spF_wF")


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            topic = "Prioritätentabelle",
            table = self.get_entries(),
            notes = [
                "IP = für Vor- und Nachteile",
                "AP = Aufwerten eines Attributs",
                "SP = für alles Mögliche, vor Allem um nicht zu sterben",
                "Konz. = Konzentration, um Proben besser zu würfeln als sonst",
                "FP = Fertigkeitspunkte",
                "FG = Fertigkeitsgruppen",
            ]
        )
        context["back_url"] = reverse("create:gfs")
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_object()
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

        if not char.processing_notes["creation_larp"] and char.ep:
            char.init_stufenhub()

        return JsonResponse({"url": reverse("levelUp:index", args=[char.id])})
