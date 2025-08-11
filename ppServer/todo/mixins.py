from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class TODOPersonMixin(UserPassesTestMixin):
    redirect_to="base:index"

    def test_func(self) -> Optional[bool]:
        return "TODO-Kalender" in self.request.spieler.groups
    
    def handle_no_permission(self):
        return redirect(self.redirect_to)