from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ppServer.mixins import VerifiedAccountMixin

from character.models import Charakter, CustomPermission


class LevelUpMixin(VerifiedAccountMixin, UserPassesTestMixin):
    char = None

    # let only owner and spielleitung access
    def test_func(self) -> bool:
        char = self.get_character()

        if self.request.user.has_perm(CustomPermission.SPIELLEITUNG.value): return True
        if not hasattr(char, "eigentümer"): return False

        spieler = self.request.spieler
        return spieler and char.eigentümer == spieler
    

    def get_character(self, queryset: QuerySet[Charakter] = None) -> Charakter:
        # return already executed default char (the one with an empty queryset)
        if self.char and not queryset and self.char.pk == self.kwargs.get("pk"): return self.char

        # need to query db
        try:
            char = get_object_or_404(queryset or Charakter, pk=self.kwargs.get("pk"))
            # save default char for later calls
            if not queryset: self.char = char

            return char
        except: return None


    def get_context_data(self, *args, **kwargs):
        char = self.get_character()

        return super().get_context_data(*args, **kwargs,
            back_url = reverse("levelUp:index", args=[char.id]),

            char = char,
            app_index = (getattr(char, "name") or "<no name>") + " - Hub",
            app_index_url = reverse("levelUp:index", args=[char.id])
        )
    
    def get(self, request, *args, **kwargs):
        char = self.get_character()
        is_eigentümer = self.request.spieler == char.eigentümer
        if not is_eigentümer:
            messages.warning(self.request, "Dir gehört der Charakter nicht, als Spielleitung kannst du ihn aber bearbeiten")

        return super().get(request, *args, **kwargs)