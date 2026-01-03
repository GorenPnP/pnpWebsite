from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

class Changelog(models.Model):
    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Changelog"
        verbose_name_plural = "Changelogs"

    timestamp = models.DateTimeField(auto_now_add=True)
    text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_STANDARD)
    text_rendered = RenderedMarkdownField(null=False)

    def __str__(self):
        return "Changelog vom {}".format(self.timestamp)