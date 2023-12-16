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
        self.object = context["object"]
        context["topic"] = self.object.name

        return context

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related(
            "types", "visible", "base_schadensWI",
            "evolutionPre__types", "evolutionPre__visible",
            "evolutionPost__types", "evolutionPost__visible",
            "alternativeForms__types", "alternativeForms__visible",
            "opposites__types", "opposites__visible",
            "attacken__types", "attacken__damage", "fähigkeiten"
        )
        
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)    # let self.get_context_data() set self.object to perform the query only once
        
        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        if  not self.object.visible.filter(name=spieler.name).exists():
            return redirect("dex:monster_index")

        return response
    
class AttackIndexView(LoginRequiredMixin, ListView):
    model = Attacke
    template_name = "dex/attack_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Attacken",
            types = Typ.objects.all()
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("types")


class TypeTableView(LoginRequiredMixin, ListView):
    model = Typ
    template_name = "dex/type_table.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Typentabelle"
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("stark_gegen", "schwach_gegen", "trifft_nicht", "stark", "schwach", "miss")


class MonsterFähigkeitView(LoginRequiredMixin, ListView):
    model = MonsterFähigkeit
    template_name = "dex/monster_fähigkeit_index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            app_index = "Allesdex",
            app_index_url = reverse("dex:index"),
            topic = "Fähigkeiten",
            spieler = get_object_or_404(Spieler, name=self.request.user.username),
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related("monster_set__visible", "monster_set__types")