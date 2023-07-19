from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from character.models import Charakter
from log.create_log import logAuswertung
from ppServer.mixins import SpielleiterOnlyMixin

from .forms import AuswertungForm, LarpAuswertungForm


class AuswertungListView(LoginRequiredMixin, SpielleiterOnlyMixin, ListView):
    model = Charakter
    template_name = "campaign/auswertung_hub.html"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()\
            .prefetch_related("eigentümer")\
            .exclude(eigentümer=None)\
            .exclude(in_erstellung=True)\
            .order_by("name")
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Auswertung",
            app_index = "Charaktere",
            app_index_url = reverse("character:index"),
        )


class AuswertungView(LoginRequiredMixin, SpielleiterOnlyMixin, DetailView):
    model = Charakter
    template_name = "campaign/auswertung.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            **kwargs,
            app_index = "Auswertung",
            app_index_url = reverse("campaign:auswertung_hub"),
        )
        context["form"] = LarpAuswertungForm() if context["object"].larp else AuswertungForm()
        context["topic"] = 'Auswertung für ' + context["object"].name

        return context
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if (self.get_object().eigentümer == None or self.get_object().in_erstellung == True):
            return redirect("campaign:auswertung_hub")

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        form = LarpAuswertungForm(request.POST) if object.larp else AuswertungForm(request.POST)
        form.full_clean()
        if form.is_valid():
            fields = {**form.cleaned_data}
            story = fields["story"]
            del fields["story"]

            if hasattr(fields, "zauberplätze") and fields["zauberplätze"]:
                for stufe, amount in fields["zauberplätze"].items():
                    print(type(stufe), stufe, type(amount), amount)
                    if not object.zauberplätze: object.zauberplätze = {}

                    old_val = object.zauberplätze[stufe] if hasattr(object.zauberplätze, stufe) else 0
                    object.zauberplätze[stufe] = old_val + amount

                object.save(update_fields=["zauberplätze"])
                del fields["zauberplätze"]

            for k, v in fields.items():
                old_value = getattr(object, k)
                setattr(object, k, old_value + v)

            object.save(update_fields=fields)
            logAuswertung(object.eigentümer, object, story, fields)

            # check ep for new stufe
            object.init_stufenhub()

            return redirect("campaign:auswertung_hub")

        return redirect(request.build_absolute_uri())
