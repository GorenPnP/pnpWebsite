from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import *

@login_required
def index(request):
    context = {
        "topic": "Goren News",
        "news": News.objects.filter(published=True)
    }

    return render(request, "news/index.html", context)
