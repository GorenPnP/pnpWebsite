from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect



class VerifiedAccountMixin(UserPassesTestMixin):
    def test_func(self) -> Optional[bool]:
        return self.request.user.groups.all().exists()
    
    def handle_no_permission(self):
        return redirect("base:index")


class SpielleiterOnlyMixin(UserPassesTestMixin):
    redirect_to="base:index"

    def test_func(self) -> Optional[bool]:
         return self.request.user.groups.filter(name="spielleiter").exists()
    
    def handle_no_permission(self):
        return redirect(self.redirect_to)