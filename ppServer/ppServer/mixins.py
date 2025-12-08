from datetime import datetime
from typing import Optional

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from character.models import CustomPermission
from httpChat.models import Account, Chatroom
from polls.models import Question, QuestionSpieler

class _PermissionMixin(UserPassesTestMixin):
    permissions: list[str] = []
    redirect_to="base:index"

    def test_func(self) -> Optional[bool]:
        return self.request.user.has_perms(self.permissions)
    
    def handle_no_permission(self):
        return redirect(self.redirect_to)


class VerifiedAccountMixin(LoginRequiredMixin):
    pass

class SpielleitungOnlyMixin(_PermissionMixin):
    permissions = [CustomPermission.SPIELLEITUNG.value]

class LARPlerOnlyMixin(_PermissionMixin):
    permissions = [CustomPermission.LARP.value]

class CopiesCharsMixin(_PermissionMixin):
    permissions = [CustomPermission.COPY_CHARS.value]

class TODOPersonMixin(_PermissionMixin):
    permissions = [CustomPermission.SEES_CALENDAR.value]

class OwnChatMixin(UserPassesTestMixin):
    redirect_to="httpchat:index"

    def test_func(self) -> Optional[bool]:
        account_slug = self.request.resolver_match.kwargs.get("account_name")
        chatroom_id = self.request.resolver_match.kwargs.get("room_id")
        spieler = self.request.spieler
        account = get_object_or_404(Account, slug=account_slug, spieler=spieler)    # should be exactly one

        if not chatroom_id: return True

        return Chatroom.objects.filter(id=chatroom_id, accounts__exact=account).exists()

    def handle_no_permission(self):
        return redirect(self.redirect_to)
    

class PollAllowedMixin(UserPassesTestMixin):
    redirect_to = "base:index"

    def test_func(self) -> Optional[bool]:
        pk = self.request.resolver_match.kwargs["pk"]

        return Question.objects\
            .filter(
                pk=pk,
                pub_date__lte=datetime.now(),
                deadline__gte=datetime.now()
            ).exists() and not\
            QuestionSpieler.objects.filter(
                question__id=pk, spieler=self.request.spieler
            ).exists()

    def handle_no_permission(self):
        return redirect(self.redirect_to)
