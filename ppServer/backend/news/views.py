from django.shortcuts import render

from ppServer.decorators import verified_account

from .models import *

@verified_account
def index(request):
    context = {
        "topic": "Goren News",
        "news": News.objects.filter(published=True)
    }

    return render(request, "news/index.html", context)
