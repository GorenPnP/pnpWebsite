from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse

from character.models import Charakter, Spieler


class LevelUpMixin(LoginRequiredMixin, UserPassesTestMixin):
    # let only owner and spielleiter access
    def test_func(self) -> bool:
        char = self.get_character()

        if self.request.user.groups.filter(name="spielleiter").exists(): return True
        if not hasattr(char, "eigentümer"): return False

        spieler = get_object_or_404(Spieler, name=self.request.user.username)
        return char.eigentümer == spieler
    

    def get_character(self) -> Charakter:
        try:
            return get_object_or_404(Charakter, pk=self.kwargs.get("pk"))
        except: return None


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        return super().get_context_data(*args, **kwargs,
            back_url = reverse("levelUp:index", args=[char.id]),

            char = char,
            app_index = (char.name if char.name else "<no name>") + " - Hub",
            app_index_url = reverse("levelUp:index", args=[char.id])
        )
    
    def get(self, request, *args, **kwargs):
        is_eigentümer = self.request.user.username == self.get_character().eigentümer.name
        if not is_eigentümer:
            messages.warning(self.request, "Dir gehört der Charakter nicht, als Spielleiter kannst du ihn aber bearbeiten")

        return super().get(request, *args, **kwargs)