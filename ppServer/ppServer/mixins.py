from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect

from character.models import Spieler
from httpChat.models import Account, Chatroom

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
    
class OwnChatMixin(UserPassesTestMixin):
    redirect_to="httpchat:index"

    def test_func(self) -> Optional[bool]:
        account_slug = self.request.resolver_match.kwargs.get("account_name")
        chatroom_id = self.request.resolver_match.kwargs.get("room_id")
        spieler = Spieler.objects.get(name=self.request.user.username)
        account =  Account.objects.filter(slug=account_slug, spieler=spieler)

        if not account.exists(): return False
        if not chatroom_id: return True

        account = account[0]
        return Chatroom.objects.filter(id=chatroom_id).filter(accounts__exact=account).exists()

    def handle_no_permission(self):
        return redirect(self.redirect_to)