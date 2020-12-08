from django.db.models.aggregates import Count
from ppServer.decorators import spielleiter_only
import math

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Sum

from quiz.models import SpielerModule, RelQuiz, SpielerSession, Subject, SpielerQuestion, module_state
from quiz.views import get_grade_score

# TODO try-except around request.POST in this file

# dice roll
@login_required
@spielleiter_only
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

def quiz_BB(request):

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

        # use questions of seen/passed modules
        sp_mods_done = SpielerModule.objects.filter(spieler=rel.spieler, state__in=[5, 6]).exclude(achieved_points=None)      # state=passed OR seen
        sessions = [SpielerSession.objects.filter(spielerModule=sp_mo).order_by("-started").first() for sp_mo in sp_mods_done]

        # use questions of all other modules if they were answered previously
        sp_mods_pending = SpielerModule.objects.filter(spieler=rel.spieler).exclude(state__in=[5, 6], achieved_points=None)  # state!=passed OR seen
        for sp_mo in sp_mods_pending:
            sp_mo_sessions = SpielerSession.objects.filter(spielerModule=sp_mo)
            if sp_mo_sessions.count() > 1:
                sessions.append(sp_mo_sessions[1])

        # really retrieve (spieler)questions
        passed_sp_qs = []
        for s in sessions:
            if s is None: continue      # ignore, can happen on a passe module with deleted sessions

            passed_sp_qs += s.questions.all()

        # collect noten from all subjects (table[0][3:]) row and average
        sum_max_points = 0
        sum_achieved_points = 0

        for s in table[0][3:]:

            subject = s["text"]

            # get achieved points & delete all questions of current subject from list (speed)
            max_points = 0
            achieved_points = 0

            reduced_questions = []
            for sp_q in passed_sp_qs:

                # take question over to next subject
                if sp_q.question.topic.subject.titel != subject:
                    reduced_questions.append(sp_q)
                    continue

                # get achieved points (sum points of questions whose modules are at least open)
                achieved_points += sp_q.achieved_points

                # get max points (sum points of questions whose modules are at least open)
                max_points += sp_q.question.points

            passed_sp_qs = reduced_questions

            grade_score, tag_class = get_grade_score(achieved_points, max_points)

            # collect vals for cell and append it to player's row
            cell = {"grade_score": grade_score, "tag_class": tag_class, "section_done": achieved_points == max_points,
                            "text": "{}/{}".format(round(achieved_points, 2), round(max_points, 2))}
            row.append(cell)

            # for average
            sum_max_points += max_points
            sum_achieved_points += achieved_points

        # construct entry for average
        grade_score, tag_class = get_grade_score(sum_achieved_points, sum_max_points)
        row[2] = {"grade_score": grade_score, "tag_class": tag_class, "section_done": sum_achieved_points == sum_max_points,
                  "text": "{}/{}".format(round(sum_achieved_points, 2), round(sum_max_points, 2))}

        # add row containing one player to table
        table.append(row)

    context = {"table": table, "topic": "Big Brother nach Punkten"}

    return render(request, "service/quiz_BB.html", context)
