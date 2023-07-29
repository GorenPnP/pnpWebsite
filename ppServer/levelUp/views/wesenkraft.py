from django.db.models import Sum
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from character.models import RelWesenkraft, RelAttribut, get_tier_cost_with_sp

from ..mixins import LevelUpMixin
from ..views import get_required_aktuellerWert


class GenericWesenkraftView(LevelUpMixin, TemplateView):

    template_name = "levelUp/wesenkraft.html"


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()
        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')

        return super().get_context_data(*args, **kwargs,
            own_wesenkraft = RelWesenkraft.objects.filter(char=char).order_by("wesenkraft__titel"),
            MA_aktuell = rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp + rel_ma.aktuellerWert_bonus - get_required_aktuellerWert(char, "MA"),
            get_tier_cost_with_sp = get_tier_cost_with_sp(),
            topic = "Wesenkraft",
        )


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        # GATHER DATA
        rel_wesenkraft_ids = [int(id) for id in request.POST.keys() if id.isnumeric()]

        new_tiers = {id: int(request.POST.get(str(id))) for id in rel_wesenkraft_ids}
        rel_wesenkraft = RelWesenkraft.objects.filter(char=char, id__in=rel_wesenkraft_ids)


        # PERFORM CHECKS

        # char already has wesenkraft
        if rel_wesenkraft.count() != len(rel_wesenkraft_ids):
            messages.error(request, "Du wolltest Tier zu Wesenkräften vergeben, die du gar nicht kennst")
            return redirect(request.build_absolute_uri())

        for rel in rel_wesenkraft:
            # not lower than current value
            if rel.tier > new_tiers[rel.id]:
                messages.error(request, "Du kannst Tier nicht wieder verkaufen")
                return redirect(request.build_absolute_uri())
            
            # has to be lower than max_tier
            if rel.tier > char.max_tier_allowed():
                messages.error(request, f"Du kannst Tier nicht über {char.max_tier_allowed()} steigern")
                return redirect(request.build_absolute_uri())

        if request.POST.get("payment_method") == "sp":
            sp = 0
            for rel in rel_wesenkraft:
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
            
            ap_available = char.ap + rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp + rel_ma.aktuellerWert_bonus - get_required_aktuellerWert(char, "MA")
            ap_to_pay = sum(new_tiers.values()) - rel_wesenkraft.aggregate(tier_sum=Sum("tier"))["tier_sum"]


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
        for rel in rel_wesenkraft:
            rel.tier = new_tiers[rel.id]
            rels.append(rel)
        RelWesenkraft.objects.bulk_update(rels, fields=["tier"])

        # return
        messages.success(request, "Tiers erfolgreich gespeichert")
        return redirect(request.build_absolute_uri())
