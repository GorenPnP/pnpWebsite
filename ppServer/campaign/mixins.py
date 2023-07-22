from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse

from character.models import Charakter, Spieler


class CampaignMixin(UserPassesTestMixin):
    app_index = "Verteilungshub"

    def test_func(self) -> bool:
        char = self.get_character()
        return char.ep_stufe != char.ep_stufe_in_progress
        

    def get_character(self):
        return get_object_or_404(Charakter, id=self.kwargs["pk"])
    
    def get_app_index_url(self):
        return reverse("campaign:hub", args=[self.get_character().id])
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["back_url"] = reverse("campaign:hub", args=[context["char"].id])
        return context
    
    def get(self, request, *args, **kwargs):
        is_eigentümer = self.request.user.username == self.get_character().eigentümer.name
        if not is_eigentümer:
            messages.warning(self.request, "Dir gehört der Charakter nicht, als Spielleiter kannst du dir ihn aber bearbeiten")

        return super().get(request, *args, **kwargs)


class OwnCharakterMixin(UserPassesTestMixin):
    # let only owner and spielleiter access
    def test_func(self) -> bool:
        if self.request.user.groups.filter(name="spielleiter").exists(): return True

        char = self.get_character()
        if not hasattr(char, "eigentümer"): return False

        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        return char.eigentümer == spieler
    
    def get_character(self) -> Charakter:
        return super().get_character()