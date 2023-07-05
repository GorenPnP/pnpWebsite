from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from character.models import Charakter, Spieler


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
