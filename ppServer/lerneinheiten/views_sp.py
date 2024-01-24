from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from character.models import Charakter
from log.create_log import logAuswertung
from ppServer.mixins import SpielleiterOnlyMixin

from .models import *

class EditorIndexView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
    model = Einheit
    template_name = "lerneinheiten/sp/editor_index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Editor",
            # app_index = "Charaktere",
            # app_index_url = reverse("character:index"),
        )

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("seite_set")

class EditorPageView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
    model = Page
    template_name = "lerneinheiten/sp/editor_page.html"