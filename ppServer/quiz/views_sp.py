import json

from django.db.models import Subquery, OuterRef
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import format_html

from django_tables2.columns import TemplateColumn

from base.abstract_views import DynamicTableView, GenericTable
from ppServer.decorators import spielleitung_only, verified_account
from ppServer.mixins import SpielleitungOnlyMixin, VerifiedAccountMixin

from .models import *
from .views import get_grade_score


@verified_account
@spielleitung_only(redirect_to="quiz:index")
def sp_index(request):

    context = {"topic": "Quiz (Spielleitung)", "entries": [
        {"titel": "Fragen sortieren", "url": reverse("quiz:sp_questions"), "beschreibung": "Fragen Modulen zuordnen"},
        {"titel": "Modulkontrolle", "url": reverse("quiz:sp_modules"), "beschreibung": "Module vom Spielern verwalten, z.B. korrigieren"},
        {"titel": "Quiz Big Brother", "url": reverse("service:quiz_BB"), "beschreibung": "nach Fächern"},
        {"titel": "Quiz Admin", "url": reverse("admin:app_list", args=["quiz"]), "beschreibung": "Die Admin-Page halt..."},
    ]}
    return render(request, "quiz/sp_index.html", context)


# map existing questions to modules
@verified_account
@spielleitung_only(redirect_to="quiz:index")
def sp_questions(request):

    if request.method == "GET":
        mq = ModuleQuestion.objects.all()
        context = {
            "topic": "Fragen sortieren", "mqs": mq,
            "questions": Question.objects.exclude(id__in=[model.question.id for model in mq]),
            "mods": Module.objects.all(),
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:sp_index"),
        }
        return render(request, "quiz/sp_questions.html", context)

    if request.method == "POST":
        ms = Module.objects.all()
        qs = Question.objects.all()

        questions = json.loads(request.body.decode("utf-8"))["questions"]

        ModuleQuestion.objects.all().delete()
        for e in questions:
            if e["module"] < 0: continue
            ModuleQuestion.objects.create(question=qs.get(id=e["question"]), module=ms.get(id=e["module"]))

        return JsonResponse({})


class SpModulesView(VerifiedAccountMixin, SpielleitungOnlyMixin, DynamicTableView):
    class Table(GenericTable):
        class Meta:
            model = SpielerModule
            fields = ["module", "spieler", "state", "achieved_points", "timestamp"]
            attrs = GenericTable.Meta.attrs
            order_by_field = "-timestamp"

        state = TemplateColumn(template_name="quiz/sp_spieler_module_status.html")

        def render_module(self, value, record):
            if not record.module.icon: return value

            spent = ""
            if record.spent_reward or record.spent_reward_larp:
                spent = f"✔ {'LARP' if record.spent_reward_larp else 'PnP'}"
            return format_html(f"<div class='title'><img class='logo' src='{record.module.icon.img.url}'><span class='module'>{value}</span><span class='spent'>{spent}</span></div>")

        def render_spieler(self, value, record):
            return record.spieler.get_real_name()

        def render_achieved_points(self, value, record):
            max_points = record.module.max_points
            [score, score_class] = get_grade_score(value, max_points)

            score_tag = f"<div class='score {score_class}'>{score}</div>"
            return format_html(f"{score_tag}<div class='points'>{value:-.2f} / {max_points:-.2f}")


    model = SpielerModule
    queryset = SpielerModule.objects\
        .prefetch_related("sessions", "module__icon", "spieler")\
        .annotate(
            timestamp = Subquery(SpielerSession.objects.filter(spielerModule__id=OuterRef("id")).order_by("-started")[:1].values("started"))
        )
    filterset_fields = {
        "module": ["exact"],
        "spieler": ["exact"],
        "state": ["exact"],
    }
    table_class = Table
    topic = "Modulzuweisung"
    template_name = "quiz/sp_spieler_modules.html"

    app_index_url = "quiz:sp_index"

    def post(self, request, *args, **kwargs):

        # update fields "state", "optional" of some SpielerModule objects
        for field in request.POST.keys():
            value = request.POST.get(field)

            if field.startswith("state"):
                optional = request.POST.get(field.replace("state", "optional"))
                
                id = int(field.split("-")[1].replace(".", ""))
                SpielerModule.objects.filter(id=id).update(state = value, optional = optional == "on")
        
        return redirect(request.build_absolute_uri())


