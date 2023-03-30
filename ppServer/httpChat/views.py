from typing import Any, Dict

from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from .models import *

class ChatroomListView(TemplateView):
    template_name = "httpchat/chatroom_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        return super().get_context_data(**kwargs, account=account, chatrooms=Chatroom.objects.filter(
            Q(owners__id=account.id) |
            Q(admins__id=account.id) |
            Q(basic_users__id=account.id)
        ).distinct())


# TODO restrict chat to members only
class ChatroomView(TemplateView):
    template_name = "httpchat/chatroom.html"

    def get_objects(self):
        return {
            "account": Account.objects.get(slug=self.kwargs["account_name"]),
            "chatroom": Chatroom.objects.get(slug=self.kwargs["room_name"])
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
