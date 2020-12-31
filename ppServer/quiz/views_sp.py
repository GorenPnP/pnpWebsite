
import json
from functools import cmp_to_key
from quiz.forms import ModuleForm
from quiz.views import get_grade_score

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from ppServer.decorators import spielleiter_only, verified_account
from character.models import Spieler
from . import models


@login_required
@spielleiter_only(redirect_to="quiz:index")
def sp_index(request):

    context = {"topic": "Quiz (Spielleiter)", "entries": [
        {"titel": "Module bearbeiten", "url": reverse("quiz:sp_module_index"), "beschreibung": "Bearbeiten & neue anlegen"},
        {"titel": "Fragen sortieren", "url": reverse("quiz:sp_questions"), "beschreibung": "Fragen Modulen zuordnen"},
        {"titel": "Modulkontrolle", "url": reverse("quiz:sp_modules"), "beschreibung": "Module vom Spielern verwalten, z.B. korrigieren"},
        {"titel": "Quiz Big Brother", "url": reverse("service:quiz_BB"), "beschreibung": "nach Fächern"},
        {"titel": "Quiz Admin", "url": reverse("admin:app_list", args=["quiz"]), "beschreibung": "Die Admin-Page halt..."},
    ]}
    return render(request, "quiz/sp_index.html", context)


@login_required
# @spielleiter_only     <-- breaks
def sp_module_index(request):

    if not request.user.groups.filter(name="spielleiter").exists():
        return redirect("quiz:index")

    context = {
        "topic": "Quiz (Spielleiter)",
        "entries": [{"icon": m.icon.img.url if m.icon else None, "titel": m.title, "url": reverse("quiz:sp_module_edit", args=[m.id]), "beschreibung": m.description} for m in models.Module.objects.all()]
    }
    return render(request, "quiz/sp_module_index.html", context)


# common save of new or edited module (private function)
def post_save_module(module, request):
    form = ModuleForm(request.POST, instance=module)

    if not form.is_valid():
        context = {'topic': module.title, 'form': form}
        return render(request, "quiz/sp_module_edit.html", context)

    form.save(commit= False)

    if "icon" in request.FILES.keys():
        image = request.FILES.get("icon")
        module.icon = models.Image.objects.create(img=image)
    module.save()
    form.save_m2m()

    return redirect("quiz:sp_module_index")


@login_required
# @spielleiter_only     <-- breaks
def sp_module_add(request):

    if request.method == 'GET':

        # form without module (doesn't exist jet) but set num to next available
        form = ModuleForm()
        form.instance.num = models.next_id()

        context = {'topic': "Neues Module", 'form': form, 'icon': None}
        return render(request, "quiz/sp_module_edit.html", context)


    if request.method == 'POST':
        module = models.Module.objects.create()
        return post_save_module(module, request)

@login_required
# @spielleiter_only     <-- breaks
def sp_module_edit(request, id):

    if not request.user.groups.filter(name="spielleiter").exists():
        return redirect("quiz:index")

    # the original module
    module = get_object_or_404(models.Module, id=id)

    if request.method == 'GET':
        form = ModuleForm(instance=module)
        context = {'topic': module.title, 'form': form, 'icon': module.icon.img.url if module.icon else None}
        return render(request, "quiz/sp_module_edit.html", context)

    if request.method == 'POST':
        return post_save_module(module, request)


# map existing questions to modules
@login_required
@spielleiter_only(redirect_to="quiz:index")
def sp_questions(request):

    if request.method == "GET":
        mq = models.ModuleQuestion.objects.all()
        context = {"topic": "Fragen sortieren", "mqs": mq,
                   "questions": models.Question.objects.exclude(id__in=[model.question.id for model in mq]),
                   "mods": models.Module.objects.all()}
        return render(request, "quiz/sp_questions.html", context)

    if request.method == "POST":
        ms = models.Module.objects.all()
        qs = models.Question.objects.all()

        questions = json.loads(request.body.decode("utf-8"))["questions"]

        models.ModuleQuestion.objects.all().delete()
        for e in questions:
            if e["module"] < 0: continue
            models.ModuleQuestion.objects.create(question=qs.get(id=e["question"]), module=ms.get(id=e["module"]))

        return JsonResponse({})


def cmp_time(a, b):
    if a is None or a["timestamp"] is None: return 1
    if b is None or b["timestamp"] is None: return -1
    return 1 if a["timestamp"] <= b["timestamp"] else -1


