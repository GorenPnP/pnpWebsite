import string, random, json
from datetime import date
from math import ceil

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from django_resized import ResizedImageField

from character.models import Spieler


module_state = [
    (0, "locked"),      # prerequisites not met
    (1, "unlocked"),    # prerequisites met
    (2, "opened"),      # open for answering
    (3, "answered"),    # answered by player
    (4, "corrected"),   # corrected by gamemaster
    (5, "seen"),        # reviewed by player
    (6, "passed")       # marked as successfully completed by gamemaster
]

# used before save on Question.picture and Answer.picture to hide real name in src-path of img-tag in HTML (anti-cheat)
def upload_and_rename_picture(instance, filename):
    file_extension = filename.split('.')[::-1][0]

    today = date.today()
    path =\
        "quiz/{}-{}-{}/".format(today.year, today.month, today.day) +\
        "".join([random.choice(string.ascii_letters + string.digits) for _ in range(20)]) +\
        "." + file_extension
    return path


class RelQuiz(models.Model):
    class Meta:
        verbose_name = "Spieler Stats"
        verbose_name_plural = "Spieler Stats"

        ordering = ["spieler"]

    spieler = models.OneToOneField(Spieler, on_delete=models.CASCADE, null=True, unique=True)

    current_session = models.ForeignKey("SpielerSession", on_delete=models.SET_NULL, null=True, blank=True)
    quiz_points_achieved = models.FloatField(default=0, blank=True)


class Image(models.Model):

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Bilder"

        ordering = ["name"]

    img = ResizedImageField(size=[512, 512], upload_to=upload_and_rename_picture)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self): return self.name


class File(models.Model):

    class Meta:
        verbose_name = "Datei"
        verbose_name_plural = "Dateien"

        ordering = ["name"]

    file = models.FileField(upload_to=upload_and_rename_picture)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self): return self.name


class Subject(models.Model):    # as in: subject like Plants, Monsters, Wesen, ..
    class Meta:
        verbose_name = "Fach"
        verbose_name_plural = "Fächer"

        unique_together = ["titel"]
        ordering = ["titel"]

    titel = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.titel


class Topic(models.Model):
    class Meta:
        verbose_name = "Thema"
        verbose_name_plural = "Themen"

        unique_together = [("titel", "subject")]
        ordering = ["subject", "titel"]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Many to one-relation, can only belong to one Subject
    titel = models.CharField(max_length=100, default="")

    def __str__(self):
        return "{}: {}".format(self.subject, self.titel)


class Question(models.Model):
    class Meta:
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"

        ordering = ["topic", "grade"]

    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(13)])
    points = models.FloatField(default=0)

    text = models.TextField(max_length=2000, default="")

    images = models.ManyToManyField(Image, blank=True)
    files = models.ManyToManyField(File, blank=True)

    answer_note = models.TextField(max_length=2000, null=True, blank=True)

    allow_text = models.BooleanField(default=True)
    allow_upload = models.BooleanField(default=False)

    def __str__(self):
        return "{} ({} Punkte)".format(self.text[:57] + (self.text[57:] and '...'), self.points)


class MultipleChoiceField(models.Model):
    class Meta:
        verbose_name = "Multiple Choice Möglichkeit"
        verbose_name_plural = "Multiple Choice Möglichkeiten"

        ordering = ["to_question", "text"]

    to_question = models.ForeignKey(Question, on_delete=models.CASCADE) # Many to one-relation: Answer to exactly one Question
    text = models.TextField(max_length=200, default="", blank=True)
    img = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.text


class ModuleQuestion(models.Model):

    class Meta:
        verbose_name = "Frage eines Moduls"
        verbose_name_plural = "Fragen eines Moduls"

        ordering = ["module", "num"]
        unique_together = [("module", "question"), ("module", "num")]

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)

    num = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "{} in {} NR. {}".format(self.question.text, self.module.title, self.num)


def next_id():
    return ceil(Module.objects.last().num) + 1.0 if Module.objects.exists() else 1.0

class Module(models.Model):

    class Meta:
        verbose_name = "Modul"
        verbose_name_plural = "Module"

        ordering = ["num"]

    num = models.FloatField(unique=True, default=next_id)
    icon = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name="icon", related_query_name="icon")

    prerequisite_modules = models.ManyToManyField('Module', blank=True)

    questions = models.ManyToManyField(Question, through=ModuleQuestion)

    title = models.CharField(max_length=300)
    reward = models.TextField()
    description = models.TextField()

    max_points = models.FloatField(default=0)

    def __str__(self):
        return self.title


