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