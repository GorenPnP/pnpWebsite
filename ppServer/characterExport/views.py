import os

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.http.response import FileResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.views.generic import DetailView

from ppServer.decorators import spielleitung_only, verified_account
from ppServer.mixins import VerifiedAccountMixin
from ppServer.settings import STATIC_ROOT
from character.models import Charakter, CustomPermission

from .export import CharakterExporter


class CharacterExportView(VerifiedAccountMixin, UserPassesTestMixin, DetailView):
    model = Charakter

    def test_func(self):
        return self.request.user.has_perm(CustomPermission.SPIELLEITUNG.value) or Charakter.objects.filter(pk=self.kwargs["pk"], eigentümer=self.request.spieler).exists()

    def handle_no_permission(self):
        return redirect("character:index")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return CharakterExporter(self.get_object()).export()


@require_GET
@verified_account
@spielleitung_only(redirect_to="character:index")
def export_all(request, *args, **kwargs):
    try:
        path = os.path.join(STATIC_ROOT, "character_export", "characters.zip")
        return FileResponse(open(path, 'rb'), as_attachment=True)
    except:
        messages.error(request, "Konnte das .zip-file nicht finden. Versuch es in 5 Minuten nochmal")
        return redirect("character:index")