@login_required
@spielleiter_only(redirect_to="quiz:index")
def sp_modules(request):

    # get SpielerModules from DB
    sp_mo = models.SpielerModule.objects.all()

    if request.method == "POST":

        # get content
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({"message": "Konnte Format nicht verstehen"}, status=418)

        # handle change in module states before filter to deliver changes
        if "state_changes" in data.keys():
            try:
                changes_optional = data["optional_changes"]
                for e in models.SpielerModule.objects.filter(id__in=changes_optional):
                    e.optional = not e.optional
                    e.save()

                changes = data["state_changes"]
                for e in models.SpielerModule.objects.filter(id__in=changes.keys()):
                    e.state = changes["{}".format(e.id)]
                    e.save()
                return JsonResponse({})
            except:
                return JsonResponse({"message": "Konnte Zustand nicht ändern"}, status=418)

        # handle filter
        try:
            player = data["player"]
            state = data["state"]
            module = data["modul"]
        except:
            return JsonResponse({"message": "Konnte Filter nicht finden"}, status=418)

        if player != -1: sp_mo = sp_mo.filter(spieler__id=player)
        if state  != -1: sp_mo = sp_mo.filter(state=state)
        if module != -1: sp_mo = sp_mo.filter(module__id=module)


    # both together
    modules = []
    for e in sp_mo:
        sessions = models.SpielerSession.objects.filter(spielerModule=e)
        score, score_class = get_grade_score(e.achieved_points, e.module.max_points) if e.achieved_points is not None else ("", "")
        modules.append(
            {
                "id": e.id,
                "icon": e.module.icon.img.url if e.module.icon else None,
                "module": e.module.title,
                "state": (e.state, e.get_state_display()),
                "spieler": e.spieler,
                "timestamp": sessions.first().started if sessions.count() else None,
                "achieved_points": e.achieved_points, "max_points": e.module.max_points,
                "score": score, "score_class": score_class,
                "optional": e.optional,
                "spent_reward": e.spent_reward, "spent_reward_larp": e.spent_reward_larp
            })
    modules = sorted(modules, key=cmp_to_key(cmp_time))

    selectOnStates = [0, 1, 2, 5, 6]    # ['locked', 'unlocked', 'opened', 'seen', 'passed']
    optionsLocked = [models.module_state[0], models.module_state[1], models.module_state[2], models.module_state[6]]    # ['locked', 'unlocked', 'opened', 'passed']
    optionsUnlocked = [models.module_state[1], models.module_state[2], models.module_state[6]]   # ['unlocked', 'opened', 'passed']
    optionsOpened = [models.module_state[1], models.module_state[2], models.module_state[6]]     # ['unlocked', 'opened', 'passed']
    optionsSeen = [models.module_state[1], models.module_state[2], models.module_state[5], models.module_state[6]]      # ['unlocked', 'opened', 'seen', 'passed']
    optionsPassed = [models.module_state[1], models.module_state[2], models.module_state[6]]     # ['unlocked', 'opened', 'passed']


    # return responses
    if request.method == "GET":
        return render(request, "quiz/sp_spieler_modules.html",
            {
                "topic": "Modulzuweisung",
                "spieler": Spieler.objects.all(),
                "states": models.module_state,
                "all_modules": models.Module.objects.all(),

                "selectOnStates": selectOnStates,
                "optionsLocked": optionsLocked,
                "optionsUnlocked": optionsUnlocked,
                "optionsOpened": optionsOpened,
                "optionsSeen": optionsSeen,
                "optionsPassed": optionsPassed,

                "modules": modules
            })

    if request.method == "POST":
        context = {"modules": modules,

                   "selectOnStates": selectOnStates,
                   "optionsLocked": optionsLocked,
                   "optionsUnlocked": optionsUnlocked,
                   "optionsOpened": optionsOpened,
                   "optionsSeen": optionsSeen,
                   "optionsPassed": optionsPassed
        }

        return JsonResponse({"html": render(request, "quiz/sp_module_list.html", context).content.decode("utf-8")})


