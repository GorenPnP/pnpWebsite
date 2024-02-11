import os

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.http.response import FileResponse
from django.shortcuts import redirect
from django.views.generic import DetailView

from ppServer.decorators import spielleiter_only
from ppServer.mixins import VerifiedAccountMixin
from ppServer.settings import STATIC_ROOT
from character.models import Charakter

from .export import CharakterExporter


class CharacterExportView(LoginRequiredMixin, VerifiedAccountMixin, UserPassesTestMixin, DetailView):
    model = Charakter

    def test_func(self):
        return self.request.spieler.is_spielleiter or Charakter.objects.filter(pk=self.kwargs["pk"], eigentümer=self.request.spieler.instance).exists()

    def handle_no_permission(self):
        return redirect("character:index")

    def get_object(self, *args, **kwargs) -> Charakter:
        return Charakter.objects.prefetch_related(
            "eigentümer", "gfs__gfsstufenplan_set__basis", "relpersönlichkeit_set",
            "beruf", "religion", "relattribut_set", "relfertigkeit_set",
            "affektivität_set", "releinbauten_set__item", "relausrüstung_technik_set__item",
            "relschusswaffen_set__item", "relwaffen_werkzeuge_set__item", "relitem_set__item",
            "relwesenkraft_set__wesenkraft", "reltalent_set__talent", "relrituale_runen_set__item", "relzauber_set__item"
        ).get(pk=self.kwargs["pk"])

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return CharakterExporter(self.get_object()).export()


@login_required
@spielleiter_only(redirect_to="character:index")
def export_all(request, *args, **kwargs):
    try:
        path = os.path.join(STATIC_ROOT, "character_export", "characters.zip")
        return FileResponse(open(path, 'rb'), as_attachment=True)
    except:
        messages.error(request, "Konnte das .zip-file nicht finden. Versuch es in 5 Minuten nochmal")
        return redirect("character:index")
