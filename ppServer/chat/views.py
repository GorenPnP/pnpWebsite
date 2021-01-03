from ppServer.decorators import verified_account
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect, render

from .models import Message


@login_required
@verified_account
def index(request):
    if request.user.groups.filter(name__iexact="spielleiter").exists():
        return sp_index(request)

    context = {"messages": Message.objects.all()}
    return render(request, 'chat/index.html', context)


@login_required
# @spielleiter_only     <-- breaks
def sp_index(request):

    if not request.user.groups.filter(name__iexact="spielleiter").exists():
        return redirect("chat:index")

    context = {"messages": Message.objects.all()}
    return render(request, 'chat/sp_index.html', context)
