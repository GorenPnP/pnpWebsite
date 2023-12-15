from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from ppServer.mixins import SpielleiterOnlyMixin

from .forms import MonsterVisibilityForm
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

            print(spieler_ids)
            for monster in Monster.objects.filter(id__in=form.cleaned_data["monster"]):
                for spieler_id in spieler_ids:
                    monster.visible.add(spieler_id) if visible else monster.visible.remove(spieler_id)
            
            messages.success(request, f"{len(form.cleaned_data['monster'])} Monster bei {len(spieler_ids)} Spieler/n")
        else:
            messages.error(request, "Some error occured")

        return redirect(request.build_absolute_uri())