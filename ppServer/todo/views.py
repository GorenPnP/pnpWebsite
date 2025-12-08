import locale, json, re
from datetime import date, datetime, timedelta, timezone

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.base import TemplateView

from planner.views import days, get_1st_day_of_next_month, get_month
from ppServer.decorators import verified_account, TODOperson_only
from ppServer.mixins import VerifiedAccountMixin, TODOPersonMixin

from .forms import CreateCategoryForm, CreateIntervalForm
from .models import *

class CalendarOverview(VerifiedAccountMixin, TODOPersonMixin, TemplateView):
    template_name = "todo/calendar.html"

    def get_context_data(self, **kwargs):
        today = date.today()
    
        day_in_next_month = get_1st_day_of_next_month(today)
        day_in_far_month = get_1st_day_of_next_month(day_in_next_month)

        categories = list(
            {
                "id": cat.id, "name": cat.name, "color": cat.color, "textColor": cat.textColor,
                "intervals": list(cat.timeinterval_set.values("start", "end", "id")),
            } for cat in Category.objects.prefetch_related("timeinterval_set")
        )

        context = {
            "topic": "TODO-Kalender",
            "categories": categories,

            "weekdays": days,
            "today": today,
            "this_month": get_month(today),
            "next_month": get_month(day_in_next_month),
            "far_month":  get_month(day_in_far_month),
        }

        return super().get_context_data(**kwargs, **context)
    
    def get(self, request, *args, **kwargs):
        TimeInterval.objects.filter(end__lt=datetime.now()).delete()

        return super().get(request, *args, **kwargs)

@require_POST
@verified_account
@TODOperson_only()
def add_interval_to_category(request, pk):
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    to_datetime = lambda iso: datetime(*[int(n) for n in re.split(r'[-T:]', iso)], tzinfo=timezone.utc)

    form = CreateIntervalForm({
        **request.POST,
        "category": pk,
        "start": to_datetime(request.POST["start"]),
        "end": to_datetime(request.POST["end"]),
    })
    form.full_clean()
    if not form.is_valid():
        messages.error(request, "Fehler: " + json.dumps(form.errors))
    else:
        form.save()
    return redirect("todo:calendar")


@require_POST
@verified_account
@TODOperson_only()
def add_day_interval(request):
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")

    category = get_object_or_404(Category.objects.prefetch_related("timeinterval_set"), pk=request.POST["category"])
    day_start = datetime(*[int(n) for n in re.split(r'[-T:]', request.POST["day"])], tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1) - timedelta(minutes=1)

    if category.timeinterval_set.filter(start__lte=day_start, end__gte=day_end).exists():
        messages.warning(request, "Den Termin gibt es schon ganztägig!")
        return redirect("todo:calendar")
    
    TimeInterval.objects.create(start=day_start, end=day_end, category=category)
    messages.success(request, "Der Termin wurde angelegt")
    return redirect("todo:calendar")


@require_POST
@verified_account
@TODOperson_only()
def add_category(request):
    form = CreateCategoryForm(request.POST)
    form.full_clean()
    if not form.is_valid():
        messages.error(request, "Fehler: " + json.dumps(form.errors))
    else:
        form.save()
    return redirect("todo:calendar")


@require_GET
@verified_account
@TODOperson_only()
def delete_category(request, pk):
    Category.objects.filter(pk=pk).delete()
    messages.success(request, "Kategorie wurde gelöscht")

    return redirect("todo:calendar")


@require_GET
@verified_account
@TODOperson_only()
def delete_interval(request, pk, day):
    to_datetime = lambda iso: datetime(*[int(n) for n in re.split(r'[-T:]', iso)], tzinfo=timezone.utc)

    interval = get_object_or_404(TimeInterval.objects.prefetch_related("category").all(), pk=pk)

    curr_date = to_datetime(day)
    before = curr_date - timedelta(minutes=1)
    after = curr_date + timedelta(days=1)

    if interval.start <= before: TimeInterval.objects.create(start=interval.start, end=before, category=interval.category)
    if after <= interval.end: TimeInterval.objects.create(start=after, end=interval.end, category=interval.category)
    interval.delete()

    messages.success(request, "Termin wurde gelöscht")

    return redirect("todo:calendar")