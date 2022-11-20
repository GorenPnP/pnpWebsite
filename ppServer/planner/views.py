from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from datetime import date, timedelta

from character.models import Spieler

from .models import *
from .forms import ProposalForm


days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

def get_1st_day_of_next_month(date_in_month: date):
    next_month = (date_in_month.month + 1) % 12
    next_year = date_in_month.year

    if next_month == 0: next_month = 12
    if next_month == 1: next_year += 1

    return date(next_year, next_month, 1)


def get_month(date_in_month: date):
    this_month = date_in_month.month
    this_year = date_in_month.year

    next_month_day = get_1st_day_of_next_month(date_in_month)

    return {
        "month_name": months[date_in_month.month-1],
        "month": date_in_month.month,
        "year": date_in_month.year,
        "first_weekday": date(this_year, this_month, 1).weekday(),
        "last_day": (next_month_day - timedelta(days=1)).day
    }


@login_required
def index(request):

    if request.method == "POST":
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            
            proposal.player = request.user
            
            chosen_date, created = Day.objects.get_or_create(date=request.POST["date"])
            proposal.day = chosen_date
            
            prev_player = chosen_date.proposal_set.order_by("-order").first()
            proposal.order = prev_player.order+1 if prev_player else 1
            proposal.save()

        return redirect("planner:index")


    today = date.today()
    
    day_in_next_month = get_1st_day_of_next_month(today)
    day_in_far_month = get_1st_day_of_next_month(day_in_next_month)

    context = {
        "topic": "Terminplaner",
        "weekdays": days,
        "today": today,
        "this_month": get_month(today),
        "next_month": get_month(day_in_next_month),
        "far_month":  get_month(day_in_far_month),
        "days": [day.to_dict() for day in Day.objects.filter(date__gte=today)],

        "form": ProposalForm()
    }

    return render(request, "planner/index.html", context)
