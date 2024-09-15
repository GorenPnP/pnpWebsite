from typing import Any, Dict

from django import forms
from django.db.models import Subquery, OuterRef, CharField, F, Value, Q, Count, Case, When
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _

from ppServer.mixins import SpielleiterOnlyMixin, VerifiedAccountMixin

from .models import *

class AdminDuplicatePoliticiansFormview(VerifiedAccountMixin, SpielleiterOnlyMixin, TemplateView):
    template_name = "politics/admin/action_duplicate_politicians.html"
    model = Politician

    class DuplicationForm(forms.Form):
        times = forms.IntegerField(min_value=1, max_value=1000, initial=1, required=True, label="Wie oft sollen sie vervielfacht werden?")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            title = _(f"Duplicate {self.model._meta.verbose_name_plural}"),
            opts = self.model._meta,
            has_view_permission = self.request.user.has_perm(f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"),
        )

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(form=self.DuplicationForm()))
    
    def post(self, request, **kwargs):
        form = self.DuplicationForm(request.POST)
        form.full_clean()
        if form.is_valid():
            new_objects = []
            for object in self.model.objects.filter(id__in=request.GET.getlist("ids")):
                object.id = None
                for _ in range(form.cleaned_data["times"]):
                    new_objects.append(object)

            self.model.objects.bulk_create(new_objects)
         
            return redirect(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist')
        else:
            return render(request, self.template_name, self.get_context_data(form=form))


class PlenumOverview(VerifiedAccountMixin, SpielleiterOnlyMixin, TemplateView):
    template_name = "politics/plenum.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Party.objects.prefetch_related("politician_set")\
            .annotate(
                politician_count=Count(F("politician")),
                lead_count=Count(F("politician"), Q(politician__is_party_lead=True)),
            )\
            .order_by("-politician_count", "name")
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        parties = [p.serialize() for p in self.get_queryset()]

        return super().get_context_data(
            **kwargs,
            topic = "Apaxus' Plenum",
            app_index = "Politik",
            parties = parties,
            app_index_url = '' #reverse("politics:index"),
        )