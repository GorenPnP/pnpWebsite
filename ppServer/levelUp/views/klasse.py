from functools import cmp_to_key

from django.db.models import Sum, Value, CharField, OuterRef, Min, Q
from django.db.models.functions import Concat, Replace, Coalesce
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView

from character.models import Charakter, KlasseAbility, KlasseStufenplan, RelKlasse, RelKlasseAbility
from log.models import Log
from ppServer.utils import ConcatSubquery

from ..mixins import LevelUpMixin


class GenericKlasseView(LevelUpMixin, TemplateView):

    template_name = "levelUp/klasse.html"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        # own Klassen
        own_klassen = RelKlasse.get_own_number_annotated(char)\
            .annotate(
                abilities = ConcatSubquery(
                    KlasseAbility.objects\
                        .filter(Q(klassestufenplan__klasse=OuterRef("klasse")) & Q(klassestufenplan__stufe__lte=OuterRef("stufe")) | Q(klasse=OuterRef("klasse")))\
                        .annotate(repr = Concat(Value("<li><b>"), "name", Value("</b><br>"), Replace("beschreibung", Value("\n"), Value("<br>")), Value("</li>"), output_field=CharField()))\
                        .order_by("klasse", "klassestufenplan__stufe", "name")\
                        .values("repr"),
                    separator=""
                )
            )\
            .prefetch_related("klasse__base_abilities").order_by("-stufe", "klasse__titel")

        # KlasseStufenpläne of potentially new Klassen
        def sort_stufenplan(a, b):
            if a.requirements_met != b.requirements_met: return (-1 if a.requirements_met else 1)
            if a.current_stufe != b.current_stufe: return b.current_stufe - a.current_stufe
            if a.klasse.titel != b.klasse.titel: return (-1 if a.klasse.titel < b.klasse.titel else 1)
            return 0
        stufenpläne = sorted(KlasseStufenplan.get_choosable_KlasseStufenplan(char), key=cmp_to_key(sort_stufenplan))

        # add info for reduced rewards where necessary
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
        if not next((True for kl in KlasseStufenplan.get_choosable_KlasseStufenplan(char) if kl.requirements_met and kl.pk == stufenplan_id), False):
            messages.error(request, "Du kannst die Klassenstufe nicht wählen")
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

        # .. base-abilities
        if stufenplan.stufe == min_stufe:
            for ability in stufenplan.klasse.base_abilities.all():
                RelKlasseAbility.objects.create(char=char, ability=ability)

        # .. numeric
        if char.reduced_rewards_until_klasse_stufe < stufen_already_spent+1:
            char.ap += stufenplan.ap
            char.fp += stufenplan.fp
            char.fg += stufenplan.fg
            char.tp += stufenplan.tp
            char.ip += stufenplan.ip
            new_zauber = char.zauberplätze.get(f"{char.ep_stufe_in_progress}", 0) + stufenplan.zauber
            if new_zauber: char.zauberplätze[char.ep_stufe_in_progress] = new_zauber

            char.save(update_fields=["ap", "fp", "fg", "tp", "ip", "zauberplätze"])

        # .. stufe-abilities
        if stufenplan.ability: char.relklasseability_set.create(ability=stufenplan.ability)


        # LOG & RETURN
        Log.objects.create(art="l", spieler=request.spieler.instance, char=char, kosten=f"Charakter Stufe {stufen_already_spent+1}", notizen=f"{stufenplan.klasse.titel} Stufe {stufenplan.stufe}")
        messages.success(request, f"{stufenplan.klasse.titel}-Klassenstufe erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
