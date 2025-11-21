from typing import Callable

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Sum, Value, CharField, Exists, OuterRef
from django.db.models.functions import Concat, Replace
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from cards.models import Card, Transaction
from character.models import Charakter, RelAttribut, RelVorteil, Spieler, get_tier_cost_with_sp, RelZauber
from shop.models import Firma, FirmaZauber, Modifier, Zauber

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin
from ..views import get_required_aktuellerWert


@method_decorator([is_erstellung_done], name="dispatch")
class GenericZauberView(LevelUpMixin, UserPassesTestMixin, TemplateView):

    template_name = "levelUp/zauber.html"

    def test_func(self) -> bool:
        if not super().test_func(): return False

        char = self.get_character()
        return not char.no_MA and not char.no_MA_MG

    def _get_price_modifiers(self) -> dict[int, Callable[[float], float]]:
        ''' get price modifiers for Zauber by firma.pk
            Should be called once to be used everywhere needed, because it contains pricy db operations.
        '''
        return {firma.pk: Modifier.getModifier(firma, Zauber) for firma in Firma.objects.annotate(pick=Exists(FirmaZauber.objects.filter(firma=OuterRef("pk")))).filter(pick=True)}
        

    def get_context_data(self, *args, **kwargs):
        char = self.get_character(Charakter.objects.prefetch_related("zauber", "relzauber_set", "relattribut_set__attribut").annotate(
            # mind. 5 bei Zaubern:
            magieamateur_exists = Exists(RelVorteil.objects.filter(char=OuterRef("pk"), teil__titel="Magie-Amateur")),                    
            # mind. 10 bei Zaubern:
            magiegelehrter_exists = Exists(RelVorteil.objects.filter(char=OuterRef("pk"), teil__titel="Magie-Gelehrter")),
        ))

        zauberplätze = char.zauberplätze if char.zauberplätze else {}

        zauberplatz_stufe_limit = max([int(k) for k in zauberplätze.keys()], default=-1)
        char_stufe_limit = max(char.ep_stufe_in_progress, 5 if char.magieamateur_exists else 0, 10 if char.magiegelehrter_exists else 0)
        max_stufe = min(zauberplatz_stufe_limit, char_stufe_limit)

        own_zauber = char.relzauber_set.filter(learned=True).prefetch_related("item").all().annotate(
            querystring=Concat(Value('?name__icontains='), Replace("item__name", Value(" "), Value("+")), output_field=CharField()),
        ).order_by("item__name")

        firmen_modifiers = self._get_price_modifiers()
        zauber = [
            {"zauber": z, "geld": min([firmen_modifiers[f.firma.pk](f.preis) for f in z.firmazauber_set.all()])}
            for z in Zauber.objects.prefetch_related("firmazauber_set__firma")\
                .annotate(
                    querystring=Concat(Value('?name__icontains='), Replace("name", Value(" "), Value("+")), output_field=CharField()),
                )\
                .filter(frei_editierbar=False, ab_stufe__lte=max_stufe)\
                .exclude(id__in=char.zauber.values("id"))
        ]

        rel_ma = char.relattribut_set.get(attribut__titel='MA')
        return super().get_context_data(*args, **kwargs,
            own_zauber = own_zauber,
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
            if RelZauber.objects.filter(char=char, item=zauber, learned=True).exists():
                messages.error(request, f"Den Zauber {zauber.name} kennst du bereits.")
                return redirect(request.build_absolute_uri())

            min_stufe_of_slots = min([int(z) for z in char.zauberplätze.keys() if int(z) >= zauber.ab_stufe], default=-1)
            if min_stufe_of_slots == -1:
                messages.error(request, f"Du hast keinen passenden Zauberplatz für {zauber.name}.")
                return redirect(request.build_absolute_uri())
            
            firmen_modifiers = self._get_price_modifiers()
            firma_prices = {t.firma.name: firmen_modifiers[t.firma.pk](t.preis) for t in FirmaZauber.objects.prefetch_related("firma").filter(item=zauber)}
            price = min(firma_prices.values())
            firma_name = [k for k, v in firma_prices.items() if v == price][0]
            if not char.in_erstellung and char.geld < price:
                messages.error(request, f"Du hast nicht genug Geld für {zauber.name}.")
                return redirect(request.build_absolute_uri())


            # apply
            # zauberplätze
            char.zauberplätze[str(min_stufe_of_slots)] -= 1
            if char.zauberplätze[str(min_stufe_of_slots)] == 0:
                del char.zauberplätze[str(min_stufe_of_slots)]
            char.save(update_fields=["zauberplätze"])

            # geld
            if not char.in_erstellung:
                char.card.money -= price
                char.card.save(update_fields=["money"])

                spielleitung_spieler = get_object_or_404(Spieler, name__startswith="spielleit")
                receiver_card, _ = Card.objects.get_or_create(name=firma_name, spieler=spielleitung_spieler)

                Transaction.objects.create(sender=char.card, receiver=receiver_card, amount=price, reason=f"Zauber '{zauber.name}' erworben/gelernt")

            # TODO or update if exists as unlearned?
            RelZauber.objects.create(char=char, item=zauber, learned=True)
            return redirect(request.build_absolute_uri())

        if operation == "update":
            # GATHER DATA
            rel_zauber_ids = [int(id) for id in request.POST.keys() if id.isnumeric()]

            new_tiers = {id: int(request.POST.get(str(id))) for id in rel_zauber_ids}
            rel_zauber = RelZauber.objects.filter(char=char, id__in=rel_zauber_ids, learned=True)


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


