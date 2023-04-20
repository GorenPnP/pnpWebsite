import json
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.detail import DetailView

from character.models import Spieler
from ppServer.mixins import VerifiedAccountMixin, PollAllowedMixin

from .models import Choice, Question

class PollView(LoginRequiredMixin, PollAllowedMixin, DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic = "Abstimmung")


    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        question = Question.objects.get(pk=pk)
        choice_ids = [int(a) for a in request.POST.getlist("answer")]
        choices = question.choice_set.filter(id__in=choice_ids).distinct()


        # check validity
        if choices.count() != len(set(choice_ids)):
            messages.error(request, "Bitte nochmal versuchen. Die Antworten sind nicht ganz richtig angekommen.")

        elif not question.allow_multiple_selection and len(set(choice_ids)) != question.anz_stimmen:
            messages.error(request, "Mehrfachwahl ist nicht erlaubt")

        elif question.allow_multiple_selection and len(choice_ids) != question.anz_stimmen:
            messages.error(request, "Bitte wähle alle Felder aus")


        #### all fine or not? ####
        if len(messages.get_messages(request)):
            return redirect(request.build_absolute_uri())


        # save to db
        spieler = get_object_or_404(Spieler, name=request.user.username)
        question.spieler_voted.add(spieler)
        
        choices_array = []
        for choice in choices:
            choice.votes += choice_ids.count(choice.id)
            choices_array.append(choice)
        Choice.objects.bulk_update(choices_array, ["votes"])


        # return response
        if question.show_result_to_user:
            return redirect(reverse("polls:results", args=[pk]))
        return redirect("base:index")


class ResultView(LoginRequiredMixin, VerifiedAccountMixin, DetailView):
    model = Question
    template_name = "polls/result.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs, topic = "Ergebnis")
