from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from base.views import reviewable_shop
from ppServer.decorators import spielleiter_only, verified_account


@login_required
@spielleiter_only()
def review_items(request):

    context = {"topic": "Neue Items", "items": reviewable_shop()}

    if not context["items"]:
        return redirect("base:index")

    return render(request, "shop/review_items.html", context)


@login_required
@verified_account
def index(request):
    return render(request, "shop/index.html", {"topic": "Shop"})
