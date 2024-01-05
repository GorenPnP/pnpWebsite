from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateView

from ppServer.mixins import SpielleiterOnlyMixin

from .forms import MonsterVisibilityForm, AttackToMonsterForm
from .models import *


class MonsterVisibilityView(LoginRequiredMixin, SpielleiterOnlyMixin, TemplateView):
    template_name = "dex/sp/visibility.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs, form=MonsterVisibilityForm())
    
    def post(self, request):
        form = MonsterVisibilityForm(request.POST)
        form.full_clean()
        if form.is_valid():
            spieler_ids = [sp.id for sp in form.cleaned_data["spieler"]]
            visible = form.cleaned_data["visible"]

            for monster in Monster.objects.filter(id__in=form.cleaned_data["monster"]):
                for spieler_id in spieler_ids:
                    monster.visible.add(spieler_id) if visible else monster.visible.remove(spieler_id)
            
            messages.success(request, f"{len(form.cleaned_data['monster'])} Monster bei {len(spieler_ids)} Spieler/n")
        else:
            messages.error(request, "Some error occured")

        return redirect(request.build_absolute_uri())


class AttackToMonsterView(LoginRequiredMixin, SpielleiterOnlyMixin, TemplateView):
    template_name = "dex/sp/attack_to_monster.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        attack = Attacke.objects.load_card().get(pk=self.kwargs["pk"])
        return super().get_context_data(**kwargs, object=attack, form=AttackToMonsterForm(initial={"monster": attack.monster_set.all().values_list("pk", flat=True), "monster_feddich": attack.monster_feddich}))
    
    def post(self, request, pk: int, **kwargs):
        attack = get_object_or_404(Attacke, pk=pk)
        form = AttackToMonsterForm(request.POST)

        form.full_clean()
        if form.is_valid():
            attack.monster_feddich = form.cleaned_data["monster_feddich"]
            attack.save(update_fields=["monster_feddich"])

            attack.monster_set.clear()
            attack.monster_set.add(*form.cleaned_data["monster"].values_list("pk", flat=True))
            
            messages.success(request, "Änderungen wurden gespeichert")
        else:
            messages.error(request, "Some error occured")

        return redirect(request.build_absolute_uri())