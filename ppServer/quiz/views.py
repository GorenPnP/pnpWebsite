from ppServer.decorators import verified_account
import random, json
from math import floor

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from character.models import Spieler
from . import models


# TODO try-except around request.POST in this file

def get_grade_score(correct, max):
    if max == 0:
        return "", ""

    grade_key = [   # minimal in%, Note
        {"min": 100, "main": "S", "extra": ""},
        {"min": 95, "main": "A", "extra": "+"},
        {"min": 90, "main": "A", "extra": ""},
        {"min": 85, "main": "A", "extra": "-"},

        {"min": 80, "main": "B", "extra": "+"},
        {"min": 75, "main": "B", "extra": ""},
        {"min": 70, "main": "B", "extra": "-"},

        {"min": 65, "main": "C", "extra": "+"},
        {"min": 60, "main": "C", "extra": ""},
        {"min": 55, "main": "C", "extra": "-"},

        {"min": 50, "main": "D", "extra": "+"},
        {"min": 45, "main": "D", "extra": ""},
        {"min": 40, "main": "D", "extra": "-"},

        {"min": 34, "main": "E", "extra": "+"},
        {"min": 28, "main": "E", "extra": ""},
        {"min": 20, "main": "E", "extra": "-"},

        {"min": 0, "main": "F", "extra": ""},
    ]
    percent = round((correct / max) * 100, 2)
    for e in grade_key:
        if percent >= e["min"]:
            return e["main"] + e["extra"], "grade_{}".format(e["main"])
    return "F-", "grade_F"


def mw_from_grade_list(grade_list):
    note = {"A+": 15, "A": 14, "A-": 13, "B+": 12, "B": 11, "B-": 10,
            "C+": 9, "C": 8, "C-": 7, "D+": 6, "D": 5, "D-": 4, "E+": 3, "E": 2, "E-": 1, "F": 0}
    grades = {}
    for g, n in note.items():
        grades[n] = g

    sum_grades = 0
    num_grades = 0
    for g in grade_list:
        if g in note.keys():
            sum_grades += note[g]
            num_grades += 1

    if num_grades == 0:
        return ""
    return grades[floor(sum_grades / num_grades + 0.5)]


@login_required
@verified_account
def index(request, spieler_id=None):

    spielleiter_service = False

    # for Phillip's wish to see everyone's timetable
    if spieler_id is not None and\
        User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():

        spielleiter_service = True

    # usual case if not spielleiter_service (as in: BB). Or not.
    spieler = get_object_or_404(Spieler, name=request.user.username) if not spielleiter_service else get_object_or_404(Spieler, id=spieler_id)

    if request.method == "GET":

        timetable = []
        for sp_m in models.SpielerModule.objects.filter(spieler=spieler).prefetch_related("module__questions", "module__icon", "module__prerequisite_modules"):

            score, score_class = get_grade_score(sp_m.achieved_points, sp_m.module.max_points) if sp_m.achieved_points is not None else ("", "")
            timetable.append({"titel": sp_m.module.title, "id": sp_m.id, "questions": sp_m.module.questions.count(),
                    "points": sp_m.achieved_points, "max_points": sp_m.module.max_points,
                    "score": score, "score_tag_class": score_class,
                    "optional": sp_m.optional,
                    "description": sp_m.module.description, "icon": sp_m.module.icon.img.url if sp_m.module.icon else None,
                    "reward": sp_m.module.reward, "spent_reward": sp_m.spent_reward, "spent_reward_larp": sp_m.spent_reward_larp,
                    "state": sp_m.get_state_display(),
                    "prerequisites": ", ".join([m.title for m in sp_m.module.prerequisite_modules.all()])})

        context = {"timetable": timetable, "topic": "{}'s Quiz".format(spieler.get_real_name()) if spielleiter_service else "Quiz",
                   "akt_punktzahl": get_object_or_404(models.RelQuiz, spieler=spieler).quiz_points_achieved, "button_states": ["opened", "corrected"]}

        return render(request, "quiz/index.html", context)

    if request.method == "POST":
        sp_mo_id = int(request.POST.get("id").replace(".", ""))
        sp_mo = get_object_or_404(models.SpielerModule, id=sp_mo_id)

        # opened
        if sp_mo.state == 2:

            rel, _ = models.RelQuiz.objects.get_or_create(spieler=spieler)

            session = sp_mo.getSessionInProgress()
            rel.current_session = session if session else models.SpielerSession.objects.create(spielerModule=sp_mo)
            rel.save(update_fields=["current_session"])

            return redirect("quiz:question")

        # corrected
        if sp_mo.state == 4:
            return redirect(reverse("quiz:review", args=[sp_mo_id]))

        # else
        return redirect("quiz:index")


