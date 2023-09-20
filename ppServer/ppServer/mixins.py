from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone

from character.models import Spieler
from httpChat.models import Account, Chatroom
from polls.models import Question, QuestionSpieler


class VerifiedAccountMixin(UserPassesTestMixin):
    def test_func(self) -> Optional[bool]:
        return self.request.user.groups.all().exists()
    
    def handle_no_permission(self):
        return redirect("base:index")
    
    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not request.user.is_authenticated or not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


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
    

class PollAllowedMixin(UserPassesTestMixin):
    def test_func(self) -> Optional[bool]:
        pk = self.request.resolver_match.kwargs["pk"]

        return Question.objects\
        .filter(
            pk=pk,
            pub_date__lte=timezone.now(),
            deadline__gte=timezone.now()
        ).exists() and not\
        QuestionSpieler.objects.filter(
            question__id=pk, spieler__name=self.request.user.username
        ).exists()

    def handle_no_permission(self):
        return redirect("base:index")
