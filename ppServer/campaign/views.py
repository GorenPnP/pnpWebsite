import re
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import reverse
from django.views.generic import DetailView

from character.models import Charakter, RelVorteil, RelAttribut
from levelUp.decorators import is_ferts_done, is_zauber_done, is_personal_done, is_spF_wF_done, is_teil_done
from levelUp.views import *
from .mixins import CampaignMixin


class HubView(LoginRequiredMixin, CampaignMixin, OwnCharakterMixin, DetailView):
    model = Charakter

    template_name = "campaign/hub.html"


    def is_done(self):
        char = self.get_character()
        is_eigentümer = self.request.user.username == char.eigentümer.name
            
        return is_eigentümer and\
            char.ap <= 1 and\
            is_ferts_done(self.request, char=char) and\
            is_zauber_done(self.request, char=char) and\
            is_personal_done(self.request, char=char) and\
            is_spF_wF_done(self.request, char=char) and\
            is_teil_done(self.request, char=char)
            # TODO teil if needed Rückmeldung?


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        char = self.get_character()
        context = super().get_context_data(**kwargs, char=char)

        base_qs = []
        if char.gfs:
            base_qs = char.gfs.gfsstufenplan_set\
                .prefetch_related("basis")\
                .filter(basis__stufe__gt=char.ep_stufe, basis__stufe__lte=char.ep_stufe_in_progress)
            
            stufenbelohnung = []
            for stufe in base_qs:
                stufen_str = []
                if stufe.basis.ap: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-pink)'>+{stufe.basis.ap} AP</b>")
                if stufe.basis.fp: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-indigo)'>+{stufe.basis.fp} FP</b>")
                if stufe.basis.fg: stufen_str.append(f"<b class='badge rounded-pill' style='background-color: var(--bs-blue)'>+{stufe.basis.fg} FG</b>")
                if stufe.basis.tp: stufen_str.append(f"+{stufe.basis.tp} TP")
                if stufe.zauber: stufen_str.append(f"+{stufe.zauber} Zauberslots")
                if stufe.ability: stufen_str.append(f"Gfs-Fähigkeit {stufe.ability.name}")

                stufenbelohnung.append(f"Stufe {stufe.basis.stufe} gibt: " + ", ".join(stufen_str))

        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')

        return {
            **context,
            "topic": "Verteilungshub",
            'char': char,
            "is_done": self.is_done(),
            "vorteile": RelVorteil.objects.filter(char=char, will_create=True),
            "stufenbelohnung": stufenbelohnung,
            "MA_aktuell": rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp,
            "app_index": char.name,
            "app_index_url": reverse("character:show", args=[char.id]),
        }


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        
        # add messages from ep-stufe distribution
        char = self.get_character()
        if "campaign" in char.processing_notes:
            for msg in char.processing_notes["campaign"]:
                messages.error(request, msg)
        
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        if not self.is_done():
            messages.error(request, "Du hast noch nicht alle nötigen Werte verteilt")
            return redirect(request.build_absolute_uri())
        
        char = self.get_character()
        char.submit_stufenhub()

        return redirect(reverse("character:show", args=[char.id]))


class HubAttributeView(CampaignMixin, GenericAttributView):
    pass

class HubFertigkeitenView(CampaignMixin, GenericFertigkeitView):
    pass

class HubZauberView(CampaignMixin, GenericZauberView):
    pass



class HubPersonalView(CampaignMixin, GenericPersonalView):
    pass



class HubVorteileView(CampaignMixin, GenericVorteilView):
    pass


class HubNachteileView(CampaignMixin, GenericNachteilView):
    pass


class HubSpFwFView(CampaignMixin, GenericSpF_wFView):
    pass


class HubTalentView(CampaignMixin, GenericTalentView):
    pass


class HubWesenkraftView(CampaignMixin, GenericWesenkraftView):
    pass


class HubAffektivitätView(CampaignMixin, AffektivitätView):
    pass