@login_required
@spielleiter_only(redirect_to="quiz:index")
def sp_correct(request, id, question_index=0):

    sp_mo = get_object_or_404(models.SpielerModule, id=id)

    # no module for player selected
    if sp_mo.state != 3:    # if not 'answered'
        return redirect("quiz:sp_modules")

    current_session = sp_mo.getSessionInProgress()
    if not current_session:
        return redirect("quiz:sp_modules")

    if question_index is None or question_index < 0: question_index = 0
    spq = current_session.questions.all()[question_index]  if question_index < current_session.questions.count() else None

    # GET
    if request.method == "GET":

        # all questions done
        if not spq:

            # if not at least one question with achieved_points is None exists, redirect to the first one
            if current_session.questions.filter(achieved_points=None).exists():

                # Not all done! look through all again
                for index, q in enumerate(current_session.questions.all()):
                    if q.achieved_points is None:
                        return redirect(reverse("quiz:sp_correct_index", args=[id, index]))

            current_session.setCorrected()

            current_session.spielerModule.achieved_points = sum([q.achieved_points for q in current_session.questions.all()])
            current_session.spielerModule.save()

            return redirect("quiz:sp_modules")

        # collect things to display
        answers = spq.question.multiplechoicefield_set.all()
        checked_answers = json.loads(spq.answer_mc) if spq.answer_mc else []
        corrected_answers = json.loads(spq.correct_mc) if spq.correct_mc else []

        context = {"topic": "{} ({})".format(sp_mo.module.title, sp_mo.spieler.name),
                   "achieved_points": spq.achieved_points,
                   "question": spq.question, "spieler_question": spq,
                   "answers": answers, "checked_answers": checked_answers, "corrected_answers": corrected_answers,
                   "start_num_questions": current_session.questions.count(), "num_question": question_index + 1,
                   "display_btn_previous": question_index,
                   "display_btn_done": question_index + 1 == current_session.questions.count(),
                   "display_old_answer": sp_mo.pointsEarned(), "sp_mo_id": id, "question_index": question_index,
                   }

        return render(request, "quiz/sp_correct.html", context)


    # POST
    if request.method == "POST":

        # save meta info of question
        spq.question.answer_note = request.POST.get("answer_note")
        spq.question.save()

        # handle corretion
        spq.correct_text = request.POST.get("text")
        spq.correct_mc = request.POST.get("ids")

        # update points if they are not None. Use current score if successful
        # replace (all) , by . for float parsing
        try:
            points = float( request.POST.get("points").replace(",", ".") )
        except ValueError:
            points = None

        new_points = points if points is not None else spq.achieved_points
        spq.achieved_points = new_points

        # check whether it's valid:
        if "img" in request.FILES.keys():  # and imgForm.is_valid():
            image = request.FILES.get("img")
            spq.correct_img = models.Image.objects.create(img=image)
            spq.correct_img.save()

            """
            TODO: validate image and file data
            file_data = {'img': SimpleUploadedFile('face.jpg', request.FILES.get("img"))}
            imgForm = ImageForm({}, file_data)

            print("IMG valid", imgForm.cleaned_data)
            spq.correct_img = imgForm.cleaned_data.get("img")

        if fileForm.is_valid():
            print("FILE valid")
            spq.correct_file = fileForm.cleaned_data["file"]
        """
        if "file" in request.FILES.keys():  # and imgForm.is_valid():
            file = request.FILES.get("file")
            spq.correct_file = models.File.objects.create(file=file)
            spq.correct_file.save()

        spq.save()

        # if redirect somewhere, do it now
        redirect_url = request.POST.get("redirect")
        if (redirect_url):
            return redirect(redirect_url)

        # otherwise continue on: which question is next?
        next_question = question_index - 1 if request.POST.get("previous") else question_index + 1
        if next_question < 0: next_question = 0

        return redirect(reverse("quiz:sp_correct_index", args=[id, next_question]))


@verified_account
# @spielleiter_only     <-- breaks
def old_answer(request, sp_mo_id, question_id, question_index):    # id of currently answered SpielerQuestion

    if not request.user.groups.filter(name="spielleiter").exists():
        return redirect("quiz:index")

    sp_mo = get_object_or_404(models.SpielerModule, id=sp_mo_id)
    old_session = sp_mo.getFinishedSession()
    if not old_session:
        return redirect(reverse("quiz:sp_correct_index", args=[sp_mo_id, question_index]))

    old_spq = old_session.questions.get(question__id=question_id)

    # no module for player selected
    if sp_mo.state != 3:    # if not 'answered'
        return redirect(reverse("quiz:sp_correct_index", args=[sp_mo_id, question_index]))


    # all questions done
    if not old_spq:
        return redirect(reverse("quiz:sp_correct_index", args=[sp_mo_id, question_index]))

    answers = old_spq.question.multiplechoicefield_set.all()
    checked_answers = json.loads(old_spq.answer_mc) if old_spq.answer_mc else []
    corrected_answers = json.loads(old_spq.correct_mc) if old_spq.correct_mc else []

    context = {"topic": "{} ({})".format(sp_mo.module.title, sp_mo.spieler.name),
                "question": old_spq.question, "spieler_question": old_spq,
                "answers": answers, "checked_answers": checked_answers, "corrected_answers": corrected_answers,
                "start_num_questions": old_session.questions.count(), "num_question": question_index + 1,
                "called_from_sp": True, "return_to": reverse("quiz:sp_correct_index", args=[sp_mo_id, question_index])
                }
    return render(request, "quiz/review.html", context)
