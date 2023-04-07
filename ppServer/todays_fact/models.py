from datetime import date
from random import choice, choices

from django.db import models

class Fact(models.Model):
    class Meta:
        ordering = ['text']

    text = models.TextField()

    def __str__(self):
        return self.text


class History(models.Model):
    class Meta:
        pass

    date = models.DateField(default=date.today)
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, null=True)

    @classmethod
    def get_fact(self):
        if Fact.objects.count() == 0: return None

        history_obj, created = self.objects.get_or_create(date=date.today())

        if created:
            fact = Fact.objects.all()[choice(range(0, Fact.objects.count()))]
            history_obj.fact = fact
            history_obj.save(update_fields=["fact"])

        return history_obj.fact
