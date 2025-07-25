from ppServer.decorators import spielleitung_only

from django.shortcuts import render
from django.urls import reverse

from ppServer.decorators import verified_account
from quiz.models import SpielerModule, RelQuiz, Subject
from quiz.views import get_grade_score

# TODO try-except around request.POST in this file

# dice roll
@verified_account
def random(request):
    dice = [
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
@verified_account
@spielleitung_only("quiz:index")
def quiz_BB(request):

    table = [[{"text": "Name"}, {"text": "Punkte"}, {"text": "Gesamt"}, *[{"text": s.titel} for s in Subject.objects.all().order_by("titel")]]]

    all_spieler = RelQuiz.objects.prefetch_related("spieler").order_by("-quiz_points_achieved")
    for rel in all_spieler:
        # get name and points
        row = [
            {"text": rel.spieler.get_real_name(), "link": reverse('service:quizTimetable', args=[rel.spieler.id])},
            {"text": rel.quiz_points_achieved}, {}
        ]

        # use questions of seen/passed modules
        sp_mo_qs = SpielerModule.objects\
            .prefetch_related("spielersession_set__questions__question__topic__subject")\
            .filter(spieler=rel.spieler).exclude(achieved_points=None)
        sp_mods = [sp_mo for sp_mo in sp_mo_qs if sp_mo.pointsEarned()]      # state=passed OR seen
        sessions = [sp_mo.getFinishedSession() for sp_mo in sp_mods if sp_mo is not None]

        # really retrieve (spieler)questions
        passed_sp_qs = []
        for s in sessions:
            if s is None: continue      # ignore, can happen, e.g. on a passed module with deleted sessions

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

                # TODO don't just ignore a value of null on a finished session question!
                if sp_q.achieved_points is None: continue

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

    context = {
        "table": table,
        "topic": "Big Brother nach Punkten",
        "app_index": "Quiz",
        "app_index_url": reverse("quiz:sp_index")
    }

    return render(request, "service/quiz_BB.html", context)
