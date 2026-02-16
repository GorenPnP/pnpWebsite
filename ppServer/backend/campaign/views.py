from typing import Any, Dict

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from cards.models import Transaction
from character.models import Charakter
from log.create_log import logAuswertung
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin

from .forms import AuswertungForm, LarpAuswertungForm


class AuswertungListView(VerifiedAccountMixin, SpielleitungOnlyMixin, ListView):
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


class AuswertungView(VerifiedAccountMixin, SpielleitungOnlyMixin, DetailView):
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
        object = self.get_object(queryset=self.model.objects.prefetch_related("card"))
        form = LarpAuswertungForm(request.POST) if object.larp else AuswertungForm(request.POST)
        form.full_clean()
        if form.is_valid():
            fields = {**form.cleaned_data}
            story = fields.pop("story")

            # apply geld
            geld = fields.pop("geld")
            if geld:
                object.card.money += geld
                object.card.save(update_fields=["money"])
                Transaction.objects.create(receiver=object.card, amount=geld, reason=f"Storybelohnung '{story}'")

            # apply zauberplätze
            zauberplätze = fields.pop("zauberplätze", dict()) or dict()
            if zauberplätze.keys():
                for stufe, amount in zauberplätze.items():
                    if not object.zauberplätze: object.zauberplätze = {}

                    old_val = object.zauberplätze[stufe] if hasattr(object.zauberplätze, stufe) else 0
                    object.zauberplätze[stufe] = old_val + amount

                object.save(update_fields=["zauberplätze"])

            # apply all other/numeric fields
            for k, v in fields.items():
                old_value = getattr(object, k)
                setattr(object, k, old_value + v)

            object.save(update_fields=fields)

            zauberplatz_log = ", ".join([f"{amount}x Stufe {stufe}" for stufe, amount in zauberplätze.items() if amount])
            logAuswertung(object.eigentümer, object, story, {**fields, "geld": geld, "zauber": zauberplatz_log})

            # check ep for new stufe
            object.init_stufenhub()

            return redirect("campaign:auswertung_hub")

        return redirect(request.build_absolute_uri())
