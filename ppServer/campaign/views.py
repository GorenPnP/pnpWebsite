import re
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import OuterRef, Value, F, Sum, Exists
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import DetailView

from django_tables2.columns import TemplateColumn

from base.abstract_views import DynamicTableView, GenericTable
from character.models import Charakter, Vorteil, RelVorteil, Spieler, RelAttribut, Attribut, Fertigkeit
from levelUp.decorators import is_ap_done, is_ferts_done, is_personal_done, is_spF_wF_done, is_teil_done, is_zauber_done
from levelUp.views import *
from log.create_log import logAuswertung
from ppServer.mixins import SpielleiterOnlyMixin, VerifiedAccountMixin
from shop.models import Engelsroboter

from .forms import AuswertungForm
from .mixins import CampaignMixin


class AuswertungView(LoginRequiredMixin, SpielleiterOnlyMixin, DetailView):
    model = Charakter

    template_name = "campaign/auswertung.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs, form=AuswertungForm())
        context["topic"] = 'Auswertung für ' + context["object"].name

        return context

    def post(self, request, *args, **kwargs):
        form = AuswertungForm(request.POST)
        form.full_clean()
        if form.is_valid():
            object = self.get_object()
            fields = {**form.cleaned_data}
            story = fields["story"]
            del fields["story"]

            for k, v in fields.items():
                old_value = getattr(object, k)
                setattr(object, k, old_value + v)

            object.save(update_fields=fields)
            logAuswertung(object.eigentümer, object, story, fields)

            # check ep for new stufe
            object.init_stufenhub()

            return redirect("character:show", object.id)

        return redirect(request.build_absolute_uri())


class HubView(LoginRequiredMixin, CampaignMixin, OwnCharakterMixin, DetailView):
    model = Charakter

    template_name = "campaign/hub.html"

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
                if stufe.special_ability: stufen_str.append(f"Gfs-Fähigkeit {stufe.special_ability}")

                stufenbelohnung.append(f"Stufe {stufe.basis.stufe} gibt: " + ", ".join(stufen_str))

        rel_ma = RelAttribut.objects.get(char=char, attribut__titel='MA')
        # TODO
        done_completely =\
            is_ap_done(self.request, char=char) and\
            is_ferts_done(self.request, char=char) and\
            is_zauber_done(self.request, char=char)
            # is_personal_done(self.request, char=char) and\
            # is_spF_wF_done(self.request, char=char) and\
            # is_teil_done(self.request, char=char)

        return {
            **context,
            "topic": "Verteilungshub",
            'char': char,
            "is_done": done_completely,
            "vorteile": RelVorteil.objects.filter(char=char, will_create=True),
            "stufenbelohnung": stufenbelohnung,
            "MA_aktuell": rel_ma.aktuellerWert + rel_ma.aktuellerWert_temp,
            "app_index": char.name,
            "app_index_url": reverse("character:show", args=[char.id]),
        }


# class ApFormView(LoginRequiredMixin, VerifiedAccountMixin, DynamicTableView):
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
