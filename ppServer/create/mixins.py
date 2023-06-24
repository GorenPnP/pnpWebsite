from django.http import HttpResponseNotFound
from django.urls import reverse

from character.models import Charakter

from .decorators import get_own_charakter

class CreateMixin:
    app_index = "Erstellung"
    app_index_url = "create:gfs"

    def get_character(self) -> Charakter:
        char, err = get_own_charakter(self.request)
        if err: return HttpResponseNotFound()

        return char

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, **kwargs, back_url = reverse("create:landing_page"))
