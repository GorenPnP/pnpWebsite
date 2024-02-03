from django.db import models


class Rule(models.Model):

    class Meta:
        ordering = ['nr', 'titel']
        verbose_name = "Regel"
        verbose_name_plural = "Regeln"

    nr = models.PositiveIntegerField(default=0)
    titel = models.CharField(max_length=256, unique=True, null=False)
    text = models.TextField(default="", null=False, blank=False)    # markdown-text

    def __str__(self):
        return "{}: {}".format(self.nr, self.titel)
