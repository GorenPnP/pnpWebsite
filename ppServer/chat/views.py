import json
from character.models import Spieler
from django.http.response import JsonResponse
from ppServer.decorators import verified_account
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect, render

from .models import Message


@login_required
@verified_account
def index(request):

    if request.method == "GET":

        # if request.user.groups.filter(name__iexact="spielleiter").exists():
        #     return sp_index_get(request)

        context = {"topic": "Chat"}
        return render(request, 'chat/index.html', context)

    if request.method == "POST":

        json_dict = json.loads(request.body.decode("utf-8"))
        spieler = get_object_or_404(Spieler, name=request.user.username)

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
                    "spielleiter": request.user.groups.filter(name__iexact="spielleiter").exists()
                }
            )



@login_required
# @spielleiter_only     <-- breaks
def sp_index_get(request):

    if not request.user.groups.filter(name__iexact="spielleiter").exists():
        return redirect("chat:index")

    context = {
        "topic": "Spielleiter-Chat",
        "messages": Message.objects.all(),
        "own_name": get_object_or_404(Spieler, name=request.user.username).get_real_name()
    }
    return render(request, 'chat/sp_index.html', context)


@login_required
def room(request, room_name):
    context = {"topic": room_name, "room_name": room_name}
    return render(request, 'chat/chatroom.html', context)