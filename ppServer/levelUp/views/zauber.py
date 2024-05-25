from django.db.models import Sum
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from character.models import RelAttribut, FirmaZauber, get_tier_cost_with_sp, RelZauber
from shop.models import Zauber

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin
from ..views import get_required_aktuellerWert


@method_decorator([is_erstellung_done], name="dispatch")
class GenericZauberView(LevelUpMixin, TemplateView):

    template_name = "levelUp/zauber.html"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')
        zauberplätze = char.zauberplätze if char.zauberplätze else {}
        max_stufe = max([int(k) for k in zauberplätze.keys()], default=-1)
        zauber = Zauber.objects\
                .filter(frei_editierbar=False, ab_stufe__lte=max_stufe)\
                .exclude(id__in=char.zauber.values("id"))\
                .values("id", "name")
        
        for z in zauber:
            z["geld"] = min([f.getPrice() for f in FirmaZauber.objects.filter(item__id=z["id"])])

        return super().get_context_data(*args, **kwargs,
            own_zauber = RelZauber.objects.filter(char=char).order_by("item__name"),
            zauber = zauber,

            MA_aktuell = rel_ma.aktuell() - get_required_aktuellerWert(char, "MA") if rel_ma.aktuellerWert_fix is None else 0,
            free_slots = sum(zauberplätze.values()),
            get_tier_cost_with_sp = get_tier_cost_with_sp(),
            topic = "Zauber",
        )


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()
        operation = request.POST.get("operation")

        if operation == "create":
            zauber_id = request.POST.get("zauber_id")
            zauber = get_object_or_404(Zauber, id=zauber_id)
            
            # checks
            if RelZauber.objects.filter(char=char, item=zauber).exists():
                messages.error(request, f"Den Zauber {zauber.name} kennst du bereits.")
                return redirect(request.build_absolute_uri())

            min_stufe_of_slots = min([int(z) for z in char.zauberplätze.keys() if int(z) >= zauber.ab_stufe], default=-1)
            if min_stufe_of_slots == -1:
                messages.error(request, f"Du hast keinen passenden Zauberplatz für {zauber.name}.")
                return redirect(request.build_absolute_uri())
            
            price = min([t.getPrice() for t in FirmaZauber.objects.filter(item=zauber)])
            if not char.in_erstellung and char.geld < price:
                messages.error(request, f"Du hast nicht genug Geld für {zauber.name}.")
                return redirect(request.build_absolute_uri())


            # apply
            # zauberplätze
            char.zauberplätze[str(min_stufe_of_slots)] -= 1
            if char.zauberplätze[str(min_stufe_of_slots)] == 0:
                del char.zauberplätze[str(min_stufe_of_slots)]
            # geld
            if not char.in_erstellung: char.geld -= price
            char.save(update_fields=["zauberplätze", "geld"])

            RelZauber.objects.create(char=char, item=zauber)
            return redirect(request.build_absolute_uri())

        if operation == "update":
            # GATHER DATA
            rel_zauber_ids = [int(id) for id in request.POST.keys() if id.isnumeric()]

            new_tiers = {id: int(request.POST.get(str(id))) for id in rel_zauber_ids}
            rel_zauber = RelZauber.objects.filter(char=char, id__in=rel_zauber_ids)


            # PERFORM CHECKS

            # char already has zauber
            if rel_zauber.count() != len(rel_zauber_ids):
                messages.error(request, "Du wolltest Tier zu Zaubern vergeben, die du gar nicht kennst")
                return redirect(request.build_absolute_uri())

            for rel in rel_zauber:
                # not lower than current value
                if rel.tier > new_tiers[rel.id]:
                    messages.error(request, "Du kannst Tier nicht wieder verkaufen")
                    return redirect(request.build_absolute_uri())
                
                # has to be lower than max_tier
                if rel.tier > char.max_tier_allowed():
                    messages.error(request, f"Du kannst Tier nicht über {char.max_tier_allowed()} steigern")
                    return redirect(request.build_absolute_uri())


            if request.POST.get("payment_method") == "slot":

                # char has enough zauberplätze to pay for
                num_slots_char = sum(char.zauberplätze.values())
                num_slots_new_tier = sum(new_tiers.values()) - rel_zauber.aggregate(tier_sum=Sum("tier"))["tier_sum"]
                if num_slots_char < num_slots_new_tier:
                    messages.error(request, f"Du hast mehr neue Tier gewählt als du Zauberplätze hast")
                    return redirect(request.build_absolute_uri())


                # APPLY

                # pay <num_slots_new_tier> many zauberplätze
                while num_slots_new_tier > 0:
                    min_stufe = min([int(k) for k in char.zauberplätze.keys()])
                    diff = min(char.zauberplätze[str(min_stufe)], num_slots_new_tier)

                    num_slots_new_tier -= diff
                    if char.zauberplätze[str(min_stufe)] == diff:
                        del char.zauberplätze[str(min_stufe)]
                    else:
                        char.zauberplätze[str(min_stufe)] -= diff

                char.save(update_fields=["zauberplätze"])


            if request.POST.get("payment_method") == "sp":
                sp = 0
                for rel in rel_zauber:
                    new_tier = new_tiers[rel.id]
                    existing_tier = rel.tier
                    while new_tier > existing_tier:
                        sp += get_tier_cost_with_sp()[new_tier]
                        new_tier -= 1

                # char has enough sp to pay for
                if char.sp < sp:
                    messages.error(request, "Du hast zu wenig SP")
                    return redirect(request.build_absolute_uri())


                # pay SP
                char.sp -= sp
                char.save(update_fields=["sp"])

            if request.POST.get("payment_method") == "ap":
                rel_ma = get_object_or_404(RelAttribut, char=char, attribut__titel="MA")
                
                ap_available = char.ap + (rel_ma.aktuell() - get_required_aktuellerWert(char, "MA") if rel_ma.aktuellerWert_fix is None else 0)
                ap_to_pay = sum(new_tiers.values()) - rel_zauber.aggregate(tier_sum=Sum("tier"))["tier_sum"]


                # char has enough AP/MA.aktuellerWert to pay for
                if ap_available < ap_to_pay:
                    messages.error(request, "Du hast zu wenig AP / Magie")
                    return redirect(request.build_absolute_uri())

                # pay AP
                ap_diff = min(char.ap, ap_to_pay)
                ap_to_pay -= ap_diff
                char.ap -= ap_diff
                char.save(update_fields=["ap"])

                # pay MA
                ap_diff = min(rel_ma.aktuellerWert_temp, ap_to_pay)
                ap_to_pay -= ap_diff
                rel_ma.aktuellerWert_temp -= ap_diff

                ap_diff = min(rel_ma.aktuellerWert, ap_to_pay)
                ap_to_pay -= ap_diff
                rel_ma.aktuellerWert -= ap_diff

                ap_diff = min(rel_ma.aktuellerWert_bonus, ap_to_pay)
                ap_to_pay -= ap_diff
                rel_ma.aktuellerWert_bonus -= ap_diff
                rel_ma.save(update_fields=["aktuellerWert", "aktuellerWert_temp", "aktuellerWert_bonus"])


            # receive
            rels = []
            for rel in rel_zauber:
                rel.tier = new_tiers[rel.id]
                rels.append(rel)
            RelZauber.objects.bulk_update(rels, fields=["tier"])

            # return
            messages.success(request, "Tiers erfolgreich gespeichert")
            return redirect(request.build_absolute_uri())



        return redirect(request.build_absolute_uri())


