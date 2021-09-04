from ppServer.decorators import verified_account
import json
from django.contrib.auth.decorators import login_required

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone

from character.models import Spieler

from .models import Choice, Question, QuestionSpieler


@login_required
@verified_account
def detail(request, pk):
    question = get_object_or_404(Question, id=pk)
    spieler = get_object_or_404(Spieler, name=request.user.username)
    if QuestionSpieler.objects.filter(question=question, spieler=spieler).count():
        return redirect("base:index")

    if request.method == "GET":
        return render(request, 'polls/detail.html', {"question": question})

    if request.method == "POST":
        question = get_object_or_404(Question, id=pk)

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
        url = reverse('polls:results', args=(question.id,)) if question.show_result_to_user else reverse('base:index')
        return JsonResponse({"url": url})


@login_required
@verified_account
def results(request, pk):
    question = get_object_or_404(Question, id=pk)
    if not question.show_result_to_user:
        return redirect("base:index")

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