@login_required
@verified_account
def question(request):
    spieler = get_object_or_404(Spieler, name=request.user.username)
    rel = get_object_or_404(models.RelQuiz, spieler=spieler)

    if request.method == "GET":

        # no module for player selected
        if not rel.current_session: return redirect("quiz:index")

        state = rel.current_session.spielerModule.state
        if state == 3:    # if 'answered'
            return redirect("quiz:session_done")

        if state != 2:    # if not 'opened'
            return redirect("quiz:index")

        spq = rel.current_session.nextQuestion()

        # all questions done
        if not spq:
            rel.current_session.setAnswered()
            return redirect("quiz:session_done")

        answers = [a for a in spq.question.multiplechoicefield_set.all()]
        random.seed()
        random.shuffle(answers)

        context = {
            "topic": rel.current_session.spielerModule.module.title,
            "question": spq.question,
            "answers": answers,
            "start_num_questions": rel.current_session.questions.count(),
            "num_question": rel.current_session.current_question + 1,
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:index"),
        }

        return render(request, "quiz/question.html", context)

    if request.method == "POST":

        spq = rel.current_session.currentQuestion()
        spq.answer_text = request.POST.get("text")
        spq.answer_mc = request.POST.get("ids")


        # check whether it's valid:
        if "img" in request.FILES.keys(): #and imgForm.is_valid():
            image = request.FILES.get("img")
            spq.answer_img = models.Image.objects.create(img=image, name="some name")
            spq.answer_img.save()

            """
            TODO: validate image and file data
            file_data = {'img': SimpleUploadedFile('face.jpg', request.FILES.get("img"))}
            imgForm = ImageForm({}, file_data)

            print("IMG valid", imgForm.cleaned_data)
            spq.answer_img = imgForm.cleaned_data.get("img")

        if fileForm.is_valid():
            print("FILE valid")
            spq.answer_file = fileForm.cleaned_data["file"]
        """
        if "file" in request.FILES.keys():  # and imgForm.is_valid():
            file = request.FILES.get("file")
            spq.answer_file = models.File.objects.create(file=file, name="some name")
            spq.answer_file.save()

        spq.save()
        return redirect("quiz:question")


@login_required
@verified_account
def session_done(request):

    spieler = get_object_or_404(Spieler, name=request.user.username)
    rel = get_object_or_404(models.RelQuiz, spieler=spieler)
    if not rel.current_session: return redirect("quiz:index")

    if request.method == "GET":
        context = {
            "topic": rel.current_session.spielerModule.module.title,
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:index"),
        }
        return render(request, "quiz/session_done.html", context)

    if request.method == "POST":
        rel.current_session = None
        rel.save(update_fields=["current_session"])

        return redirect("quiz:index")


@login_required
@verified_account
def score_board(request):

    spieler = []
    same = []
    for  s in models.RelQuiz.objects.all().order_by("-quiz_points_achieved"):
        if (len(same) >= 1 and same[0].quiz_points_achieved != s.quiz_points_achieved):
            spieler.append(same)
            same = []

        same.append(s)
    spieler.append(same)

    context = {
        "spieler": spieler,
        "topic": "Bestenliste",
        "app_index": "Quiz",
        "app_index_url": reverse("quiz:index"),
    }
    return render(request, "quiz/score_board.html", context)


@login_required
@verified_account
def review(request, id):

    sp_mo = get_object_or_404(models.SpielerModule, id=id)

    # no module for player selected
    if sp_mo.state != 4:    # if not 'corrected'
        return redirect("quiz:index")

    current_session = sp_mo.getSessionInProgress()
    if not current_session:
        return redirect("quiz:index")

    # GET
    if request.method == "GET":

        spq = current_session.nextQuestion()

        # all questions done
        if not spq:

            # change state to seen
            current_session.setSeen()

            spieler = sp_mo.spieler
            rel = get_object_or_404(models.RelQuiz, spieler=spieler)

            # calc new score
            rel.quiz_points_achieved = sum([q.achieved_points for q in models.SpielerModule.objects.filter(
                spieler=spieler) if q.pointsEarned() and q.achieved_points is not None]) # sum all modules with earned points on them

            rel.save(update_fields=["quiz_points_achieved"])

            return redirect("quiz:review_done")

        answers = spq.question.multiplechoicefield_set.all()
        checked_answers = json.loads(spq.answer_mc) if spq.answer_mc else []
        corrected_answers = json.loads(spq.correct_mc) if spq.correct_mc else []

        context = {
            "topic": "{} ({})".format(sp_mo.module.title, sp_mo.spieler.name),
            "question": spq.question, "spieler_question": spq,
            "answers": answers, "checked_answers": checked_answers, "corrected_answers": corrected_answers,
            "start_num_questions": current_session.questions.count(), "num_question": current_session.current_question + 1,
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:index"),
        }
        return render(request, "quiz/review.html", context)

    # POST
    if request.method == "POST":

        current_session.current_question += 1
        current_session.save(update_fields=["current_question"])

        return redirect(reverse("quiz:review", args=[id]))


@login_required
@verified_account
def review_done(request):

    spieler = get_object_or_404(Spieler, name=request.user.username)
    rel = get_object_or_404(models.RelQuiz, spieler=spieler)
    if not rel.current_session:
        return redirect("quiz:index")

    if request.method == "GET":
        context = {
            "topic": rel.current_session.spielerModule.module.title,
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:index"),
        }
        return render(request, "quiz/review_done.html", context)

    if request.method == "POST":
        rel.current_session = None
        rel.save(update_fields=["current_session"])

        return redirect("quiz:index")
