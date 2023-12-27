from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views.generic import DetailView
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from django.urls import reverse

from character.models import Spieler

from .models import *


class GeschöpfIndexView(LoginRequiredMixin, ListView):
    model = Geschöpf
    template_name = "dex/geschöpf_index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "PIA-Archiv",
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )


class GeschöpfDetailView(LoginRequiredMixin, DetailView):
    model = Geschöpf
    template_name = "dex/geschöpf_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "PIA-Archiv",
            app_index_url = reverse("dex:geschöpf_index"),
        )
        context["topic"] = f"#{context['object'].number} {context['object'].name}"

        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        context["visible"] = context["object"].visible.filter(id=spieler.id).exists()
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("initiative", "schadensWI", "geschöpffertigkeit_set__fertigkeit", "visible")