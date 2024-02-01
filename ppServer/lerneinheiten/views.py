from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.shortcuts import reverse, get_object_or_404

from ppServer.mixins import VerifiedAccountMixin

from .models import *


class IndexView(LoginRequiredMixin, VerifiedAccountMixin, ListView):
    model = Einheit
    template_name = "lerneinheiten/spieler/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "LARP",
            # app_index = "Charaktere",
            # app_index_url = reverse("character:index"),
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("page_set", "fach")


class PageView(LoginRequiredMixin, VerifiedAccountMixin, DetailView):
    model = Page
    template_name = "lerneinheiten/spieler/page/_default.html"

    def get_template_names(self) -> list[str]:
        return [f"lerneinheiten/spieler/page/{self.object.get_type_display().lower()}.html"] + super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "LARP",
            app_index_url = reverse("lerneinheiten:index"),
        )
        context["topic"] = context["object"].__str__()

        return context
