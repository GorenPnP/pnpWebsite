from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD


class Rule(models.Model):

    class Meta:
        ordering = ['nr', 'titel']
        verbose_name = "Regel"
        verbose_name_plural = "Regeln"

    nr = models.PositiveIntegerField(default=0)
    titel = models.CharField(max_length=256, unique=True, null=False)

    text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_STANDARD)
    text_rendered = RenderedMarkdownField(null=False)

    def __str__(self):
        return "{}: {}".format(self.nr, self.titel)
    
class Ghost(models.Model):

    class Meta:
        ordering = ['titel']
        verbose_name = "Geist"
        verbose_name_plural = "Geister"

    titel = models.CharField(max_length=64, unique=True)
    sch = models.CharField(max_length=64, default="", verbose_name="Schnelligkeit")
    angriff = models.CharField(max_length=64, default="", verbose_name="Angriff")
    ma = models.CharField(max_length=64, default="", verbose_name="Magie")
    wk = models.CharField(max_length=64, default="", verbose_name="Willenskraft")
    st = models.CharField(max_length=64, default="", verbose_name="Stärke")
    schaWI = models.CharField(max_length=64, default="", verbose_name="Schadenswiderstand")
    reaktion = models.CharField(max_length=64, default="", verbose_name="Reaktion")
    schaden_pro_erfolg = models.CharField(max_length=64, default="", verbose_name="Schaden / Erfolg")
    initiative = models.CharField(max_length=64, default="", verbose_name="Initiative")
    astralschaden = models.CharField(max_length=64, default="", verbose_name="Astralschaden")

    eigenschaft = models.TextField(default="")

    def __str__(self):
        return self.titel
    
class RuleTable(models.Model):

    class Meta:
        ordering = ['topic']
        verbose_name = "Regel-Tabelle"
        verbose_name_plural = "Regel-Tabellen"

    topic = models.CharField(max_length=128, unique=True)
    csv_data = models.TextField(default="")

    def __str__(self):
        return self.topic