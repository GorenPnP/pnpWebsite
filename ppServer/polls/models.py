import datetime
from django.utils import timezone

from django.db import models

from character.models import Spieler


def default_deadline():
    return datetime.datetime.now() + datetime.timedelta(days=14)


class Question(models.Model):
    class Meta:
        verbose_name = "Umfrage"
        verbose_name_plural = "Umfragen"

    text = models.CharField(max_length=200)
    anz_stimmen = models.PositiveIntegerField("Stimmen pro Person", default=1)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    deadline = models.DateTimeField('deadline', default=default_deadline)
    show_result_to_user = models.BooleanField(default=False)
    allow_multiple_selection = models.BooleanField(default=False)

    spieler_voted = models.ManyToManyField(Spieler, through="QuestionSpieler")

    def umfrage_läuft(self):
        return self.pub_date <= datetime.datetime.now(tz=datetime.timezone.utc) <= self.deadline

    umfrage_läuft.admin_order_field = 'pub_date'
    umfrage_läuft.boolean = True
    umfrage_läuft.short_description = 'Umfrage läuft gerade'

    def __str__(self):
        return self.text


class Choice(models.Model):
    class Meta:
        verbose_name = "Wahl"
        verbose_name_plural = "Wahlen"

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class QuestionSpieler(models.Model):
    class Meta:
        verbose_name = "hat abgestimmt"
        verbose_name_plural = "haben abgestimmt"
        unique_together = ["question", "spieler"]

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    spieler = models.ForeignKey(Spieler, on_delete=models.CASCADE)

    def __str__(self):
        return self.spieler.name + " hat abgestimmt"
