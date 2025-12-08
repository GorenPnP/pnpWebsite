from datetime import datetime
from typing import Any, Dict

from django.db.models import Subquery, OuterRef, Q
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.urls import reverse

from ppServer.mixins import VerifiedAccountMixin, OwnChatMixin

from .forms import AccountForm, ChatroomForm
from .models import *
from .signals import send_webpush

class AccountListView(VerifiedAccountMixin, TemplateView):
    template_name = "httpChat/account_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        spieler = self.request.spieler

        return super().get_context_data(**kwargs,
            form=AccountForm(),
            accounts=Account.objects
                .load_unread_messages()
                .prefetch_related("spieler")
                .filter(spieler=spieler)
                .order_by("-unread_messages", "name"),
            topic="Meine Chats"
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        spieler = request.spieler

        account = Account(spieler=spieler)
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()

        # redirect to self.get()
        return redirect(request.build_absolute_uri())


class ChatroomListView(VerifiedAccountMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        return super().get_context_data(**kwargs,
            account=account,
            new_chat_form=ChatroomForm(exclude_account=account, prefix="create-chat"),
            edit_account_form=AccountForm(instance=account, prefix="update-account"),
            chatrooms=Chatroom.objects
                .load_title(account)
                .prefetch_related("accounts", "message_set")
                .filter(accounts__id=account.id)
                .annotate(
                    unread_messages = Subquery(ChatroomAccount.objects\
                        .load_unread_messages()\
                        .filter(account=account, chatroom__id=OuterRef("id"))\
                        .values_list("unread_messages", flat=True)[:1]
                    ),
                )
                .order_by("-unread_messages", "final_title", "accounts"),
            app_index="Chat",
            app_index_url=reverse("httpchat:index")
        )
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        account = Account.objects.get(slug=self.kwargs["account_name"])

        create_chat_form = ChatroomForm(account, request.POST, prefix="create-chat")
        if create_chat_form.is_valid():
            accounts_M2M = list(create_chat_form.cleaned_data['accounts'])
            create_chat_form.cleaned_data['accounts'] = accounts_M2M + [account]
            create_chat_form.save()

        update_account_form = AccountForm(request.POST, request.FILES, instance=account, prefix="update-account")
        if update_account_form.is_valid():
            update_account_form.save()

        # redirect to self.get()
        return redirect(request.build_absolute_uri())


class ChatroomView(VerifiedAccountMixin, OwnChatMixin, TemplateView):
    template_name = "httpChat/chatroom.html"

    def get_objects(self):
        account = Account.objects.get(slug=self.kwargs["account_name"])
        return {
            "account": account,
            "chatroom": Chatroom.objects.load_title(account).prefetch_related("message_set__author").get(id=self.kwargs["room_id"]),
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

        # set accessed
        self.latest_access = objects["chatroomaccount"].latest_access
        ChatroomAccount.objects.filter(chatroom=objects["chatroom"], account__spieler=request.spieler).update(latest_access=datetime.now())
        send_webpush(ChatroomAccount, instance=ChatroomAccount.objects.filter(chatroom=objects["chatroom"], account__spieler=request.spieler).first())

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
            now = datetime.now()

            # set message for all own characters in this group to read
            # do this before Message.objects.create triggers WebPushies
            ChatroomAccount.objects.filter(chatroom=objects["chatroom"], account__spieler=objects["account"].spieler).update(latest_access=now)

            # create message object
            Message.objects.create(
                text=text,
                author=objects["account"],
                chatroom=objects["chatroom"],
                type=Message.choices[0][0],
                created_at=now,
            )


        # redirect to chatroom
        return redirect(request.build_absolute_uri())


class PollNewMessagesRestView(VerifiedAccountMixin, OwnChatMixin, View):

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        res = Chatroom.objects.get(id=self.kwargs["room_id"]).message_set.filter(Q(created_at__gte=Subquery(
                ChatroomAccount.objects
                    .filter(account__slug=self.kwargs["account_name"], chatroom__id=self.kwargs["room_id"])[:1]
                    .values("latest_access")
        ))).exists()

        return JsonResponse({"unread_messages": res})
