from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Subquery, OuterRef, Value, BooleanField
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from .models import *

class MonsterIndexView(LoginRequiredMixin, ListView):
    model = Monster
    template_name = "dex/monster_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Monsterdex",
            types = Typ.objects.all(),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("types", "visible")


class MonsterDetailView(LoginRequiredMixin, DetailView):
    model = Monster
    template_name = "dex/monster_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Monster",
            app_index_url = reverse("dex:monster_index"),
            types = Typ.objects.all(),
            spieler = get_object_or_404(Spieler, name=self.request.user.username)
        )
        context["topic"] = context["object"].name
        
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("types", "visible")
        
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        if spieler not in self.get_object().visible.all():
            return redirect("dex:monster_index")

        return super().get(request, *args, **kwargs)