import json

from django.db.models import Subquery, OuterRef, Sum, Exists, F, Value, IntegerField
from django.db.models.base import Model as Model
from django.db.models.functions import Coalesce
from django.http import HttpResponseNotFound
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.utils.decorators import method_decorator

from ppServer.mixins import VerifiedAccountMixin

from base.abstract_views import DynamicTableView
from character.models import Wesenkraft, Beruf, RelAttribut, RelFertigkeit, RelVorteil,\
    RelNachteil, RelWesenkraft, GfsAttribut, GfsFertigkeit, GfsWesenkraft, GfsVorteil,\
    GfsNachteil, GfsZauber, GfsStufenplanBase, RelZauber, Klasse, RelKlasse, RelKlasseAbility, KlasseStufenplan
from levelUp.mixins import LevelUpMixin
from log.models import Log

from .decorators import *
from .models import *


class GfsWahlfilterView(VerifiedAccountMixin, DynamicTableView):

    model = GfsCharacterization
    topic = "Gfs Wahlfilter"
    template_name = "create/gfs_characterization.html"

    filterset_fields = ["gfs__difficulty", "state", "social", "magical", "can_punch", "can_shoot", "gets_pricy_skills", "can_fly", "attitude"]
    table_fields = ["gfs__titel", "gfs__beschreibung"]

    app_index = "Erstellung"
    app_index_url = "create:gfs"


