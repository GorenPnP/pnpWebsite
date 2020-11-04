import math
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.db.models import Sum

from character.models import Charakter, RelVorteil, RelNachteil, RelFertigkeit, \
    RelMagische_Ausrüstung, Spieler

from shop.models import FirmaMagische_Ausrüstung
from log.views import logQuizPointsSP
from quiz.models import SpielerModule, Question, RelQuiz, Subject, SpielerQuestion, module_state
from quiz.views import get_grade_score, mw_from_grade_list

# TODO try-except around request.POST in this file

# dice roll
def random(request):
    dice = [
        {"art": "pink", "faces": [0, 0, 0, 1, 1, 2], "color": "hotpink"},
        {"art": "grün", "faces": [0, 0, 1, 1, 2, 2], "color": "green"},
        {"art": "weiß", "faces": [0, 1, 2, 2, 2, 3], "color": "white"},
        {"art": "schwarz", "faces": [0, 1, 2, 2, 3, 4], "color": "black"},

        {"art": "W4", "faces": [i for i in range(1, 5)]},
        {"art": "W6", "faces": [i for i in range(1, 7)]},
        {"art": "W8", "faces": [i for i in range(1, 9)]},
        {"art": "W10", "faces": [i for i in range(1, 11)]},
        {"art": "W12", "faces": [i for i in range(1, 13)]},
        {"art": "W20", "faces": [i for i in range(1, 21)]},
        {"art": "W100", "faces": [i for i in range(1, 101)]}
    ]

    return render(request, 'service/random.html', {'topic': 'Würfel', "dice": dice})


# quiz big brother
@login_required
def quiz_BB(request):

    if not User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
        return HttpResponse(status=404)

    all_spieler = RelQuiz.objects.all().order_by("-quiz_points_achieved")
    all_subjects = Subject.objects.all().order_by("titel")

    table = [[{"text": "Name"}, {"text": "Punkte"}, {"text": "Gesamt"}]]
    for s in all_subjects:
        table[0].append({"text": s.titel})

    for rel in all_spieler:
        # get name and points
        row = [
            {"text": rel.spieler.get_real_name() if rel.spieler.get_real_name() else rel.spieler.name, "link": reverse('service:quizTimetable', args=[rel.spieler.id])},
            {"text": rel.quiz_points_achieved}, {}
        ]

        # TODO: reformat passed_questions with its sp_mod
        passed_mods = [sp_mod.module for sp_mod in SpielerModule.objects.filter(spieler=rel.spieler, state=module_state[6][0])]   # state=passed
        passed_sp_qs = []
        for m in passed_mods:
            for mq in m.modulequestion_set.all():
                passed_sp_qs.append(SpielerQuestion.objects.filter(spieler=rel.spieler, question=mq.question).order_by("questions__started").first())


        # collect noten from all subjects (table[0][3:]) row and average
        sum_max_points = 0
        sum_achieved_points = 0

        for s in table[0][3:]:

            # get max points (sum points of questions whose modules are at least open)
            subject = s["text"]
            max_points = 0
            for sp_mod in SpielerModule.objects.filter(spieler=rel.spieler, state__gte=module_state[2][0]): # at least state of opened
                questions = sp_mod.module.questions.filter(topic__subject__titel=subject)

                if questions:
                    max_points += questions.aggregate(Sum("points"))["points__sum"]

            # get achieved points & delete all questions of current subject (speed)
            achieved_points = 0
            reduced_questions = []
            for sp_q in passed_sp_qs:
                if sp_q.question.topic.subject.titel == subject:
                    achieved_points += sp_q.achieved_points
                else:
                    reduced_questions.append(sp_q)
            passed_sp_qs = reduced_questions

            grade_score, tag_class = get_grade_score(achieved_points, max_points)

            cell = {"grade_score": grade_score, "tag_class": tag_class, "section_done": achieved_points == max_points,
                            "text": "{}/{}".format(math.floor(achieved_points), math.floor(max_points))}
            row.append(cell)

            # for average
            sum_max_points += max_points
            sum_achieved_points += achieved_points

        # construct entry for average
        grade_score, tag_class = get_grade_score(sum_achieved_points, sum_max_points)
        row[2] = {"grade_score": grade_score, "tag_class": tag_class, "section_done": sum_achieved_points == sum_max_points,
                  "text": "{}/{}".format(math.floor(sum_achieved_points), math.floor(sum_max_points))}

        # add row containing one player to table
        table.append(row)

    context = {"table": table, "topic": "Big Brother nach Punkten"}

    return render(request, "service/quiz_BB.html", context)
