import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from character.models import Spieler
from django.views.decorators.http import require_POST

from .models import Choice, Question, QuestionSpieler


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_object(self, queryset=None):
        id_ = self.kwargs.get("pk")
        return self.model.objects.get(id=id_)

    def post(self, request, *args, **kwargs):
        question = self.get_object()

        try:
            choice_ids=json.loads(request.body.decode("utf-8"))["ids"]
        except:
            return JsonResponse({"message": "Daten nicht angekommen"}, status=418)

        if not question.umfrage_läuft():
            return JsonResponse({"message": "Die Umfrage ist nicht zur Abstimmung freigegeben."}, status=418)

        if len(choice_ids) != question.anz_stimmen:
            return JsonResponse({"message": "Falsche Anzahl an choices."}, status=418)

        choices = []
        for id in choice_ids:
            choice = get_object_or_404(Choice, id=id)
            if choice.question.id != question.id:
                return JsonResponse({"message": "Choices.id gehört nicht zu dieser Frage"}, status=418)
            choices.append(choice)

        spieler = get_object_or_404(Spieler, name=request.user.username)
        #if QuestionSpieler.objects.filter(question=question, spieler=spieler).exists():
        #    return JsonResponse({"message": "Bereits über diese Frage abgestimmt"}, status=418)

        # valid since here

        for c in choices:
            c.votes += 1
            c.save()
        QuestionSpieler.objects.get_or_create(spieler=spieler, question=question)

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return JsonResponse({"url": reverse('polls:results', args=(question.id,))})


def results(request, pk):

    spieler = get_object_or_404(Spieler, name=request.user.username)
    now = timezone.now()

    all_answered = [qs.question.id for qs in QuestionSpieler.objects.filter(spieler=spieler)]
    open_questions = Question.objects.filter(pub_date__lte=now, deadline__gte=now).exclude(id__in=all_answered)

    next_url = reverse("polls:detail", args=[open_questions[0].id]) if open_questions.exists() else reverse("base:index")
    context = {
        "question": get_object_or_404(Question, id=pk),
        "next_url": next_url,
    }

    return render(request, 'polls/result.html', context)
