import json

from django.http import HttpResponseNotFound
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from ppServer.decorators import verified_account, spielleitung_only

from .models import Message


@verified_account
def index(request):

    if request.method == "GET":

        context = {"topic": "Chat"}
        return render(request, 'chat/index.html', context)

    if request.method == "POST":

        json_dict = json.loads(request.body.decode("utf-8"))
        spieler = request.spieler.instance
        if not spieler: return HttpResponseNotFound()

        # typed a new message, need to save it
        if "new_msg" in json_dict.keys():

            new_msg = json_dict["new_msg"].strip()
            if not new_msg: return JsonResponse({}, status=400)

            Message.objects.create(text=new_msg, author=spieler)
            return JsonResponse({})

        # polling for newer messages than timestamp in 'since'
        elif "since" in json_dict.keys():
            since = json_dict["since"]

            messages = Message.objects.filter(created_at__gt=since) if since else Message.objects.all()
            return JsonResponse(
                {
                    "messages":
                        [{"author": m.author.get_real_name(), "text": m.text, "created_at": m.created_at.isoformat()} for m in messages],
                    "own_name": spieler.get_real_name(),
                    "spielleitung": request.spieler.is_spielleitung
                }
            )



@verified_account
@spielleitung_only("chat:index")
def sp_index_get(request):

    context = {
        "topic": "Spielleitung-Chat",
        "messages": Message.objects.all(),
        "own_name": request.spieler.instance.get_real_name(),
        "app_index": "Chats",
        "app_index_url": reverse("chat:index")
    }
    return render(request, 'chat/sp_index.html', context)


@verified_account
def room(request, room_name):
    context = {
        "topic": room_name,
        "room_name": room_name,
        "app_index": "Chats",
        "app_index_url": reverse("chat:index")
    }
    return render(request, 'chat/chatroom.html', context)