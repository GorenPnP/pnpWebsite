from typing import Any, Dict

from django import forms
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, F, Q, Count
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.urls import reverse
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


class VoteOnLegalActFormview(VerifiedAccountMixin, SpielleiterOnlyMixin, DetailView):
    template_name = "politics/admin/vote_on_legalAct.html"
    model = LegalAct

    class LegalActForm(forms.ModelForm):
        class Meta:
            model = LegalAct
            fields = ["code", "paragraph", "text", "voting_done"]
            widgets = {
                "text": forms.widgets.Textarea,
            }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.object = get_object_or_404(self.model, pk=self.kwargs["pk"])
        return super().get_context_data(
            **kwargs,
            subtitle = self.object,
            title = self.model._meta.verbose_name + " ändern",
            original = self.object,
            opts = self.model._meta,
            add = False,
            change = True,
            is_popup = False,
            save_as = False,
            has_add_permission = self.request.user.has_perm(f"{self.model._meta.app_label}.add_{self.model._meta.model_name}"),
            has_change_permission = self.request.user.has_perm(f"{self.model._meta.app_label}.change_{self.model._meta.model_name}"),
            has_delete_permission = self.request.user.has_perm(f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}"),
            has_view_permission = self.request.user.has_perm(f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"),
            has_editable_inline_admin_formsets = False,
            user = self.request.user,

            parties = [p.serialize() for p in Party.objects.all()],
            votes = [v.serialize(populate_politician=True) for v in self.object.politicianvote_set.all().prefetch_related("politician")],
        )

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(form=self.LegalActForm(instance=self.get_object())))

    def post(self, request, **kwargs):
        self.object = get_object_or_404(self.model, pk=self.kwargs["pk"])

        # handle legalact-form
        form = self.LegalActForm(request.POST, instance=self.object)
        form.full_clean()
        if not form.is_valid(): return render(request, self.template_name, self.get_context_data(form=form))

        # handle votes
        votes_per_politician = {int(key.replace("politician-", "")): request.POST.get(key) for key in request.POST.keys() if key.startswith("politician-")}
        
        choices = [v for v, _ in PoliticianVote.VOTE_ENUM]
        votes_per_choice = {choice: set() for choice in choices}
        for politician_id, vote in votes_per_politician.items():
            # vote has to be one of y, n, e, a
            if vote not in choices:
                form.add_error(None, _("Some votes have incorrect values"))
                break
            votes_per_choice[vote].add(politician_id)


        # politicians all exist and are the right ones
        all_politician_ids = set(votes_per_politician.keys())
        if PoliticianVote.objects.filter(legal_act=self.object.id, politician__id__in=all_politician_ids).count() != len(all_politician_ids):
            form.add_error(None, _("Received incorrect votes"))


        # update valid form
        form.save()
        # update object's admin-history
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(self.model).pk,
            object_id=self.object.id,
            object_repr=self.object.__str__(),
            action_flag=CHANGE,
            change_message=(", ".join(form.changed_data) or "Nichts") + "  geändert. (Abstimmungen nicht aufgeführt)"
        )


        # update votes if all valid
        if not form.is_valid(): return render(request, self.template_name, self.get_context_data(form=form))
        for vote, politicians in votes_per_choice.items():
            PoliticianVote.objects.filter(legal_act=self.object, politician__in=politicians).update(vote=vote)

        # redirect afterwards
        what_now = [key for key in request.POST.keys() if key.startswith("_")][0]
        base = f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}'
        if what_now == "_save":
            return redirect(f'{base}_changelist')
        if what_now == "_addanother":
            return redirect(f'{base}_add')
        if what_now == "_continue":
            return redirect(reverse(f'{base}_change', args=[self.object.id]))


class PlenumOverview(VerifiedAccountMixin, TemplateView):
    template_name = "politics/plenum.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Party.objects.prefetch_related("politician_set")\
            .annotate(
                politician_count=Count(F("politician"), filter=Q(politician__member_of_parliament=True)),
            )\
            .order_by("-politician_count", "name")
    
    def get_legalAct_queryset(self) -> list:
        qs = LegalAct.objects.all()\
            .prefetch_related(
                Prefetch("votes", queryset=Politician.objects.filter(member_of_parliament=True))
            )
        
        serialized_acts = []
        for act in qs:
            votes = [{"vote": vote.vote, **vote.politician.serialize()} for vote in act.politicianvote_set.prefetch_related("politician__party").filter(politician__member_of_parliament=True)]
            serialized_acts.append({
                "label": f"act_{act.id}",
                **act.serialize(),
                "votes": votes
            })
        return serialized_acts


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        plenum = [pol.serialize() for pol in Politician.objects.prefetch_related("party").filter(member_of_parliament=True)]

        return super().get_context_data(
            **kwargs,
            topic = "Apaxus' Abstimmungen",
            app_index = "Politik",
            parties = [{**p.serialize(), "politician_count": p.politician_count} for p in self.get_queryset()],
            plenum = plenum,
            legalActs = self.get_legalAct_queryset(),
            app_index_url = '',
            plus = 'Parteiprogramme',
            plus_url = reverse("politics:party-programs"),
        )


class ProgramsListview(VerifiedAccountMixin, ListView):
    template_name = "politics/party_program.html"
    model = Party

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            **kwargs,
            topic = "Wahlprogramme",
            app_index = "Politik",
            app_index_url = reverse("politics:plenum"),
        )