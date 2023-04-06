from typing import Any, Dict

from django.db.models import F, Subquery, OuterRef, Value, Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View

from ppServer.mixins import VerifiedAccountMixin, OwnChatMixin

from .forms import AccountForm, ChatroomForm
from .models import *

class AccountListView(LoginRequiredMixin, VerifiedAccountMixin, TemplateView):
    template_name = "httpChat/account_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        spieler = Spieler.objects.get(name=self.request.user.username)

        return super().get_context_data(**kwargs, form=AccountForm(), accounts=Account.objects
            .filter(spieler=spieler)
            .order_by("name")
            .prefetch_related("chatroom_set", "chatroom_set__message_set")
            .annotate(
                new_messages = Count("chatroom__message", distinct=True, filter=
                    ~Q(chatroom__message__author__id=F("id")) &         # .exclude(author=account)
                    Q(chatroom__message__type="m") &                    # type is a written message, no info or sth.
                    Q(chatroom__message__created_at__gte=Subquery(    # message that is younger than the last time the account opened the chatroom
                        ChatroomAccount.objects.filter(account__id=OuterRef("id"), chatroom=OuterRef("chatroom"))[:1].values("latest_access")
                    ))
                )
            )
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        spieler = Spieler.objects.get(name=request.user.username)

        account = Account(spieler=spieler)
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()

        # redirect to self.get()
        return redirect(request.build_absolute_uri())


class ChatroomListView(LoginRequiredMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        return super().get_context_data(**kwargs, account=account, form=ChatroomForm(exclude_account=account),
            chatrooms=Chatroom.objects
                .prefetch_related("accounts", "message_set")
                .filter(accounts__id=account.id)
                .annotate(
                    new_messages = Count("message", distinct=True, filter=
                        ~Q(message__author=account) &           # .exclude(author=account)
                        Q(message__type="m") &                  # type is a written message, no info or sth.
                        Q(message__created_at__gte=Subquery(    # message that is younger than the last time the account opened the chatroom
                            ChatroomAccount.objects.filter(account=account, chatroom__id=OuterRef("id"))[:1].values("latest_access")
                        ))
                    )
                )
        )
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        form = ChatroomForm(account, request.POST)
        if form.is_valid():
            accounts_M2M = list(form.cleaned_data['accounts'])
            form.cleaned_data['accounts'] = accounts_M2M + [account]
            form.save()

        # redirect to self.get()
        return redirect(request.build_absolute_uri())


class ChatroomView(LoginRequiredMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom.html"

    def get_objects(self):
        return {
            "account": Account.objects.get(slug=self.kwargs["account_name"]),
            "chatroom": Chatroom.objects.get(id=self.kwargs["room_id"]),
            "chatroomaccount": ChatroomAccount.objects.get(
                account__slug=self.kwargs["account_name"],
                chatroom__id=self.kwargs["room_id"]
            )
        }


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        objects = self.get_objects()

        return super().get_context_data(**kwargs,
            latest_access=self.latest_access,
            **objects,
        )
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        objects = self.get_objects()
        self.latest_access = objects["chatroomaccount"].latest_access
        objects["chatroomaccount"].set_accessed()

        # if opening chatroom for the first time, add welcome msg
        if self.latest_access.year == ancient_datetime().year:
            Message.objects.create(
                type = Message.choices[1][0],   # info
                text = f"{objects['account'].name} joined",
                author = objects['account'],
                chatroom = objects["chatroom"]
            )

        return super().get(request, *args, **kwargs)

    
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


class PollNewMessagesRestView(LoginRequiredMixin, OwnChatMixin, View):

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        res = Chatroom.objects.get(id=self.kwargs["room_id"]).message_set.filter(Q(created_at__gte=Subquery(
                ChatroomAccount.objects
                    .filter(account__slug=self.kwargs["account_name"], chatroom__id=self.kwargs["room_id"])[:1]
                    .values("latest_access")
        ))).exists()

        return JsonResponse({"new_messages": res})
