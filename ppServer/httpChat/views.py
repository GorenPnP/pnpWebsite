from typing import Any, Dict

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from ppServer.mixins import VerifiedAccountMixin, OwnChatMixin

from .models import *

class AccountListView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):
    template_name = "httpChat/account_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        spieler = Spieler.objects.get(name=self.request.user.username)
        accounts = Account.objects.filter(spieler=spieler).order_by("name")

        return super().get_context_data(**kwargs, accounts=accounts)


class ChatroomListView(LoginRequiredMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        return super().get_context_data(**kwargs, account=account, chatrooms=Chatroom.objects.filter(
            Q(owners__id=account.id) |
            Q(admins__id=account.id) |
            Q(basic_users__id=account.id)
        ).distinct())


class ChatroomView(LoginRequiredMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom.html"

    def get_objects(self):
        return {
            "account": Account.objects.get(slug=self.kwargs["account_name"]),
            "chatroom": Chatroom.objects.get(id=self.kwargs["room_id"])
        }


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        objects = self.get_objects()

        return super().get_context_data(**kwargs,
            topic=objects["chatroom"].titel,
            **objects
        )

    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        # create new message
        objects = self.get_objects()
        text = request.POST.get("message-text")
        if text:
            Message.objects.create(
                text=text,
                author=objects["account"],
                chatroom=objects["chatroom"],
                type=Message.choices[0][0]
            )

        # redirect to chatroom
        return redirect(request.build_absolute_uri())
