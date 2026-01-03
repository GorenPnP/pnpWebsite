from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

from character.models import RelTalent, Talent

from ..decorators import is_erstellung_done
from ..mixins import LevelUpMixin


@method_decorator([is_erstellung_done], name="dispatch")
class GenericTalentView(LevelUpMixin, TemplateView):

    template_name = "levelUp/talent.html"
    

    def get_available_talente(self, char):

        own_talent_ids = [rel.talent.id for rel in RelTalent.objects.prefetch_related("talent").filter(char=char)]
        talente = Talent.objects.prefetch_related("bedingung").filter(tp__lte=char.tp).exclude(id__in=own_talent_ids)

        available_talente = []
        for talent in talente:
            bedingung_ids = [b.id for b in talent.bedingung.all()]

            # test bedingungen
            ok = True
            for b_id in bedingung_ids:
                if b_id not in own_talent_ids:
                    ok = False
                    break

            # add if bedingungen all met
            if ok: available_talente.append(talent)

        return available_talente

    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        return super().get_context_data(*args, **kwargs,
            own_talente = [rel.talent for rel in RelTalent.objects.filter(char=char)],
            talente = self.get_available_talente(char),
            topic = "Talent"
        )


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        char = self.get_character()

        talent_id = request.POST.get("talent_id")
        talent = get_object_or_404(Talent, id=talent_id)
        
        # checks
        if not talent in self.get_available_talente(char):
            messages.error(request, f"Das Talent {talent.titel} hast du bereits oder kannst du nicht lernen.")
            return redirect(request.build_absolute_uri())

        # apply
        char.tp -= talent.tp
        char.save(update_fields=["tp"])

        RelTalent.objects.create(char=char, talent=talent)
        return redirect(request.build_absolute_uri())
