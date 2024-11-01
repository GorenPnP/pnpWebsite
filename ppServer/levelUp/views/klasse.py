from django.db.models import Sum, Value, CharField, OuterRef, Subquery, Min
from django.db.models.functions import Concat, Replace, Coalesce
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView

from character.models import Charakter, KlasseAbility, KlasseStufenplan
from log.models import Log
from ppServer.utils import ConcatSubquery

from ..mixins import LevelUpMixin


class GenericKlasseView(LevelUpMixin, TemplateView):

    template_name = "levelUp/klasse.html"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        get_SumSubquery = lambda field: KlasseStufenplan.objects\
            .filter(klasse=OuterRef("klasse"), stufe__lte=OuterRef("stufe"))\
            .values("klasse")\
            .annotate(sum=Sum(field))\
            .values("sum")

        own_klassen = char.relklasse_set\
            .annotate(
                ap = Subquery(get_SumSubquery("ap")),
                fp = Subquery(get_SumSubquery("fp")),
                fg = Subquery(get_SumSubquery("fg")),
                tp = Subquery(get_SumSubquery("tp")),
                ip = Subquery(get_SumSubquery("ip")),
                zauber = Subquery(get_SumSubquery("zauber")),
                abilities = ConcatSubquery(
                    KlasseAbility.objects\
                        .filter(klassestufenplan__klasse=OuterRef("klasse"), klassestufenplan__stufe__lte=OuterRef("stufe"))\
                        .annotate(repr = Concat(Value("<li><b>"), "name", Value("</b><br>"), Replace("beschreibung", Value("\n"), Value("<br>")), Value("</li>"), output_field=CharField()))\
                        .order_by("klassestufenplan__stufe")\
                        .values("repr"),
                    separator=""
                )
            )\
            .prefetch_related("klasse").order_by("-stufe", "klasse__titel")

        stufenpläne = KlasseStufenplan.get_choosable_KlasseStufenplan(char)\
            .prefetch_related("klasse")\
            .order_by("-current_stufe", "klasse__titel")
        
        if char.reduced_rewards_until_klasse_stufe:
            messages.info(self.request, f"{char.name} ist älter als Klassen, bekommt also bis Charakterstufe {char.reduced_rewards_until_klasse_stufe} nur deren Fähigkeiten.")

        return super().get_context_data(*args, **kwargs,
            missing_stufen = char.ep_stufe_in_progress - char.relklasse_set.aggregate(stufen=Coalesce(Sum("stufe"), 0))["stufen"],
            own_klassen = own_klassen,
            stufenpläne = stufenpläne,
            topic = "Klassen",
        )


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character(Charakter.objects.prefetch_related("relklasse_set"))

        # GATHER DATA
        stufenplan_id = int(request.POST.get("stufenplan_id"))


        # PERFORM CHECKS

        # no new klassenstufe choosable
        stufen_already_spent = char.relklasse_set.aggregate(stufen=Coalesce(Sum("stufe"), 0))["stufen"] +1
        missing_stufen = char.ep_stufe_in_progress - stufen_already_spent
        if missing_stufen < 0:
            messages.error(request, "Du kannst gerade keine Klassenstufen wählen")
            return redirect(request.build_absolute_uri())

        # char already has stufenplan
        if KlasseStufenplan.get_own_KlasseStufenplan(char).filter(pk=stufenplan_id).exists():
            messages.error(request, "Du wolltest eine Klassenstufe nochmal wählen")
            return redirect(request.build_absolute_uri())

        # char cannot get stufenplan
        if not KlasseStufenplan.get_choosable_KlasseStufenplan(char).filter(pk=stufenplan_id).exists():
            messages.error(request, "Du kannst die Klassenstufe nicht wählenn")
            return redirect(request.build_absolute_uri())


        # RECEIVE REWARDS
    
        stufenplan = get_object_or_404(KlasseStufenplan.objects.prefetch_related("klasse", "ability"), pk=stufenplan_id)
        min_stufe = KlasseStufenplan.objects.filter(klasse=stufenplan.klasse).aggregate(min_stufe = Min("stufe"))["min_stufe"]

        # add stufe to relklasse
        if stufenplan.stufe == min_stufe:
            char.relklasse_set.create(klasse=stufenplan.klasse, stufe=stufenplan.stufe)
        else:
            char.relklasse_set.filter(klasse=stufenplan.klasse).update(stufe=stufenplan.stufe)

        # give rewards to char

        notizen = []
        # keep notizen as is
        if char.notizen: notizen.append(char.notizen)
        # add base-klasse
        if stufenplan.stufe == min_stufe:
            notizen.append(f"---\n{stufenplan.klasse.titel} 1:\n{stufenplan.klasse.beschreibung}\n---")
        char.notizen = "\n\n".join(notizen)

        if char.reduced_rewards_until_klasse_stufe < stufen_already_spent+1:
            char.ap += stufenplan.ap
            char.fp += stufenplan.fp
            char.fg += stufenplan.fg
            char.tp += stufenplan.tp
            char.ip += stufenplan.ip
            char.zauberplätze[char.ep_stufe_in_progress] = char.zauberplätze.get(f"{char.ep_stufe_in_progress}", 0) + stufenplan.zauber

            char.save(update_fields=["ap", "fp", "fg", "tp", "ip", "zauberplätze", "notizen"])
        else:
            char.save(update_fields=["notizen"])
        if stufenplan.ability: char.relklasseability_set.create(ability=stufenplan.ability)

        # LOG & RETURN
        Log.objects.create(art="l", spieler=request.spieler.instance, char=char, kosten=f"Charakter Stufe {stufen_already_spent+1}", notizen=f"{stufenplan.klasse.titel} Stufe {stufenplan.stufe}")
        messages.success(request, "Klassenstufe erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