class GfsFormView(VerifiedAccountMixin, TemplateView):

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "gfs": Gfs.objects.all(),
            "klassen": Klasse.objects.all(),
            "old_scetches": Charakter.objects.filter(eigentümer=request.spieler.instance, in_erstellung=True),
            "topic": "Charakter erstellen",
            "app_index": "Charaktere",
            "app_index_url": reverse("character:index"),
        }

        return render(request, "create/gfs.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        klassen_pks = Klasse.objects.all().values_list("pk", flat=True)
        try:
            gfs_id = int(request.POST["gfs_id"])
            larp = "larp" in request.POST
            stufe = int(request.POST.get("stufe")) if "stufe" in request.POST else 0
            klassenstufen = {int(key.replace("klasse-", "")): int(stufe) for key, stufe in request.POST.items() if "klasse-" in key and int(key.replace("klasse-", "")) in klassen_pks}
        except:
            return JsonResponse({"message": "Keine Gfs angekommen"}, status=418)
        
        if sum(klassenstufen.values()) != stufe:
            return JsonResponse({"message": "Charakter-Stufe stimmt nicht mit der Summe der Klassenstufen überein"}, status=418)

        spieler = request.spieler.instance
        if not spieler: return HttpResponseNotFound()
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
            if stufe > 1:
                char.ep = GfsStufenplanBase.objects.get(stufe=stufe).ep
            char.save(update_fields=["manifest", "wesenschaden_waff_kampf", "wesenschaden_andere_gestalt", "ep"])

            # Attributes
            objects = []
            qs = RelAttribut.objects.annotate(
                    aktuell=Subquery(GfsAttribut.objects.filter(gfs=char.gfs, attribut=OuterRef("attribut")).values("aktuellerWert")[:1]),
                    max=Subquery(GfsAttribut.objects.filter(gfs=char.gfs, attribut=OuterRef("attribut")).values("maxWert")[:1]),
                )\
                .filter(char=char)
            for e in qs:
                e.aktuellerWert = e.aktuell
                e.maxWert = e.max
                objects.append(e)
            RelAttribut.objects.bulk_update(objects, fields=["aktuellerWert", "maxWert"])
            
            # Fertigkeiten
            objects = []
            qs = RelFertigkeit.objects.annotate(
                    bonus=Subquery(GfsFertigkeit.objects.filter(gfs=char.gfs, fertigkeit=OuterRef("fertigkeit")).values("fp")[:1])
                )\
                .filter(char=char).exclude(bonus=0)

            for e in qs:
                e.fp_bonus = e.bonus
                objects.append(e)
            RelFertigkeit.objects.bulk_update(objects, fields=["fp_bonus"])

            # Wesenkräfte
            RelWesenkraft.objects.bulk_create([
                RelWesenkraft(
                    char=char, wesenkraft=gfs_wesenkr.wesenkraft,
                    tier=1 if gfs_wesenkr.tier_up else 0
                )

                for gfs_wesenkr in GfsWesenkraft.objects.prefetch_related("wesenkraft").annotate(
                    tier_up = Exists(Wesenkraft.objects.filter(pk=OuterRef("wesenkraft"), skilled_gfs=gfs)),
                ).filter(gfs=char.gfs)
            ])

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
            RelZauber.objects.bulk_create([
                RelZauber(char=char, item=gfs_zauber.item, tier=gfs_zauber.tier)
                for gfs_zauber in GfsZauber.objects.filter(gfs=char.gfs)
            ])

            # Klassen
            for klasse in Klasse.objects.filter(pk__in=klassenstufen.keys()):
                RelKlasse.objects.create(char=char, klasse=klasse, stufe=klassenstufen[klasse.id])
                # klasse logging
                Log.objects.create(art="l", spieler=request.spieler.instance, char=char, kosten=f"Charaktererstellung", notizen=f"{klasse.titel} bis Stufe {klassenstufen[klasse.id]}")
                # note: values of chosen Klassen will be distributed in Prio.post() due to crotocal values for priotable

        return redirect(reverse("create:prio", args=[char.id]))


@method_decorator([is_gfs_done, is_prio_missing], name="dispatch")
class PriotableFormView(LevelUpMixin, DetailView):
    template_name = "create/prio.html"
    model = Charakter

    # number of WP per spF & wF chosen
    WP_FACTOR = 4

    class ResponseData:
        @staticmethod
        def get_fieldnames() -> list[str]:
            return ["ip", "ap", "fp", "sp", "zauber", "drachmen"]

        def __init__(self, ip: Priotable, ap: Priotable, fp: Priotable, sp: Priotable, zauber: Priotable, drachmen: Priotable):
            self.ip = ip
            self.ap = ap
            self.fp = fp
            self.sp = sp
            self.zauber = zauber
            self.drachmen = drachmen
        
        def valid(self) -> bool:
            return len([1 for field in self.__class__.get_fieldnames() if getattr(self, field) is None]) == 0
        
        def keys(self):
            return self.__class__.get_fieldnames()
        
        def values(self) -> list[Priotable]:
            return [getattr(self, field) for field in self.__class__.get_fieldnames()]
        

    def get_entries(self):
        return Priotable.objects.all()


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs,
            topic = "Prioritätentabelle",
            table = self.get_entries(),
            points = self.get_entries().aggregate(cost = Sum("cost"))["cost"],
            notes = [
                "IP = für Vor- und Nachteile",
                "AP = Aufwerten eines Attributs",
                "SP = für alles Mögliche, vor Allem um nicht zu sterben",
                "Konz. = Konzentration, um Proben besser zu würfeln als sonst",
                "FP = Fertigkeitspunkte",
                "FG = Fertigkeitsgruppen",
                "Zauber = Anz. wählbarer Zauber, bzw. Zauberverbesserungen",
                "Drachmen = Geld",
                "SP-Fert und W-Fert = wählbare Spezialisierungen"
            ]
        )
        context["back_url"] = reverse("create:gfs")
        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_object()

        # collect data
        if char is None:
            return JsonResponse({"url": reverse("create:gfs")}, status=300)


        try:
            prio_by_name = {prio.priority: prio for prio in self.get_entries()}

            chosen_fields = PriotableFormView.ResponseData(**{
                key: prio_by_name[value]
                    for key, value in list(json.loads(request.body.decode("utf-8")).items())
                    if key in PriotableFormView.ResponseData.get_fieldnames() and value in prio_by_name.keys()
            })
        except:
            return JsonResponse({'message': 'Falsche Auswahl (Format)'}, status=418)

        if not chosen_fields.valid():
            return JsonResponse({"message": "Falsche Auswahl (Anzahl Felder)"}, status=418)

        # cost points
        spend = sum([prio.cost for prio in chosen_fields.values()])
        cost = self.get_entries().aggregate(cost = Sum("cost"))["cost"]
        if spend != cost:
            return JsonResponse({"message": f"Die gewählten Prioritäten kosten {spend} Punkte von {cost} Punkten. Es darf keiner übrig bleiben."}, status=418)

        # cost ap
        if getattr(chosen_fields, "ap").ap - char.gfs.ap < 0:
            return JsonResponse({"message": "Zu wenig AP für Gfs"}, status=418)

        fields = []
        prio = None
        # ip
        prio = getattr(chosen_fields, "ip")
        char.ip = prio.ip
        fields.append({"prio": prio.priority, "text": f"{prio.ip} IP"})

        # ap
        prio = getattr(chosen_fields, "ap")
        char.ap = prio.ap - char.gfs.ap
        fields.append({"prio": prio.priority, "text": f"{prio.ap} AP"})

        # sp & konzentration
        prio = getattr(chosen_fields, "sp")
        char.sp = prio.sp
        char.konzentration = prio.konzentration
        fields.append({"prio": prio.priority, "text":  f"{prio.sp} SP, {prio.konzentration} Konz."})

        # fp & fg
        prio = getattr(chosen_fields, "fp")
        char.fp = prio.fp
        char.fg = prio.fg
        fields.append({"prio": prio.priority, "text":  f"{prio.fp} FP, {prio.fg} FG"})

        # zauber
        prio = getattr(chosen_fields, "zauber")
        char.zauberplätze = {"0": prio.zauber} if prio.zauber else {}
        fields.append({"prio": prio.priority, "text": f"{prio.zauber} Zauber"})

        # drachmen & spF_wF
        prio = getattr(chosen_fields, "drachmen")
        char.geld = prio.drachmen
        char.spF_wF = prio.spF_wF
        char.wp = prio.spF_wF * self.WP_FACTOR
        fields.append({"prio": prio.priority, "text":  f"{prio.drachmen} Drachmen, {prio.spF_wF} Sp-Fert/W-Fert"})


        char.processing_notes["priotable"] = fields

        # rewards of Klassen ..

        # .. KlasseAbility
        qs = KlasseStufenplan.objects\
            .annotate(
                max_stufe=Coalesce(Subquery(RelKlasse.objects.filter(char=char, klasse=OuterRef("klasse")).values("stufe")), Value(0), output_field=IntegerField()),
            )\
            .filter(stufe__lte=F("max_stufe")).exclude(ability=None)
        for stufenplan in qs:
            RelKlasseAbility.objects.create(char=char, ability=stufenplan.ability)

        klasse_rewards = RelKlasse.get_own_number_annotated(char) # has keys { "klasse", "ap", "fp", "fg", "tp", "ip", "zauber", ...}
        for reward in klasse_rewards:
            # .. numeric
            char.ap += reward.ap
            char.fp += reward.fp
            char.fg += reward.fg
            char.tp += reward.tp
            char.ip += reward.ip
            new_zauber = char.zauberplätze.get(f"{char.ep_stufe_in_progress}", 0) + reward.zauber
            if new_zauber: char.zauberplätze[char.ep_stufe_in_progress] = new_zauber

            # .. base-abilities
            for ability in reward.klasse.base_abilities.all():
                RelKlasseAbility.objects.create(char=char, ability=ability)

        char.save(update_fields=["ip", "sp", "konzentration", "fp", "fg", "zauberplätze", "geld", "spF_wF", "wp", "ap", "tp", "processing_notes"])

        if not char.processing_notes["creation_larp"] and char.ep:
            char.init_stufenhub()

        return JsonResponse({"url": reverse("levelUp:index", args=[char.id])})