@verified_account
@spielleitung_only(redirect_to="quiz:index")
def sp_correct(request, id, question_index=0):

    sp_mo = get_object_or_404(SpielerModule, id=id)

    # no module for player selected
    if sp_mo.state != 3:    # if not 'answered'
        return redirect("quiz:sp_modules")

    current_session = sp_mo.getSessionInProgress()
    if not current_session:
        return redirect("quiz:sp_modules")

    if question_index is None or question_index < 0: question_index = 0

    sqs = current_session.sorted_spieler_questions()
    spq = sqs[question_index]  if question_index < len(sqs) else None

    # GET
    if request.method == "GET":

        # all questions done
        if not spq:

            # if not at least one question with achieved_points is None exists, redirect to the first one
            if any([sq.achieved_points is None for sq in sqs]):

                # Not all done! look through all again
                for index, q in enumerate(sqs):
                    if q.achieved_points is None:
                        return redirect(reverse("quiz:sp_correct_index", args=[id, index]))

            current_session.setCorrected()

            current_session.spielerModule.achieved_points = sum([q.achieved_points for q in sqs])
            current_session.spielerModule.save(update_fields=["achieved_points"])

            return redirect("quiz:sp_modules")

        # collect things to display
        answers = spq.question.multiplechoicefield_set.all()
        checked_answers = json.loads(spq.answer_mc) if spq.answer_mc else []
        corrected_answers = json.loads(spq.correct_mc) if spq.correct_mc else []

        num_questions = len(sqs)
        context = {
            "topic": "{} ({})".format(sp_mo.module.title, sp_mo.spieler.name),
            "achieved_points": spq.achieved_points,
            "question": spq.question, "spieler_question": spq,
            "answers": answers, "checked_answers": checked_answers, "corrected_answers": corrected_answers,
            "start_num_questions": num_questions, "num_question": question_index + 1,
            "display_btn_previous": question_index,
            "display_btn_done": question_index + 1 == num_questions,
            "display_old_answer": sp_mo.pointsEarned(), "sp_mo_id": id,
            "question_index": question_index, "prev_question_index": question_index - 1, "next_question_index": question_index + 1,
            "pages": [i for i in range(num_questions)],
            "app_index": "Quiz",
            "app_index_url": reverse("quiz:sp_index"),
        }

        return render(request, "quiz/sp_correct.html", context)


    # POST
    if request.method == "POST":

        # save meta info of question
        spq.question.answer_note = request.POST.get("answer_note")
        spq.question.save(update_fields=["answer_note"])

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
            spq.correct_img = Image.objects.create(img=image)
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
            spq.correct_file = File.objects.create(file=file)
            spq.correct_file.save()

        spq.save()

        # if redirect somewhere, do it now
        redirect_url = request.POST.get("redirect")
        if (redirect_url):
            return redirect(redirect_url)

        # otherwise continue on
        return redirect(reverse("quiz:sp_correct_index", args=[id, question_index + 1]))


@verified_account
@spielleitung_only("quiz:index")
def old_answer(request, sp_mo_id, question_id, question_index):    # id of currently answered SpielerQuestion

    sp_mo = get_object_or_404(SpielerModule, id=sp_mo_id)
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

    context = {
        "topic": "{} ({})".format(sp_mo.module.title, sp_mo.spieler.name),
        "question": old_spq.question, "spieler_question": old_spq,
        "answers": answers, "checked_answers": checked_answers, "corrected_answers": corrected_answers,
        "start_num_questions": old_session.questions.count(), "num_question": question_index + 1,
        "called_from_sp": True, "return_to": reverse("quiz:sp_correct_index", args=[sp_mo_id, question_index]),
        "app_index": "Quiz",
        "app_index_url": reverse("quiz:sp_index"),
    }
    return render(request, "quiz/review.html", context)
