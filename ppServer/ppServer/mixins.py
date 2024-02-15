from datetime import datetime
from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from httpChat.models import Account, Chatroom
from polls.models import Question, QuestionSpieler


class VerifiedAccountMixin(UserPassesTestMixin):
    def test_func(self) -> Optional[bool]:
        return self.request.spieler.is_verified
    
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
        return self.request.spieler.is_spielleiter
    
    def handle_no_permission(self):
        return redirect(self.redirect_to)
    
class OwnChatMixin(UserPassesTestMixin):
    redirect_to="httpchat:index"

    def test_func(self) -> Optional[bool]:
        account_slug = self.request.resolver_match.kwargs.get("account_name")
        chatroom_id = self.request.resolver_match.kwargs.get("room_id")
        spieler = self.request.spieler.instance
        account = Account.objects.filter(slug=account_slug, spieler=spieler)

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
            pub_date__lte=datetime.now(),
            deadline__gte=datetime.now()
        ).exists() and not\
        QuestionSpieler.objects.filter(
            question__id=pk, spieler=self.request.spieler.instance
        ).exists()

    def handle_no_permission(self):
        return redirect("base:index")