class SpielerModule(models.Model):    # if existing, Spieler answered related Questions
    class Meta:
        verbose_name = "Modulstatus eines Spielers"
        verbose_name_plural = "Modulstati eines Spielers"

        unique_together = [("spieler", "module")]
        ordering = ["spieler", "module"]

    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    state = models.PositiveSmallIntegerField(choices=module_state, default=module_state[0][0])
    # answering this module(again) is optional. It count as achieved prerequisite to others and the achieved_points will be added to the overall score
    optional = models.BooleanField(default=False)

    achieved_points = models.FloatField(default=None, null=True, blank=True)

    spent_reward = models.BooleanField(default=False)
    spent_reward_larp = models.BooleanField(default=False)
    spent_reward_on = models.TextField(blank=True, null=True)

    sessions = models.ManyToManyField("SpielerSession")

    def __str__(self):
        return "{} von {}".format(self.module, self.spieler)

    def getFinishedSession(self):
        sessions = self.spielersession_set.all() # is .order_by("-started"), see class SpielerSession.Meta.ordering

        if self.state in [5, 6]: return sessions.first()
        return sessions[1] if sessions.count() > 1 else None

    def getSessionInProgress(self):
        return SpielerSession.objects.filter(spielerModule=self).order_by("-started").first() if self.state < 5 else None

    def pointsEarned(self):
        return self.state in [5, 6] or self.optional or self.spielersession_set.count() > 1

    def moduleFinished(self):
        return self.state in [5, 6] or self.optional


class SpielerSession(models.Model):
    class Meta:
        verbose_name = "Moduldurchlauf eines Spielers"
        verbose_name_plural = "Moduldurchläufe eines Spielers"

        unique_together = ["spielerModule", "started"]
        ordering = ["spielerModule", "-started"]

    spielerModule = models.ForeignKey(SpielerModule, on_delete=models.CASCADE, null=True)


    questions = models.ManyToManyField("SpielerQuestion", related_name="questions")
    # question of questions which the spieler answers right now or is corrected right now. None ^= all done
    current_question = models.SmallIntegerField(default=0, blank=True, null=True)

    started = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self): return "{}, Start um {}".format(self.spielerModule, self.started)

    def sorted_spieler_questions(self):

        # get all own SpielerQuestions
        sqs = self.questions.all()

        # get num out of ModuleQUESTIONs for all found SpielerQUESTIONs
        mqs_in_order = ModuleQuestion.objects.filter(module=self.spielerModule.module, question__in=[sq.question for sq in sqs])

        question_id_to_num = {}     # {question_id: num, ...}
        for mq in mqs_in_order: question_id_to_num[mq.question.id] = mq.num

        return sorted(sqs, key=lambda sq: question_id_to_num[sq.question.id])


    def currentQuestion(self):
        questions = self.sorted_spieler_questions()
        return questions[self.current_question] if self.current_question is not None and self.current_question < len(questions) else None


    def nextQuestion(self):
        ''' returns next spielerQuestion of module or None if no more exist '''

        # current questions index, work from here to next question
        current_question = self.currentQuestion()
        if not current_question: return None

        # get all questions and index to the next to display. Is the current if no answer was given.
        offset = 1 if (self.spielerModule.state == 2 and (json.loads(current_question.answer_mc) or current_question.answer_text or current_question.answer_img or current_question.answer_file)) or\
                      (self.spielerModule.state == 3 and (current_question.achieved_points is not None)) else 0
        questions = self.sorted_spieler_questions()

        # if index out of bounds, return None
        if self.current_question + offset >= len(questions) or self.current_question + offset < 0: return None

        # apply offset
        self.current_question += offset
        self.save(update_fields=["current_question"])

        return questions[self.current_question]


    def setOpened(self):
        self._setState(module_state[2][0])

    def setAnswered(self):
        self._setState(module_state[3][0])

    def setCorrected(self):
        self._setState(module_state[4][0])

    def setSeen(self):
        self._setState(module_state[5][0])

    def _setState(self, state):
        self.spielerModule.state = state
        self.spielerModule.save(update_fields=["state"])

        self.current_question = 0
        self.save(update_fields=["current_question"])


class SpielerQuestion(models.Model):

    class Meta:
        verbose_name = "Fragendurchlauf eines Spielers"
        verbose_name_plural = "Fragendurchläufe eines Spielers"

        ordering = ["spieler"]    # TODO manual ordering by moduleQuestions.num at current module needed, because a question could appear in multiple modules

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)

    moduleQuestions = models.ManyToManyField(ModuleQuestion)

    achieved_points = models.FloatField(null=True, blank=True)

    # fields for answer
    answer_mc = models.TextField(default="[]")      # json-array of multiple choice answers (ids of selected MultipleChoiceFields)
    answer_text = models.TextField(null=True, blank=True)
    answer_img = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name="answer_img")
    answer_file = models.OneToOneField(File, on_delete=models.SET_NULL, null=True, blank=True, related_name="answer_file")

    # fields for correction
    correct_mc = models.TextField(default="[]")     # json-array of multiple choice answers (ids of corrected MultipleChoiceFields)
    correct_text = models.TextField(null=True, blank=True)
    correct_img = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name="correct_img")
    correct_file = models.OneToOneField(File, on_delete=models.SET_NULL, null=True, blank=True, related_name="correct_file")

    def __str__(self):
        return self.question.__str__()
