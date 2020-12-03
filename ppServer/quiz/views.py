import collections, random, json, datetime
from math import floor
from functools import cmp_to_key

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from character.models import Spieler
from .models import *
from .forms import *


# TODO try-except around request.POST in this file

def get_grade_score(correct, max):
    if correct > max or max == 0:
        return "", ""

    grade_key = [   # minimal in%, Note
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
def index(request, spieler_id=None):
    # for Phillip's wish to see everyone's timetable
    if spieler_id is not None:
        if not User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
            return HttpResponse(status=404)
        spielleiter_service = True
        is_spielleiter = False
        spieler = get_object_or_404(Spieler, id=spieler_id)
    # usual case
    else:
        spielleiter_service = False
        is_spielleiter = User.objects.filter(username=request.user.username, groups__name='spielleiter').exists()
        spieler = get_object_or_404(Spieler, name=request.user.username)

    if request.method == "GET":

        timetable = []
        for sp_m in SpielerModule.objects.filter(spieler=spieler):

            score, score_class = get_grade_score(sp_m.achieved_points, sp_m.module.max_points) if sp_m.achieved_points is not None else ("", "")
            timetable.append({"titel": sp_m.module.title, "id": sp_m.id, "questions": sp_m.module.questions.count(),
                    "points": sp_m.achieved_points if sp_m.achieved_points else 0, "max_points": sp_m.module.max_points,
                    "score": score, "score_tag_class": score_class,
                    "description": sp_m.module.description, "icon": sp_m.module.icon.img.url if sp_m.module.icon else None,
                    "revard": sp_m.module.reward, "state": sp_m.get_state_display()})

        context = {"timetable": timetable, "topic": "{}'s Quiz".format(spieler.get_real_name()) if spielleiter_service else "Quiz",
                   "akt_punktzahl": get_object_or_404(RelQuiz, spieler=spieler).quiz_points}

        return render(request, "quiz/index.html", context)

    if request.method == "POST":
        sp_mod = json.loads(request.body.decode("utf-8"))["id"]
        rel, _ = RelQuiz.objects.get_or_create(spieler=spieler)
        rel.current_session, _ = SpielerSession.objects.get_or_create(spielerModule=get_object_or_404(SpielerModule, id=sp_mod))
        rel.save()

        return JsonResponse({"url": reverse("quiz:question")})


@login_required
def question(request):
    spieler = get_object_or_404(Spieler, name=request.user.username)
    rel = get_object_or_404(RelQuiz, spieler=spieler)

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

        context = {"topic": rel.current_session.spielerModule.module.title, "question": spq.question, "answers": answers,
                   "start_num_questions": rel.current_session.questions.count(), "num_question": rel.current_session.current_question + 1
                   }

        return render(request, "quiz/question.html", context)

    if request.method == "POST":

        spq = rel.current_session.currentQuestion()
        spq.answer_text = request.POST.get("text")
        spq.answer_mc = request.POST.get("ids")


        # check whether it's valid:
        if "img" in request.FILES.keys(): #and imgForm.is_valid():
            image = request.FILES.get("img")
            spq.answer_img = Image.objects.create(img=image, name="some name")
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
            spq.answer_file = File.objects.create(file=file, name="some name")
            spq.answer_file.save()

        spq.save()
        return redirect("quiz:question")


@login_required
def session_done(request):

    spieler = get_object_or_404(Spieler, name=request.user.username)
    rel = get_object_or_404(RelQuiz, spieler=spieler)
    if not rel.current_session: return redirect("quiz:index")

    if request.method == "GET":
        context = {"topic": rel.current_session.spielerModule.module.title}
        return render(request, "quiz/session_done.html", context)

    if request.method == "POST":
        rel.current_session = None
        rel.save()

        return redirect("quiz:index")


def score_board(request):

    # copy_tinker()

    spieler = []
    same = []
    for  s in RelQuiz.objects.all().order_by("-quiz_points_achieved"):
        if (len(same) >= 1 and same[0].quiz_points_achieved != s.quiz_points_achieved):
            spieler.append(same)
            same = []

        same.append(s)
    spieler.append(same)

    context = {"spieler": spieler}
    return render(request, "quiz/score_board.html", context)



def copy_tinker():
    from shop.models import Tinker, TinkerNeeds, TinkerWaste
    from crafting.models import Recipe, Ingredient, Product

    # populate recipes
    for t in Tinker.objects.all():
        r = Recipe.objects.create(table=t.herstellung_via, duration=t.herstellungsdauer)

        for s in t.probe_spezial.all(): r.spezial.add(s)
        for w in t.probe_wissen.all(): r.wissen.add(w)

        r.save()


        # add ingredients
        for tn in TinkerNeeds.objects.filter(product=t):
            Ingredient.objects.create(num=tn.num, item=tn.part, recipe=r)


        # add products
        Product.objects.create(num=t.num_product, item=t, recipe=r)

        for tw in TinkerWaste.objects.filter(rezept=t):
            Product.objects.create(num=tw.num, item=tw.neben, recipe=r)
