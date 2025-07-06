from typing import Optional
from urllib.parse import urlencode

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse

from crafting.models import RelCrafting


class ProfileSetMixin(UserPassesTestMixin):
    redirect_to="crafting:index"

    def test_func(self) -> Optional[bool]:
        spieler = self.request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        rel, _ = RelCrafting.objects.prefetch_related("profil").get_or_create(spieler=spieler)
        self.relCrafting = rel

        # no profile active? change that!
        return self.relCrafting.profil is not None and self.relCrafting.char is not None


    def handle_no_permission(self):
        return redirect(f'{reverse(self.redirect_to)}?{urlencode({"redirect": self.request.path})}')
