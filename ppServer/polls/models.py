import datetime
from django.utils import timezone

from django.db import models
from django.utils.timezone import now

from character.models import Spieler


def default_deadline():
    return now() + datetime.timedelta(days=14)


class Question(models.Model):
    class Meta:
        verbose_name = "Umfrage"
        verbose_name_plural = "Umfragen"

    text = models.CharField(max_length=200)
    anz_stimmen = models.PositiveIntegerField("Stimmen pro Person", default=1)
    pub_date = models.DateTimeField('date published', default=now)
    deadline = models.DateTimeField('deadline', default=default_deadline)

    spieler_voted = models.ManyToManyField(Spieler, through="QuestionSpieler")

    def umfrage_läuft(self):
        now = timezone.now()
        return self.pub_date <= now <= self.deadline

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
